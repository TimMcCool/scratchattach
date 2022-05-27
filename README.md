Scratchattach is a modern and object oriented library for the Scratch website.
Automate actions and interact with your Scratch projects through cloud variables.

**Some functions require logging in to Scratch.**
**You also need to have the coding language Python installed on your computer.**
*Download Python here if you don't have it: https://www.python.org/downloads/*

The project is maintained by TimMcCool: https://scratch.mit.edu/users/TimMcCool/

# Installation

To install the library, run the following command in your command prompt
/ shell:
```
pip install scratchattach
```

**OR**

Add this to your Python code:
```python
import os

os.system("pip install scratchattach")
```

# Logging in  `scratch3.Session`

**Logging in with username / password:**

```python
import scratchattach as scratch3

session = scratch3.login("username", "password")
```

`login()` returns a `Session` object that saves your login

**Logging in with a sessionId:**

```python
import scratchattach as scratch3

session = scratch3.Session("sessionId")
```

**Attributes:**
```py
session.session_id #Returns the associated session id
session.xtoken
session.email #Returns the email adress associated with the account
session.new_scratcher #Returns True if the associated account is a New Scratcher
session.mute_status
session.banned #Returns True if the associated account is banned
```

# Cloud variables  `scratch3.CloudConnection` `scratch3.TwCloudConnection`

**Connect to the Scratch cloud:**

With a `Session` object:

```python
conn = session.connect_cloud(project_id="project_id")
```

Directly with a sessionId (cookie connect):

```python
conn = scratch3.CloudConnection(project_id = "project_id", username="username", session_id="sessionId")
```

**Connect to the TurboWarp cloud:**

Does not require a session.

```python
conn = scratch3.TwCloudConnection(project_id = "project_id", username="username", cloud_host="<wss://clouddata.turbowarp.org")
```

**Set a cloud var:**

New Scratchers can set Scratch cloud variables too.

```python
conn.set_var("variable", "value") #the variable name is specified
without the cloud emoji
```

**Get a Scratch cloud var from the clouddata logs:**

Does not require a connection / session.

```python
value = scratch3.get_var("project_id", "variable")
variables = scratch3.get_cloud("project_id") #Returns a dict with all cloud var values
logs = scratch3.get_cloud_logs("project_id") #Returns the cloud logs as list
```

**Get a TurboWarp cloud var from the websocket:** (new in v0.4.7)

Requires a connection to TurboWarp's cloud (a `TwCloudConnection` object).

```python
value = conn.get_var("variable")
```

# Encoding / Decoding  `scratch3.Encoding`

To send text to your Scratch project, you can use the built in encoder.
To decode sent texts in Scratch, download this sprite and add it to your Scratch project: https://scratch3-assets.1tim.repl.co/Encoder.sprite3

```python
from scratchattach import Encoding

Encoding.encode("input") #will return the encoded text
Encoding.decode("encoded") #will decode an encoded text
```

# Cloud events  `scratch3.CloudEvents` `scratch3.TwCloudEvents`

*Cloud events allow reacting to cloud events in real time. If a Scratcher
sets / creates / deletes a cloud var on the given project, an
event will be called.*

They do not require a session.

**How to use with Scratch:**

```python
import scratchattach as scratch3

events = scratch3.CloudEvents("project_id")

@events.event
def on_set(event): #Called when a cloud var is set
    print(f"{event.user} set the variable {event.var} to the valuee {event.value} at {event.timestamp}")

@events.event
def on_del(event):
    print(f"{event.user} deleted variable {event.var}")

@events.event
def on_create(event):
    print(f"{event.user} created variable {event.var}")

@events.event #Called when the event listener is ready
def on_ready():
   print("Event listener ready!")

events.start() #Make sure this is ALWAYS at the bottom of your Python file!
```

**How to use with TurboWarp:** (new in v0.4.7)

```python
import scratchattach as scratch3

events = scratch3.TwCloudEvents("project_id")

...
```

# Cloud requests  `scratch3.CloudRequests`

