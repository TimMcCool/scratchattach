import dotenv
dotenv.load_dotenv()
import os
import sys
sys.path.insert(0, os.path.join(__file__, "..", ".."))
import scratchattach

session_string = os.getenv("SCRATCH_SESSION_STRING")
assert session_string

session = scratchattach.login_by_session_string(session_string)


input()
