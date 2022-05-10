Scratch3.py is a modern and object oriented library for the Scratch website.
Automate actions and interact with your Scratch projects through cloud variables.

**Some functions require logging in to Scratch.**
**You also need to have the coding language Python installed on your computer.**
*Download Python here if you don't have it: https://www.python.org/downloads/*

The project is maintained by TimMcCool: https://scratch.mit.edu/users/TimMcCool/

# Installation

To install the library, run the following command in your command prompt
/ shell:
```
pip install scratch3.py
```

**OR**

Add this to your Python code:
```
import os

os.system("pip install scratch3.py")
```

# Logging in  `scratch3.Session`

**Logging in to Scratch:**

```
import scratch3

session = scratch3.login("username", "password")
```

`login()` returns a `Session` object that saves your login

Logging in directly with a sessionId (advanced):

```
import scratch3

session = scratch3.Session("sessionId")
```

# Cloud variables  `scratch3.CloudConnection`

**Connecting to the Scratch cloud server:**

With a `Session` object:

```
conn = session.connect_cloud(project_id="project_id")
```

Directly with a sessionId (advanced):

```
conn = scratch3.CloudConnection(project_id = "project_id", username="username", session_id="sessionId")
```

**Connecting to the TurboWarp cloud server:**

Does not require a session

```
conn = scratch3.TwCloudConnection(project_id = "project_id", username="username", cloud_host="<wss://clouddata.turbowarp.org")
```

**Set a cloud var:**

New Scratchers can set Scratch cloud variables too

```
conn.set_var("variable", "value") #the variable name is specified
without the cloud emoji
```

**Get a Scratch cloud var:**

Does not require a session

```
value = scratch3.get_var("project_id", "variable") #Returns value of the cloud var
variables = scratch3.get_cloud("project_id") #Returns a dict with all cloud var values
logs = scratch3.get_cloud_logs("project_id") #Returns the cloud logs as list
```

Getting a TurboWarp cloud var is not possible at the moment

# Cloud events  `scratch3.CloudEvents`

*Cloud events allow reacting to cloud events in real time. If a Scratcher
sets / creates / deletes a cloud var on the given project, an
event will be called.*

They do not require a session

**How to use:**

```
import scratch3

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

**Tip:** If you combine this with the scripts from above, you can make a bot that
auto-reacts when a cloud variable is set!

# Cloud requests  `scratch3.CloudRequests`

*Cloud requests make it possible to access data like message counts, user
stats and more from Scratch projects. They use cloud variables to
transmit data*

**Add Cloud requests to your Scratch project:**

Download this project file to your computer: https://scratch3-assets.1tim.repl.co/CloudRequests_Template.sb3

Then, go to the Scratch website, create a new project and upload the project file from above.

**How to use:**

Copy this code to your Python editor:

```
import scratch3

session = scratch3.login("username", "password") #replace with your data
conn = session.connect_cloud(project_id="project_id") #replace with your project id

client = scratch3.CloudRequests(conn, ignore_exceptions=True)

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

1)  Almost no limitations: Max. length of the returned
    data is at 3000 characters. (If the returned data is too long to fit
    into one cloud var, it will be split to multiple cloud vars)
2)  It can handle multiple requests being sent at the same time
3)  You can freely choose the names of your requests
4)  You can also return lists

**Example 1: Script that loads your message count**

Scratch code:

![image](https://scratch3-assets.1tim.repl.co/pypi_docs/example1.png/)

Python code (add this to the code from above, but make sure `client.run()` stays at the bottom of the file):

```
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

```
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
```
user = session.connect_user("username")
```

Get the user that you are logged in with:
```
session.get_linked_user()
```

You can also get users without logging in:
```
user = scratch3.get_user("username")
```

**Attributes:**
```
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
```
user.message_count()
user.featured_data() #Returns info on the user's featured project as dict

user.follower_count()
user.following_count()
user.project_count()
user.favorites_count() #Returns the amount of projects the user has favorited

user.followers(limit=40, offset=0) #Returns the followers as list of scratch3.User objects
user.following(limit=40, offset=0) #Returns the people the user is following as list of scratch3.User objects
user.projects(limit=None, offset=0) #Returns the projects the user has shared as list of scratch3.Project objects
user.favorites(limit=None, offset=0) #Returns the projects the user has favorited as list of scratch3.Project objects

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

user.stats() #Returns the user's statistics as dict. Fetched from
ScratchDB user.ranks() #Returns the user's ranks as dict. Fetched from ScratchDB
```

# Projects  `scratch3.Project`

**Get a project:**
```
project = session.connect_project("project_id")
```

You can also get projects without logging in:
```
project = scratch3.get_project("project_id")
```

**Attributes:**
```
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
project.favorite s #Returns the project's favorite count
project.remix_count  #Returns the number of remixes
project.views  #Returns the view count
# ----- ----- #
project.update()  #Updates the above data
```

**Functions:**
```
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

**Most functions don't work for such projects. However, these still work:**
```
project.remixes(limit=None, offset=0)

project.download(filename="project_name.sb3", dir="/")
project.get_raw_json()
project.get_creator_agent()
```

# Search / Explore page

Doesn't require a session

**Search:**
```
session.search_projects(query="query", mode="trending", language="en", limit=40, offset=0)
scratch3.search_projects(query="query", mode="trending", language="en", limit=40, offset=0) #Doesn't require logging in

scratch3.search_studios(query="query", mode="trending", language="en", limit=40, offset=0)

scratch3.search_comments(query="query") #This will return matching profile comments from all across Scratch. It is based on ScratchData
```

**Get the explore page:**
```
session.explore_projects(query="*", mode="trending", language="en", limit=40, offset=0)
scratch3.explore_projects(query="*", mode="trending", language="en", limit=40, offset=0) #Doesn't require logging in

scratch3.explore_studios(query="*", mode="trending", language="en", limit=40, offset=0)
```

# Messages / My stuff page

**Functions:**
```
session.get_mystuff_projects("all", page=1, sort_by="") #Returns the projects from your "My stuff" page as list

session.messages(limit=40, offset=0) #Returns your messages as dict
session.clear_messages() #Marks your messages as read
session.get_message_count() #Returns your message count
```

# "What's happening" section / Your feed

**Functions:**
```
session.get_feed(limit=20, offset=0) #Returns your "What's happening" section from the Scratch front page as list
session.loved_by_followed_users(limit=40, offset=0) #Returns the projects loved by users you are following as list
```

# Featured projects / News

Doesn't require a session

```
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
