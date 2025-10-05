"""
Only for use within __main__.py
"""
import io

from rich.console import RenderableType
from typing_extensions import Optional
from scratchattach.cli.__about__ import VERSION
from scratchattach.cli.namespace import ArgSpace
from scratchattach.cli.context import ctx


# noinspection PyPackageRequirements
def try_get_img(image: bytes, size: tuple[int, int] | None = None) -> Optional[RenderableType]:
    try:
        from PIL import Image
        from rich_pixels import Pixels

        with Image.open(io.BytesIO(image)) as image:
            if size is not None:
                image = image.resize(size)

            return Pixels.from_image(image)

    except ImportError:
        return ""
