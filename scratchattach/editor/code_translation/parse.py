from __future__ import annotations
from pathlib import Path
from typing import Union, Generic, TypeVar
from abc import ABC, abstractmethod
from collections.abc import Sequence

from lark import Lark, Transformer, Tree, Token, v_args
from lark.reconstruct import Reconstructor

R = TypeVar("R")
class SupportsRead(ABC, Generic[R]):
    @abstractmethod
    def read(self, size: int | None = -1) -> R:
        pass

LANG_PATH = Path(__file__).parent / "language.lark"

lang = Lark(LANG_PATH.read_text(), maybe_placeholders=False)
reconstructor = Reconstructor(lang)

def parse(script: Union[str, bytes, SupportsRead[str], Path]) -> Tree:
    if isinstance(script, Path):
        script = script.read_text()
    if isinstance(script, SupportsRead):
        read_data = script.read()
        assert isinstance(read_data, str)
        script = read_data
    if isinstance(script, bytes):
        script = script.decode("utf-8")
    return lang.parse(script)

def unparse(tree: Tree) -> str:
    return reconstructor.reconstruct(tree)

class PrettyUnparser(Transformer):
    INDENT_STRING = "    "

    @classmethod
    def _indent(cls, text):
        if not text:
            return ""
        return "\n".join(cls.INDENT_STRING + line for line in text.splitlines())

    def PARAM_NAME(self, token):
        return token.value

    def BLOCK_NAME(self, token):
        return token.value

    def EVENT(self, token):
        return token.value

    def CONTROL_BLOCK_NAME(self, token):
        return token.value
        
    def _PREPROC_INSTR_CONTENT(self, token):
        return token.value
        
    def _COMMMENT_CONTENT(self, token):
        return token.value
    
    @v_args(inline=True)
    def hat(self, child):
        return child

    @v_args(inline=True)
    def param(self, child):
        return child

    @v_args(inline=True)
    def value_param(self, name):
        return name

    @v_args(inline=True)
    def bool_param(self, name):
        return f"<{name}>"

    @v_args(inline=True)
    def event_hat(self, event_name):
        return f"when ({event_name})"

    def block_hat(self, items):
        name, *params = items
        params_str = ", ".join(params)
        return f"custom_block {name} ({params_str})"

    @v_args(inline=True)
    def PREPROC_INSTR(self, content):
        return f"{content}"
    
    @v_args(inline=True)
    def COMMMENT(self, content):
        return f"{content}"
    
    def block(self, items):
        params = []
        inner_blocks = []
        for i in items[1:]:
            if not isinstance(i, Tree):
                continue
            if str(i.data) == "block_content":
                inner_blocks.extend(i.children)
            if str(i.data) == "block_params":
                params.extend(i.children)
        block_name = items[0]
        block_text = f"{block_name}({', '.join(params)})" if params or not inner_blocks else f"{block_name}"
        if len(inner_blocks) > 0:
            blocks_content = "\n".join(inner_blocks)
            indented_content = self._indent(blocks_content)
            block_text += f" {{\n{indented_content}\n}}"
        return block_text
    
    def LITERAL_NUMBER(self, number: str):
        return number
    
    @v_args(inline=True)
    def expr(self, item):
        return item
    
    @v_args(inline=True)
    def low_expr1(self, item):
        if " " in item:
            return f"({item})"
        return item
    
    @v_args(inline=True)
    def low_expr2(self, item):
        return item
    
    def addition(self, items):
        return items[0] + " + " + items[1]
    
    def subtraction(self, items):
        return items[0] + " - " + items[1]

    def multiplication(self, items):
        return items[0] + " * " + items[1]
    
    def division(self, items):
        return items[0] + " / " + items[1]
    
    def top_level_block(self, items):
        first_item = items[0]
        if first_item.startswith("%%") or first_item.startswith("##"):
            return first_item

        hat, *blocks = items
        blocks_content = "\n".join(blocks)
        indented_content = self._indent(blocks_content)
        return f"{hat} {{\n{indented_content}\n}}"
    
    def start(self, items):
        return "\n\n".join(items)

def pretty_unparse(tree: Tree):
    return PrettyUnparser().transform(tree)

if __name__ == "__main__":
    EXAMPLE_FILE = Path(__file__).parent / "example.txt"
    tree = parse(EXAMPLE_FILE)
    print(tree.pretty())
    print()
    print()
    print(tree)
    print()
    print()
    print(unparse(tree))
    print()
    print()
    print(pretty_unparse(tree))