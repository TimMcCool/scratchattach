from __future__ import annotations

from . import base, block, sprite


class Comment(base.IDComponent):
    def __init__(self, _id: str = None, _block: block.Block = None, x: int = 0, y: int = 0, width: int = 100,
                 height: int = 100,
                 text: str = '', *, _sprite: sprite.Sprite = None):
        self.block = _block

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.text = text

        super().__init__(_id, _sprite)

    def __repr__(self):
        return f"Comment<{self.text[:10]!r}>"

    @staticmethod
    def from_json(data: tuple[str, dict]):
        assert len(data) == 2
        _id, data = data

        _block_id = data.get("blockId")
        if _block_id is not None:
            _block = block.Block(_block_id)
        else:
            _block = None

        x = data.get("x", 0)
        y = data.get("y", 0)

        width = data.get("width", 100)
        height = data.get("height", 100)

        text = data.get("text")

        ret = Comment(_id, _block, x, y, width, height, text)
        if _block is not None:
            _block.comment = ret
        return ret

    def to_json(self) -> dict:
        pass
