Scratch API wrapper with support for almost all site features

This library can set cloud variables, follow Scratchers, post comments and do so much more! It has special features that make it easy to transmit data through cloud variables.

**Some functions require logging in to Scratch.**
**You also need to have the coding language Python installed on your device.**
*Download Python here if you don't have it: https://www.python.org/downloads/*

The project is maintained by TimMcCool: https://scratch.mit.edu/users/TimMcCool/

[![PyPI status](https://img.shields.io/pypi/status/scratchattach.svg)](https://pypi.python.org/pypi/scratchattach/)
[![PyPI download month](https://img.shields.io/pypi/dm/scratchattach.svg)](https://pypi.python.org/pypi/scratchattach/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/scratchattach.svg)](https://pypi.python.org/pypi/scratchattach/)
[![GitHub license](https://badgen.net/github/license/TimMcCool/scratchattach)](https://github.com/TimMcCool/scratchattach/blob/master/LICENSE)

# Installation

Run the following command in your command prompt
/ shell:
```
pip install -U scratchattach
```

**OR**

Add this to your Python code:
```python
import os

os.system("pip install -U scratchattach")
```

# Logging in  `scratch3.Session`

**Logging in with username / password:**

```python
import scratchattach as scratch3

session = scratch3.login("username", "password")
```

`login()` returns a `Session` object that saves your login

**Logging in with a sessionId:**
*You can get your session id from your browser's cookies. [More information](https://github.com/TimMcCool/scratchattach/wiki/Get-your-session-id)*

```python
import scratchattach as scratch3

session = scratch3.Session("sessionId", username="username")
```

**Attributes:**
```py
session.session_id #Returns the associated session id
session.xtoken
session.email #Returns the email address associated with the account
session.new_scratcher #Returns True if the associated account is a New Scratcher
session.mute_status
session.banned #Returns True if the associated account is banned
```

# Cloud variables  `scratch3.CloudConnection`
*Make sure you're using the latest scratchattach version. Update scratchattach with `pip install scratchattach --upgrade`*

**Connect to the Scratch cloud:**

With a `Session` object:

```python
conn = session.connect_cloud("project_id")
```

Directly with a sessionId (cookie connect):

```python
conn = scratch3.CloudConnection(project_id = "project_id", username="username", session_id="sessionId")
```

**Connect to the TurboWarp cloud:**

Does not require a session.

```python
conn = scratch3.TwCloudConnection(project_id = "project_id", username="username")  
# Optional argument: cloud_host="wss://clouddata.turbowarp.org"
# To connect to forkphorus's cloud server, use cloud_host="wss://stratus.turbowarp.org"
```

**Set a cloud var:**

New Scratchers can set Scratch cloud variables too.

```python
conn.set_var("variable", "value") #the variable name is specified without the cloud emoji
```

**Get a Scratch cloud var from the clouddata logs:**

Does not require a connection / session.

```python
value = scratch3.get_var("project_id", "variable")
variables = scratch3.get_cloud("project_id") #Returns a dict with all cloud var values
logs = scratch3.get_cloud_logs("project_id") #Returns the cloud logs as list
```

**Get a Scratch / TurboWarp cloud var from the websocket:** (new in v0.8.0)

Requires a connection to Scratch or TurboWarp's cloud (a `CloudConnection` / `TwCloudConnection` object).

```python
value = conn.get_var("variable")
```

**Close the cloud connection:**

```python
conn.disconnect()
```

# Encoding / Decoding  `scratch3.Encoding`

Scratchattach has a built in encoder. Scratch sprite to decode texts encoded with scratchattach: https://scratch3-assets.1tim.repl.co/Encoder.sprite3

```python
from scratchattach import Encoding

Encoding.encode("input") #will return the encoded text
Encoding.decode("encoded") #will decode an encoded text
```

# Cloud events  `scratch3.CloudEvents`

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

events.start()
```

**How to use with TurboWarp:** (new in v0.4.7)

```python
import scratchattach as scratch3

events = scratch3.TwCloudEvents("project_id")

...
```

**Functions:**
```py
events.start(thread=True)
events.pause()
events.resume()
events.stop()
```

# Cloud Requests  `scratch3.CloudRequests`

Cloud Requests Framework (inspired by discord.py) that allows Scratch projects and Python to interact

*This makes it possible to access data like message counts, user stats and more from Scratch projects! Uses cloud variables to transmit data.*

**[Cloud Requests are documented on this page:](https://github.com/TimMcCool/scratchattach/wiki/Cloud-Requests)**

[https://github.com/TimMcCool/scratchattach/blob/main/CLOUD_REQUESTS.md](https://github.com/TimMcCool/scratchattach/wiki/Cloud-Requests)

If you want to access external information in Scratch projects or store data on an external database, scratchattach's Cloud Requests are ideal for your project:
- Similar to cloud events, but send back data to the project
- Automatically encode / decode sent data
- Tons of extra features

# Users  `scratch3.User`

**Get a user:**
```python
user = session.connect_user("username")
```

Get the user that you are logged in with:
```python
session.get_linked_user()
```

You can also get users without logging in: (but then you can't use any functions that require a login, like user.follow(), user.post_comment(), ...)
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
user.activity_html(limit=1000) #Returns the user's activity as HTML document

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
user.set_featured("project_id", label="") #Changes the featured project

user.stats() #Returns the user's statistics as dict. Fetched from ScratchDB
user.ranks() #Returns the user's ranks as dict. Fetched from ScratchDB
user.followers_over_time(segment=1, range=30) #Fetched from ScratchDB

user.forum_posts(page=0, order="newest") #Returns a list of scratch3.ForumPost objects. New in v0.5.5. Fetched from ScratchDB
user.forum_counts() #Returns the amount of posts a user has written different forums as dict. Fetched from ScratchDB
user.forum_counts_over_time() #Fetched from ScratchDB
user.forum_signature() #Fetched from ScratchDB
user.forum_signature_history() #A change log for the user's forum history. Fetched from ScratchDB

user.ocular_status() #Returns information about the user's ocular status, like the status text, the color, and the time of the last update.
```

# Projects  `scratch3.Project`

**Get a project:**
```python
project = session.connect_project("project_id")
```

You can also get projects without logging in: (but then you can't use any functions that require a login, and you can't get your unshared projects)
```python
project = scratch3.get_project("project_id")
```

**Attributes:**
```python
project.id  #Returns the project id
project.url  #Returns the project url
project.title #Returns the project title
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
project.moderation_status() #Returns the project's moderation status (either "safe" or "notsafe" (nfe)). New in v0.5.4. Fetched from jeffalo.net

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
project.set_thumbnail(file="filename.png") #File must be .png and fit Scratch's thumbnail guidelines
project.share()
project.unshare()

project.turn_off_commenting()
project.turn_on_commenting()
project.toggle_commenting()

project.remixes(limit=None, offset=0) #Returns the remixes as list of scratch3.Project
project.studios(limit=None, offset=0) #Returns the studios the project is in as list of dicts

project.download(filename="project_name.sb3", dir="") #Downloads the project to your computer. The downloaded file will only work in the online editor
project.get_raw_json() #Returns the json of the project content as dict
project.get_creator_agent() #Returns the user-agent of the user who created the project (with information about their browser and OS)
```

# Unshared projects  `scratch3.PartialProject`

When connecting / getting a project that you can't access, a `PartialProject` object is returned instead.

**Most attributes and most functions don't work for such projects. However, these still work:**
```python
project.remixes(limit=None, offset=0)
```

# Studios  `scratch3.Studio`
(New in v0.5.0)

**Get a studio:**
```python
studio = session.connect_studio("studio_id")
```
You can also get studios without logging in: (But then you can't use any functions that require a login, like studio.follow(), studio.add_project(), ...)
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
studio.update()  #Updates the above data
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

studio.set_description("new description")
studio.set_title("new title")
studio.open_projects() #Allows everyone to add projects
studio.close_projects()

studio.turn_off_commenting() # New in v1.0.1
studio.turn_on_commenting()
studio.toggle_commenting()

studio.invite_curator("username")
studio.promote_curator("username")
studio.remove_curator("username")
studio.leave() #Removes yourself from the studio

studio.projects(limit=40, offset=0)
studio.curators(limit=24, offset=0) #Returns the curators as list of users (scratch3.User)
studio.managers(limit=24, offset=0)
studio.activity(limit=24, offset=0) #New in v1.0.1
```

# Search / Explore page

Doesn't require a session

**Search:**
```python
session.search_projects(query="query", mode="trending", language="en", limit=40, offset=0)
scratch3.search_projects(query="query", mode="trending", language="en", limit=40, offset=0) #Doesn't require logging in

scratch3.search_studios(query="query", mode="trending", language="en", limit=40, offset=0)

session.search_posts(query="query", order="newest", page=0) #Searches forum posts. Returns a list of scratch3.ForumPost objects
scratch3.search_posts(query="query", order="newest", page=0) #Doesn't require logging in
```

**Get the explore page:**
```python
session.explore_projects(query="*", mode="trending", language="en", limit=40, offset=0)
scratch3.explore_projects(query="*", mode="trending", language="en", limit=40, offset=0) #Doesn't require logging in

scratch3.explore_studios(query="*", mode="trending", language="en", limit=40, offset=0)
```

# Messages / My stuff page

```python
session.mystuff_projects("all", page=1, sort_by="") #Returns the projects from your "My stuff" page as list

session.messages(limit=40, offset=0) #Returns your messages as dict
session.clear_messages() #Marks your messages as read
session.get_message_count() #Returns your message count
```

# Frontpage

```python
scratch3.get_news(limit=10, offset=0) #Returns the news from the Scratch front page as list

scratch3.featured_projects() #Returns the featured projects from the Scratch homepage as list
scratch3.featured_studios()
scratch3.top_loved()
scratch3.top_remixed()
scratch3.newest_projects() #Returns a list with the newest Scratch projects. This list is not present on the Scratch home page, but the API still provides it.
scratch3.design_studio_projects()

session.get_feed(limit=20, offset=0) #Returns your "What's happening" section from the Scratch front page as list
session.loved_by_followed_users(limit=40, offset=0) #Returns the projects loved by users you are following as list
```

# Forum topics `scratch3.ForumTopic`
(New in v0.5.5)
All of this data is fetched from ScratchDB v3, therefore it may be slighty off.

**Get a forum topic:**
```python
topic = session.connect_topic("topic_id")
```
You can also get topics without logging in:
```python
topic = scratch3.get_topic("topic_id")
```

**Get a list of the topics in a category:**
```python
topic_list = session.connect_topic_list("category_name", page=0)
```
You can also do this without logging in:
```python
topic_list = scratch3.get_topic_list("category_name", page=0)
```

**Attributes:**
```python
topic.title
topic.category
topic.closed
topic.deleted
topic.post_count
# ----- ----- #
topic.update()  #Updates the above data
```

**Functions:**
```python
topic.posts(page=0, order="oldest") #Returns the topic posts as list of scratch3.ForumPost objects. Possible parameters for "order" are "oldest" and "newest"
topic.first_post() #Returns the first topic post as scratch3.ForumPost object
topic.follow()
topic.unfollow()

topic.post_count_by_user("username")
topic.activity() #Returns an activity / change log for the topic
```

To prevent spam, adding posts to topics is not a scratchattach feature and never will be.

# Forum posts `scratch3.ForumPost`
(New in v0.5.5)
All of this data is fetched from ScratchDB v3, therefore it may be slighty off.

**Get a forum post:**
```python
post = session.connect_post("post_id")
```
You can also get posts without logging in:
```python
post = scratch3.get_post("post_id")
```

**Search for forum posts:**
```python
post_list = session.search_posts(query="query", order="newest", page=0) #Returns a list of scratch3.ForumPost objects
```
You can also get posts without logging in:
```python
post_list = scratch3.search_posts(query="query", order="newest", page=0) #Returns a list of scratch3.ForumPost objects
```

**Attributes:**
```python
post.id
post.author
post.posted #The date the post was made
post.edited #The date of the most recent post edit. If the post wasn't edited this is None
post.edited_by #The user who made the most recent edit. If the post wasn't edited this is None
post.deleted #Whether the post was deleted
post.html_content #Returns the content as HTML
post.bb_content #Returns the content as BBCode
post.topic_id #The id of the topic the post is in
post.topic_name #The name of the topic the post is in
post.topic_category #The name of the category the post topic is in
# ----- ----- #
post.update()  #Updates the above data
```

**Functions:**
```python
post.get_topic() #Returns the topic the post is in as scratch3.ForumTopic object
post.get_author() #Returns the post author as scratch3.User object

post.edit(new_content) #Requires you to be the post author.

post.ocular_reactions()
```

# Site stats and health

```python
scratch3.total_site_stats() #Returns the total project count, user count, comment count and other total counts
scratch3.monthly_site_traffic() #Returns last month's site traffic
scratch3.country_counts() #Returns the amount of Scratch users in each country
scratch3.age_distribution() #Returns how many Scratchers were 1,2,3,4,5,6,... years old when they created their account

scratch3.get_health() #Returns Scratch's health data
```

# Backpack

```python
session.backpack(limit=20, offset=0) #Returns the contents of your backpack as dictionary
session.delete_from_backpack("asset id") #Deletes an asset from your backpack
```

# Contributors

- Allmost all code by TimMcCool.
- See the GitHub repository for full list of contributors.
- Create a pull request to contribute code yourself.

# Support

If you need help with your code, leave a comment on TimMcCool's Scratch
profile: https://scratch.mit.edu/users/TimMcCool/