*Cloud requests make it possible to access data like message counts, user
stats and more from Scratch projects. They use cloud variables to
transmit data*

**Add Cloud requests to your Scratch project:**

Download this project file to your computer: https://scratch3-assets.1tim.repl.co/CloudRequests_Template.sb3

Then, go to the Scratch website, create a new project and upload the project file from above.

**How to use:**

Copy this code to your Python editor:

```python
import scratchattach as scratch3

session = scratch3.login("username", "password") #replace with your data
conn = session.connect_cloud(project_id="project_id") #replace with your project id

client = scratch3.CloudRequests(conn) #optional argument: ignore_exceptions=True

@client.request
def ping(): #called when client receives request
    print("Ping request received")
    return "pong" #sends back 'pong' to the Scratch project

@client.event
def on_ready():
    print("Request handler is ready")

client.run()  #Make sure this is ALWAYS at the bottom of your Python file!
```

In the `Cloud Requests` sprite, you will find this block:

![image](https://scratch3-assets.1tim.repl.co/pypi_docs/tutorial.png/)

When active, it will send a "ping" request to the Python client. This will call the `ping()` function. The data returned by the function will be sent back to the project.

![image](https://scratch3-assets.1tim.repl.co/pypi_docs/tutorial_result.png/)

**Notes:**

1)  **No length limitation** for the returned data! (If the response is too long to fit into one cloud var, it will be split to multiple cloud vars)
2)  It can handle multiple requests being sent at the same time
3)  You can freely choose the names of your requests
4)  You can also return lists

**Example 1: Script that loads your message count**

Scratch code:

