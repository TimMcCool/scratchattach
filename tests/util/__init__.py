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

_teacher_session: Optional[_Session] = None
def teacher_session() -> _Session:
    global _teacher_session

    if not _teacher_session:
        if "teacher_auth" not in __AUTH:
            warnings.warn(f"Could not test for teacher session")
            exit(0)

        data = __AUTH["teacher_auth"]
        _teacher_session = login(data["username"], data["password"])

    return _teacher_session
