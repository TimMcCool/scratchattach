from __future__ import annotations
import re
import argparse
import contextlib
import os
from copy import deepcopy
from typing import Any, TypedDict, cast, Optional, TYPE_CHECKING, Sequence
import ast
from pathlib import Path
import json
import subprocess
import libcst

if TYPE_CHECKING:
    from _typeshed import StrPath


PRE_CODEGEN_NAME = "IS_PRE_CODEGEN"
STATICALLY_ASYNC_NAME = "IS_ASYNC"
DYNAMICALLY_ASYNC_NAME = "IS_ASYNC"

COMMENT_IDENTIFIER = "COMMENT"
PREVIOUS_LINE_COMMENT_IDENTIFIER = "PREV_LINE_COMMENT"


class CodegenConfig(TypedDict):
    sync_target_directory: str
    async_target_directory: str
    exclude: list[str]
    include_directories: list[str]


class AsyncCodegenNodeTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.generic_visit(node)

        if node.name.endswith("_prim_sync"):
            return None

        return node

    def _is_statically_async_literal(self, node: ast.AST) -> bool:
        return isinstance(node, ast.Constant) and node.value == STATICALLY_ASYNC_NAME

    def _is_pre_codegen_literal(self, node: ast.AST) -> bool:
        return isinstance(node, ast.Constant) and node.value == PRE_CODEGEN_NAME

    def _match_static_condition(self, test: ast.AST) -> bool | None:
        if self._is_statically_async_literal(test):
            return True

        if self._is_pre_codegen_literal(test):
            return False

        if (
            isinstance(test, ast.UnaryOp)
            and isinstance(test.op, ast.Not)
            and self._is_statically_async_literal(test.operand)
        ):
            return False

        if (
            isinstance(test, ast.UnaryOp)
            and isinstance(test.op, ast.Not)
            and self._is_pre_codegen_literal(test.operand)
        ):
            return True

        return None

    def visit_If(self, node: ast.If) -> Any:
        self.generic_visit(node)

        if (condition_value := self._match_static_condition(node.test)) is not None:
            return node.body if condition_value else node.orelse

        return node


