# utility methods for testing
# includes special handlers for authentication etc.
import warnings

from typing import Optional

from .keyhandler import AUTH as __AUTH
from scratchattach import login, Session as _Session, LoginDataWarning

warnings.filterwarnings('ignore', category=LoginDataWarning)

_session: Optional[_Session] = None


def session() -> _Session:
    global _session

    if not _session:
        _session = login("ScratchAttachV2", __AUTH["auth"]["scratchattachv2"])

    return _session
