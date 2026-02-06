# utility methods for testing
# includes special handlers for authentication etc.
import warnings

from typing import Optional
from datetime import datetime

from .keyhandler import get_auth
from scratchattach import login, Session as _Session, LoginDataWarning

warnings.filterwarnings('ignore', category=LoginDataWarning)

_session: Optional[_Session] = None

def credentials_available() -> bool:
    auth = get_auth()
    if not auth:
        return False
    return auth.get("auth") is not None

def session() -> _Session:
    global _session

    if not _session:
        auth = get_auth().get("auth")
        scratchattachv2 = None if auth is None else auth.get("scratchattachv2")
        if scratchattachv2 is None:
            raise RuntimeError("Not enough data for login.")
        _session = login("ScratchAttachV2", scratchattachv2)

    return _session

_teacher_session: Optional[_Session] = None
def teacher_session() -> Optional[_Session]:
    global _teacher_session

    if not _teacher_session:
        if "teacher_auth" not in get_auth():
            warnings.warn(f"Could not test for teacher session")
            return None

        data = get_auth()["teacher_auth"]
        _teacher_session = login(data["username"], data["password"])

    return _teacher_session

def allow_before(d: datetime) -> bool:
    return datetime.now() < d