class SyncCodegenNodeTransformer(ast.NodeTransformer):
    def visit_Assign(self, node: ast.Assign) -> Any:
        self.generic_visit(node)

        if node.targets:
            first_target = node.targets[0]
            if isinstance(first_target, ast.Name) and first_target.id == DYNAMICALLY_ASYNC_NAME:
                node.value = ast.Constant(value=False, kind=None)

        return node

    def visit_Await(self, node: ast.Await) -> Any:
        self.generic_visit(node)
        return node.value

    def visit_AsyncFor(self, node: ast.AsyncFor) -> Any:
        self.generic_visit(node)
        new_node = ast.For(**{field: getattr(node, field) for field in node._fields})
        return ast.copy_location(new_node, node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> Any:
        self.generic_visit(node)
        new_node = ast.With(**{field: getattr(node, field) for field in node._fields})
        return ast.copy_location(new_node, node)

    def visit_comprehension(self, node: ast.comprehension) -> Any:
        self.generic_visit(node)
        node.is_async = 0
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self.generic_visit(node)

        # primitive functions are implemented as sync and as async so the async variant can be dropped
        if node.name.endswith("_prim"):
            return None

        new_node = ast.FunctionDef(**{field: getattr(node, field) for field in node._fields})

        return ast.copy_location(new_node, node)

    def _is_statically_async_literal(self, node: ast.AST) -> bool:
        return isinstance(node, ast.Constant) and node.value == STATICALLY_ASYNC_NAME

    def _is_pre_codegen_literal(self, node: ast.AST) -> bool:
        return isinstance(node, ast.Constant) and node.value == PRE_CODEGEN_NAME

    def _match_static_condition(self, test: ast.AST) -> bool | None:
        if self._is_statically_async_literal(test):
            return False

        if self._is_pre_codegen_literal(test):
            return False

        if (
            isinstance(test, ast.UnaryOp)
            and isinstance(test.op, ast.Not)
            and self._is_statically_async_literal(test.operand)
        ):
            return True

        if (
            isinstance(test, ast.UnaryOp)
            and isinstance(test.op, ast.Not)
            and self._is_pre_codegen_literal(test.operand)
        ):
            return True

        return None

    def visit_If(self, node: ast.If) -> Any:
        self.generic_visit(node)

        if (condition_value := self._match_static_condition(node.test)) is not None:
            return node.body if condition_value else node.orelse

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.generic_visit(node)

        if node.name.endswith("_prim_sync"):
            node.name = node.name.removesuffix("_sync")

        return node


class CommentTransformer(libcst.CSTTransformer):
    @staticmethod
    def _get_comment(node: libcst.CSTNode, target_name: str) -> str | None:
        if isinstance(node, libcst.SimpleStatementLine) and len(node.body) == 1:
            expr = node.body[0]
            if (
                isinstance(expr, libcst.Expr)
                and isinstance((call := expr.value), libcst.Call)
                and isinstance((func := call.func), libcst.Name)
                and func.value == target_name
                and len(call.args) == 1
                and isinstance((comment_value := call.args[0].value), libcst.SimpleString)
            ):
                comment_value_string = comment_value.evaluated_value
                if isinstance(comment_value_string, bytes):
                    return comment_value_string.decode()
                return comment_value_string
        return None

    @classmethod
    def _process_statement_sequence(
        cls, sequence: Sequence[libcst.BaseStatement]
    ) -> tuple[list[libcst.BaseStatement], list[libcst.EmptyLine], libcst.Comment | None]:
        new_body: list[libcst.BaseStatement] = []
        pending_comments: list[libcst.EmptyLine] = []
        header_comment: libcst.Comment | None = None
        for statement in sequence:
            prev_line_comment_text = cls._get_comment(statement, PREVIOUS_LINE_COMMENT_IDENTIFIER)
            if prev_line_comment_text is not None:
                comment = libcst.Comment(f"# {prev_line_comment_text}")
                if new_body:
                    prev_statement = new_body[-1]
                    if isinstance(prev_statement, libcst.SimpleStatementLine):
                        whitespace = libcst.TrailingWhitespace(
                            whitespace=libcst.SimpleWhitespace(" "), comment=comment
                        )
                        new_body[-1] = prev_statement.with_changes(trailing_whitespace=whitespace)
                    else:
                        pending_comments.append(libcst.EmptyLine(indent=True, comment=comment))
                elif header_comment is None:
                    header_comment = comment
                else:
                    pending_comments.append(libcst.EmptyLine(indent=True, comment=comment))
                continue
            comment_text = cls._get_comment(statement, COMMENT_IDENTIFIER)
            if comment_text is not None:
                pending_comments.append(
                    libcst.EmptyLine(indent=True, comment=libcst.Comment(f"# {comment_text}"))
                )
                continue
            if (
                pending_comments
                and (leading_lines := getattr(statement, "leading_lines", None)) is not None
            ):
                statement = statement.with_changes(
                    leading_lines=(*leading_lines, *pending_comments)
                )
                pending_comments = []
            new_body.append(statement)
        return (new_body, pending_comments, header_comment)

    def leave_Module(
        self, original_node: libcst.Module, updated_node: libcst.Module
    ) -> libcst.Module:
        new_body, pending_comments, header_comment = self._process_statement_sequence(
            updated_node.body
        )
        if header_comment is not None:
            pending_comments.insert(0, libcst.EmptyLine(indent=True, comment=header_comment))
        new_footer = (*updated_node.footer, *pending_comments)
        return updated_node.with_changes(body=new_body, footer=new_footer)

    def leave_IndentedBlock(
        self, original_node: libcst.IndentedBlock, updated_node: libcst.IndentedBlock
    ) -> libcst.IndentedBlock:
        new_body, pending_comments, header_comment = self._process_statement_sequence(
            updated_node.body
        )
        new_footer = (*updated_node.footer, *pending_comments)
        if not new_body:
            new_body = [libcst.SimpleStatementLine([libcst.Pass()])]

        changes: dict[str, Any] = {"body": new_body, "footer": new_footer}

        if header_comment:
            changes["header"] = libcst.TrailingWhitespace(
                whitespace=libcst.SimpleWhitespace(" "), comment=header_comment
            )

        return updated_node.with_changes(**changes)


def codegen_for_ast(ast: ast.AST) -> tuple[ast.AST, ast.AST]:
    ast_2 = deepcopy(ast)
    return (
        SyncCodegenNodeTransformer().generic_visit(ast),
        AsyncCodegenNodeTransformer().generic_visit(ast_2),
    )


def add_comments(code: str) -> str:
    cst = libcst.parse_module(code)
    transformer = CommentTransformer()
    return cst.visit(transformer).code


def codegen_for_file(file: Path) -> tuple[ast.AST, ast.AST]:
    code = file.read_text()
    return codegen_for_ast(ast.parse(code))


def codegen_for_whole_directory(directory: "StrPath"):
    directory = Path(directory).resolve()
    items = {path.name: path for path in directory.iterdir()}
    codegen_config: CodegenConfig
    try:
        codegen_config = cast(
            "CodegenConfig", json.loads(items.pop("codegen_config.json").read_text())
        )
    except KeyError:
        codegen_config = CodegenConfig(
            sync_target_directory=str(
                directory.with_stem(f"{directory.stem}_sync"),
            ),
            async_target_directory=str(
                directory.with_stem(f"{directory.stem}_async"),
            ),
            exclude=[],
            include_directories=[],
        )
    sync_target_directory = directory / codegen_config["sync_target_directory"]
    async_target_directory = directory / codegen_config["async_target_directory"]
    sync_target_directory.mkdir(parents=True, exist_ok=True)
    async_target_directory.mkdir(parents=True, exist_ok=True)
    exclusions = {(directory / exclusion).resolve() for exclusion in codegen_config["exclude"]}
    for path in items.values():
        path = path.resolve()
        if path.suffix.lower() != ".py":
            continue
        if not path.is_file():
            continue
        if path in exclusions:
            continue
        (sync_ast, async_ast) = codegen_for_file(path)
        (sync_code, async_code) = (
            add_comments(ast.unparse(sync_ast)),
            add_comments(ast.unparse(async_ast)),
        )
        (sync_target_directory / path.name).write_text(sync_code)
        (async_target_directory / path.name).write_text(async_code)
    subprocess.run(
        [
            "python",
            "-m",
            "ruff",
            "format",
            str(sync_target_directory.resolve()),
            str(async_target_directory.resolve()),
        ],
        capture_output=True,
        text=True,
    )
    for included_dir in codegen_config["include_directories"]:
        codegen_for_whole_directory(directory / included_dir)


class CodegenArgumentNamespace(argparse.Namespace):
    targets: list[Path]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("targets", nargs="*", type=Path)
    parsed = parser.parse_args(namespace=CodegenArgumentNamespace())
    for target in parsed.targets:
        codegen_for_whole_directory(target)


if __name__ == "__main__":
    main()