![image](https://scratch3-assets.1tim.repl.co/pypi_docs/example1.png/)

Python code (add this to the code from above, but make sure `client.run()` stays at the bottom of the file):

```python
@client.request
def message_count(argument1):
    print(f"Message count requested for user {argument1}")
    user = scratch3.get_user(argument1)
    return user.message_count()
```

**Example 2: Script that loads someone's stats**

Scratch code:

![image](https://scratch3-assets.1tim.repl.co/pypi_docs/example3.png/)

Python code:

```python
@client.request
def foo(argument1):
    print(f"Data requested for user {argument1}")
    user = scratch3.get_user(argument1)
    stats = user.stats()

    return_data = []
    return_data.append(f"Total loves: {stats['loves']}")
    return_data.append(f"Total favorites: {stats['favorites']}")
    return_data.append(f"Total views: {stats['views']}")

    return return_data
```

**Make sure to credit @TimMcCool on Scratch if you use the Scratch sprite!**
**Uncredited use will automatically be reported to the Scratch Team.**

# Users  `scratch3.User`

**Get a user:**
```python
user = session.connect_user("username")
```

Get the user that you are logged in with:
```python
session.get_linked_user()
```

You can also get users without logging in:
```python
user = scratch3.get_user("username")
```

**Attributes:**
```python
user.join_date
user.about_me
user.wiwo #Returns the user's 'What I'm working on' section
user.country #Returns the country from the user profile
user.icon_url #Returns the link to the user's pfp (90x90)
user.id #Returns the id of the user
user.scratchteam #Retuns True if the user is in the Scratch team
# ----- ----- #
user.update() #Updates the above data
```

**Functions:**
```python
user.message_count()
user.featured_data() #Returns info on the user's featured project as dict

user.follower_count()
user.following_count()
user.project_count()
user.favorites_count() #Returns the amount of projects the user has favorited
user.studio_count() #Returns the amount of studios the user is curating
user.studio_following_count()

user.followers(limit=40, offset=0) #Returns the followers as list of scratch3.User objects
user.following(limit=40, offset=0) #Returns the people the user is following as list of scratch3.User objects
user.projects(limit=None, offset=0) #Returns the projects the user has shared as list of scratch3.Project objects
user.favorites(limit=None, offset=0) #Returns the projects the user has favorited as list of scratch3.Project objects
user.studios(limit=None, offset=0) #Returns the studios the user is curating as list of dicts

user.viewed_projects(limit=24, offset=0) #To use this you need to be logged in as the user. Returns the projects the user has recently viewed as list of scratch3.Project objects

user.follow()
user.unfollow()
user.is_following("scratcher") #Returns True if user is following the specified Scratcher
user.is_followed_by("scratcher") #Returns True if user is followed by the specified Scratcher

user.comments(limit=20, page=1) #Returns the user's profile comments
user.post_comment("comment content", parent_id="", commentee_id="") #Posts a comment on the user's profile. Requires logging in. Returns the info of the posted commented.
user.reply_comment("comment content", parent_id="parent_id") #Replies to a specified profile comment. Requires logging in. Returns the info of the posted commented.
user.delete_comment(comment_id="comment_id")
user.report_comment(comment_id="comment_id")

user.toggle_commenting()
user.set_bio(text) #Changes the 'About me' of the user
user.set_wiwo(text)

user.stats() #Returns the user's statistics as dict. Fetched from ScratchDB
user.ranks() #Returns the user's ranks as dict. Fetched from ScratchDB
user.followers_over_time(segment=1, range=30) #Fetched from ScratchDB
```

# Projects  `scratch3.Project`

**Get a project:**
```python
project = session.connect_project("project_id")
```

You can also get projects without logging in:
```python
project = scratch3.get_project("project_id")
```

**Attributes:**
```python
project.id  #Returns the project id
project.url  #Returns the project url
project.author  #Returns the username of the author
project.comments_allowed  #Returns True if comments are enabled
project.instructions
project.notes  #Returns the 'Notes and Credits' section
project.created  #Returns the date of the project creation
project.last_modified  #Returns the date when the project was modified the last time
project.share_date
project.thumbnail_url
project.remix_parent
project.remix_root
project.loves  #Returns the love count
project.favorites #Returns the project's favorite count
project.remix_count  #Returns the number of remixes
project.views  #Returns the view count
project.project_token
# ----- ----- #
project.update()  #Updates the above data
```

**Functions:**
```python
project.get_author()  #Returns the author as scratch3.User object
project.ranks()  #Returns the project's ranks. Fetched from ScratchDB

project.comments(limit=40, offset=0)  #Fetches all project comments except for comment replies
project.get_comment_replies(comment_id="comment_id", limit=40, offset=0)  #Fetches the replies to a specific comment
project.post_comment(content="comment content", parent_id="", commentee_id="")  #Returns the info of the posted commented.
project.reply_comment(content="comment content", parent_id="parent_id")  #Returns the info of the posted commented.
project.delete_comment(comment_id="comment_id")
project.report_comment(comment_id="comment_id")

project.love()
project.unlove()
project.favorite()
project.unfavorite()
project.post_view()

project.set_title("new title")
project.set_instructions("new instructions")
project.set_notes("new notes and credits")  #Sets the notes and credits section of the project
project.set_thumbnail("filename") #File must be .png and fit Scratch's thumbnail guidelines project.share() project.unshare()

project.turn_off_commenting()
project.turn_on_commenting()
project.toggle_commenting()

project.remixes(limit=None, offset=0) #Returns the remixes as list of scratch3.Project
project.studios(limit=None, offset=0) #Returns the studios the project is in as list of dicts

project.download(filename="project_name.sb3", dir="") #Downloads the project to your computer. The downloaded file will only work in the online editor.
project.get_raw_json() #Returns the json of the project content as dict
project.get_creator_agent() #Returns the user-agent of the user who created the project (with information about their browser and OS)
```

# Unshared projects  `scratch3.PartialProject`

When connecting / getting a project that you can't access, a `PartialProject` object is returned instead.

**Most attributes and most functions don't work for such projects. However, these still work:**
```python
project.remixes(limit=None, offset=0)

project.download(filename="project_name.sb3", dir="/")
project.get_raw_json()
project.get_creator_agent()
```

# Studios  `scratch3.Studio`
(New in v0.5.0)

**Get a studio:**
```python
studio = session.connect_studio("studio_id")
```
You can also get studios without logging in:
```python
studio = scratch3.get_studio("studio_id")
```

**Attributes:**
```python
studio.id
studio.title
studio.description
studio.host_id #The user id of the studio host
studio.open_to_all #Whether everyone is allowed to add projects
studio.comments_allowed
studio.image_url
studio.created
studio.modified
studio.follower_count
studio.manager_count
studio.project_count
# ----- ----- #
project.update()  #Updates the above data
```

**Functions:**
```python
studio.follow()
studio.unfollow()

studio.comments(limit=40, offset=0)  #Fetches all project comments except for comment replies
studio.get_comment_replies(comment_id="comment_id", limit=40, offset=0)  #Fetches the replies to a specific comment
studio.post_comment(content="comment content", parent_id="", commentee_id="")  #Returns the info of the posted commented.
studio.reply_comment(content="comment content", parent_id="parent_id")  #Returns the info of the posted commented.

studio.add_project("project_id")
studio.remove_project("project_id")

studio.invite_curator("username")
studio.promote_curator("username")
studio.remove_curator("username")

studio.projects(limit=40, offset=0)
studio.curators(limit=24, offset=0) #Returns the curators as list of users (scratch3.User)
studio.managers(limit=24, offset=0)
studio.activity(limit=24, offset=0)
```

# Search / Explore page

Doesn't require a session

**Search:**
```python
session.search_projects(query="query", mode="trending", language="en", limit=40, offset=0)
scratch3.search_projects(query="query", mode="trending", language="en", limit=40, offset=0) #Doesn't require logging in

scratch3.search_studios(query="query", mode="trending", language="en", limit=40, offset=0)

scratch3.search_comments(query="query") #This will return matching profile comments from all across Scratch. It is based on ScratchData
```

**Get the explore page:**
```python
session.explore_projects(query="*", mode="trending", language="en", limit=40, offset=0)
scratch3.explore_projects(query="*", mode="trending", language="en", limit=40, offset=0) #Doesn't require logging in

scratch3.explore_studios(query="*", mode="trending", language="en", limit=40, offset=0)
```

# Messages / My stuff page / Backpack

**Functions:**
```python
session.get_mystuff_projects("all", page=1, sort_by="") #Returns the projects from your "My stuff" page as list

session.messages(limit=40, offset=0) #Returns your messages as dict
session.clear_messages() #Marks your messages as read
session.get_message_count() #Returns your message count
```

# "What's happening" section

**Functions:**
```python
session.get_feed(limit=20, offset=0) #Returns your "What's happening" section from the Scratch front page as list
session.loved_by_followed_users(limit=40, offset=0) #Returns the projects loved by users you are following as list
```

# Backpack

**Functions:**
```python
session.backpack(limit=20, offset=0) #Returns the contents of your backpack as dictionary
session.delete_from_backpack("asset id") #Deletes an asset from your backpack
```

# Featured projects / News

Doesn't require a session

```python
scratch3.get_news(limit=10, offset=0) #Returns the news from the Scratch front page as list
scratch3.featured_projects() #Returns the featured projects from the Scratch homepage as list
scratch3.featured_studios()
scratch3.top_loved()
scratch3.top_remixed()
scratch3.newest_projects() #Returns a list with the newest Scratch projects. This list is not present on the Scratch home page, but the API still provides it.
scratch3.design_studio_projects()
```

# Contributors

-   Almost all code by TimMcCool
    (https://scratch.mit.edu/users/TimMcCool/)
-   Siddhesh (creator of scratchconnect) for some help and the profile
    comments API
-   DatOneLefty for ScratchDB which is used to fetch stats and ranks
-   Lynx for ScratchData (https://sd.sly-little-fox.ru/api/v1/search?q=)

Source code available on GitHub

# Support

If you need help with your code, leave a comment on TimMcCool's Scratch
profile: https://scratch.mit.edu/users/TimMcCool/
