# i am really unsure on how this should be implemented
from __future__ import annotations
import os
from copy import deepcopy
from typing import Any, TypedDict, cast, Optional, TYPE_CHECKING
import ast
from pathlib import Path
import json

if TYPE_CHECKING:
    from _typeshed import StrPath


class CodegenConfig(TypedDict):
    sync_target_directory: str
    async_target_directory: str


class AsyncCodegenNodeTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.generic_visit(node)

        if node.name.endswith("_prim_sync"):
            return None

        return node


class SyncCodegenNodeTransformer(ast.NodeTransformer):
    def visit_Assign(self, node: ast.Assign) -> Any:
        self.generic_visit(node)

        if node.targets:
            first_target = node.targets[0]
            if isinstance(first_target, ast.Name) and first_target.id == "IS_ASYNC":
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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.generic_visit(node)

        if node.name.endswith("_prim_sync"):
            node.name = node.name.removesuffix("_sync")

        return node


def codegen_for_ast(ast: ast.AST) -> tuple[ast.AST, ast.AST]:
    ast_2 = deepcopy(ast)
    return (
        SyncCodegenNodeTransformer().generic_visit(ast),
        AsyncCodegenNodeTransformer().generic_visit(ast_2),
    )


def codegen_for_file(file: Path) -> tuple[ast.AST, ast.AST]:
    code = file.read_text()
    return codegen_for_ast(ast.parse(code))


def codegen_for_whole_directory(directory: "StrPath"):
    directory = Path(directory).resolve()
    prev_cwd = os.getcwd()
    os.chdir(directory)
    items = {path.name: path for path in directory.iterdir()}
    codegen_config: CodegenConfig
    try:
        codegen_config = cast("CodegenConfig", json.loads(items.pop(".codegen_config").read_text()))
    except KeyError:
        codegen_config = CodegenConfig(
            sync_target_directory=str(
                directory.with_stem(f"{directory.stem}_sync"),
            ),
            async_target_directory=str(
                directory.with_stem(f"{directory.stem}_async"),
            ),
        )
    sync_target_directory = Path(codegen_config["sync_target_directory"])
    async_target_directory = Path(codegen_config["async_target_directory"])
    sync_target_directory.mkdir(parents=True, exist_ok=True)
    async_target_directory.mkdir(parents=True, exist_ok=True)
    for path in items.values():
        if path.suffix.lower() != ".py":
            continue
        if not path.is_file():
            continue
        (sync_ast, async_ast) = codegen_for_file(path)
        (sync_code, async_code) = (ast.unparse(sync_ast), ast.unparse(async_ast))
        (sync_target_directory / path.name).write_text(sync_code)
        (async_target_directory / path.name).write_text(async_code)
    os.chdir(prev_cwd)


def main(): ...


if __name__ == "__main__":
    main()
