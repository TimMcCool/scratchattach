exit()
import dotenv
dotenv.load_dotenv()
import scratchattach
import os

session_string = os.getenv("SCRATCH_SESSION_STRING")
assert session_string

session = scratchattach.login_by_session_string(session_string)

cloud = session.connect_cloud(693122627)
client = cloud.requests()

@client.request(name="get")
def get(user1, user2):
    print(user1, user2, client.get_requester())
    return "hi"

client.start()