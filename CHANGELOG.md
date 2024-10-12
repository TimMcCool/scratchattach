# 2.0.0

Some less important changes are not listed here. [How to migrate to v2 quickly](https://github.com/TimMcCool/scratchattach/wiki/Migrating-to-v2)

scratchattach is now by far the biggest Scratch API wrapper.

## Key Changes in v2.0.0:

- Tons of new features.
- New object-oriented design with base classes for better abstraction.
- Cloud storage framework, comment filterbot and cloud events / cloud requests improvements.
- Project JSON editing capabilities and new features for self-hosting TurboWarp servers.
- Session handling is more consistent across the library.

## General:

- Structured all the classes in three categories (site components, cloud, and event handlers). There are three base classes: BaseSiteComponent, BaseCloud and BaseEventHandler. All other classes inherit from one of these base classes, common methods are definied within the base class. This adds more abstraction to the library.
- Added utils > commons.py file with methods for getting an object of a class inheriting from BaseSiteComponent and for getting and parsing data from an iterative Scratch API.
- In method names "get_" always means that there's no Session connected to the returned object and that the returned object therefore can't be used for performing operations (like .love(), .follow()) that require authentication.
"connect_" always means that the Session will be connected to the returned object / saved in the object's ._session attribute. If a method is called on this object, the object returned by the method will also have the Session connected to it. This makes it possible to write code like `session.connect_user("username").projects()[0].comment_by_id("comment_id").reply("text")` without having to worry about staying logged in.
This is now used consistently throughout the whole library.
- Added new logo and scratchattach website (scratchattach.tim1de.net) featuring scratchattach projects (automatically fetched from the Scratch studio)

## Sessions / Logging in:

- Added new login method *login by session string*. A session string is a string that saves both your session id and username / password. When using it to login, scratchattach will attempt both login methods.
- To login by session id, you now have to use `session = sa.login_by_id("session_id")`
- Added `session.admin_messages()` (gets alerts from the Scratch team), `session.mystuff_studios()`, `session.backpack()`, `session.become_scratcher_invite()`
- `session.message_count()` now returns the count from the API used by 2.0-style pages, while `user.message_count()` uses the API from the 3.0-style pages

## Users:

- Added `session.connect_user_by_id(user_id)` for fetching a user by their user id
- Added `user.comment_by_id` for getting a profile comment (as scratchattach.Comment object) by its id
- Added `user.verify_identity()` futcion which returns a Verificator class, making it easy to verify the user's identity in an application by asking them to comment a token on a project

## Studios:

- Studios are now represented as scratchattach.Studio objects everywhere (for example, when using `session.mystuff_studios()`, `session.search_studios()` etc.)
- Added `studio.promote_curator()`, `studio.your_role()` and `studio.transfer_ownership()` methods
- Added `studio.comment_by_id` for getting a studio comment (as scratchattach.Comment object) by its id

## Projects: 

- Projects are now represented as scratchattach.Project objects everywhere (for example, when using `sa.featured_projects()` etc.)
- Added `session.create_project()` and `project.create_remix()` methods (also works on unshared projects) for creating projects
- Added `project.load_description()` method that allows getting the title and description of an unshared project (Warning: Using it might be against Scratch's rules)
- Added `project.body()` function that loads the contents of the project as `scratchattach.ProjectBody` object (this class allows editing the project further using Python, then it can be saved on Scratch using `project.set_body(project_body)`)
- Made it so specific errors are raised when loving, faving etc. fails
- Added `project.visibility()` method which returns info about the project's visibility on Scratch

## Forum:

- Fixed session.connect_topic, scratchattach.get_topic and connect_ / get_topic_list functions (they now work without ScratchDB and scrape the data directly from the website or the RSS feed)
- Removed get_post and connect_post functions (getting a post by id is no longer possible)

## Comments:

- Added the scratchattach.Comment class representing a project, studio or profile comment
- The class has methods like .author(), .place(), .parent_comment() -> scratchattach.Comment, .replies(), .reply("content") (for replying directly to a comment), .delete(), .report()

## Messages / Activities:

- Added the scratchattach.Activity class representing an activity shown in the "What I've been doing" feed of a user, in the "What's happening?" feed on the front page or in the activity feed of a studio, or representing a message (in Scratch's API, the JSON objects saving messages and activities share the same structure)
- session.messages(), studio.activiy(), user.activity() and session.feed() now return lists of Activity objects
- The class has the methods .actor(), .target() (returning the user, studio, project or comment the activity targets)

## Cloud:

- Completely reworked cloud variable classes and methods
- Added a generalized base class (BaseCloud) for representing the cloud of any cloud variable server.
- Added ScratchCloud and TwCloud inherit from this class and are optimized for using Scratch / TurboWarp cloud variables. There's also CustomCloud (also inheriting from BaseCloud) which allows setting all attributes yourself in the constructor. Cloud objects are obtained using scratch3.get_cloud(project_id) / session.connect_cloud(project_id).
- If you need even more customizability (like defining your own set_var function etc) you can create your own class inheriting from BaseCloud (there's more info about this in the docstring of BaseCloud).
- Added a built-in cloud recorder. When calling the cloud.get_var(var_name) function for the first time, it will automatically start recording cloud variable updates on the websocket using the new built-in scratchattach.eventhandlers.cloud_recorder.CloudRecorder class. cloud.get_var will return the recorded value, this means you can now safely use the cloud.get_var and cloud.get_all_vars functions in a loop without having to worry about spamming an API.
- cloud.set_var() now allows setting cloud variables faster (15 var sets per second)
- Added cloud.set_vars function for setting multiple cloud vars simultaneously (with an intelligent rate-limit handler)
- Added cloud.reconnect()
- Added ScratchCloud.logs(), the cloud activities are not represented as scratchattach.CloudActivity objects. This class has the methods .load_log_data() (loads the user who set the var from the clouddata logs, if logs are available for the cloud), .actor() -> scratchattach.User and .project() -> scratchattach.Project

## Cloud events:

- The event handler is now initialized using `events = cloud.events()`. There's one event handler class that gets data from the websocket (CloudEvents) and another one that gets the data from the cloud logs (CloudLogEvent)
- Abstracted lots of functions in the BaseEventHandler class which is also used by scratchattach's new message events
- on_set event function is now called with a CloudActivity object as argument

## Cloud requests:

- The event handler is now initialized using `client = cloud.requests()`. The same CloudRequests class is used for any cloud variable websocket (Scratch, TurboWarp etc.)
- Massively lowered CPU usage by implementing threading.Event in the event loops to lock them until a request is received
- Added .send("data") for sending messages (either string, int or list of string / int) to the Scratch project without a priorly received request
- Added TCP-like packet loss prevention
- client.get_requester() and client.get_exact_timestamp() now work for requests ran in threads (all requests are now ran in threads by default)
- It's now possible to add priority values to requests to determine the order in which responses should be sent back to the Scratch project
- Requests not ran in threads no longer block the process sending back data to Scratch -> faster request handling
- Requests are now saved as callable scratchattach.eventhandlers.cloud_requests.Request objects in the CloudRequests._requests dict, cleaned up code a lot, CloudRequests is now built upon / inheriting from CloudEvents

## Cloud storage (new in v2.0):

Docs: https://github.com/TimMcCool/scratchattach/wiki/Cloud-Storage

- A simple key-value storage engine that can be initialized using `storage = cloud.storage()`, built upon / inheriting from CloudRequests
- Allows adding databases, getting / setting attributes from the Scratch project (just like for cloud requests, there's a pre-built sprite) and saving them in JSON files automatically
- An event is called on every set operation -> allows connecting dbs like mongodb

## MultiEventHandlers (new in v2.0):

- Added new `scratchattach.MultiEventHandlers([ ... ])` class that allows combining multiple event handlers (cloud events, cloud requests, cloud storages, message events or filterbots) in one object

## Message events and Filterbot:

Docs: https://github.com/TimMcCool/scratchattach/wiki/Filterbot

- Added new `MessageEvents` class that allows reacting to messages in real time. Every time you receive a message on Scratch, an event is be called (similar to cloud events)
- Added a `Filterbot` framework, a bot automatically checking comments you receive, checking them for spam and blacklisted words and deleting them if they match criteria. There are different kind of filters, some always applying (HardFilter) while others only apply if a cumulative score is exceeded (SoftFilter). There's also SpamFilter which only deletes comments matching criteria if they are posted too often. There are also pre-built filter profiles (like an f4f filter and an ads filter).

## Self-hosting a TurboWarp cloud variable websocket (new in v2.0):

Docs: https://github.com/TimMcCool/scratchattach/wiki/Self%E2%80%90hosting-TurboWarp-cloud-websockets

- Added a feature for easily hosting a websocket server locally (TwCloudServer class). The server is automatically set up for being used as cloud_host for a project running on TurboWarp (through TurboWarp's ?cloud_host= URL parameter).
- The server is is initialized using `server = sa.init_cloud_server()` and started using `server.start()`. After starting, the address where the server is running is printed in the console. This address (including the port) has to be passed to TurboWarp's ?cloud_host= URL parameter. When hosting the server locally, it will be only be accessible by devices in your network. To host online, use a hosting platform and start the websocket server there.
- You can allow non-numeric cloud values (enabled by default)
- You can customize the IP addresss (localhost by default) and the port (8080 by default) where the server is running on
- You can block IP addresses from connecting to the server
- You can directly set cloud variables server-side anytime.
- You can access the values of the cloud variables and the users connected to the server directly from the Python backend anytime, using `server.active_user_names(project_id)`, `server.active_user_ips(project_id`, `server.get_var(project_id, var_name)` etc. There are also events called on cloud variable sets (the TwCloudServer class is inheriting from BaseEvenHandler).

## Project JSON editing capabilities (new in v2.0):

Docs: https://github.com/TimMcCool/scratchattach/wiki/Project-JSON-editing-capabilities

- Added ProjectBody representing the contents of a Scratch project.
- The contents of a Scratch project can be loaded from a Scratch community project using `body = project.body()` or from a sb3 file using `body = sa.read_sb3_file("filepath")`. You can also create an empty project using `body = sa.get_empty_project_pb()`
- The attributes .sprites, .monitors (the variables and lists shown in the project), .extensions and .meta save the project contents
- There's a ProjectBody.BaseProjectBodyComponent class. Variables, lists, sprites, assets, blocks and monitors are represented using Variable, List, Sprite, Asset, Block and Monitor classes that inherit from BaseProjectBodyComponent.
- It is possible to add and remove variables and convert variables to cloud variables
- It is possible to navigate through the project's blocks using `block = Sprite.block_by_id(block_id)`, `block.complete_chain()`, `block2 = block.attached_block()` etc. You can add blocks and edit blocks using `block.attach_block`, `block.delete()`, `sprite.add_block(block)` etc. (there are many more features, [see the docs for all of them](https://github.com/TimMcCool/scratchattach/wiki/Project-JSON-editing-capabilities))
- It is possible to add assets (sounds and costumes) to the project. The added assets are automatically uploaded to the Scratch website if the ProjectBody object was connected using a Project object which was connected using a Session object.
- Assets can be directly downloaded using sa.download_asset(asset_id_with_file_ext) or Asset.download()

## Other stuff:

- Added functions for getting statistics: `sa.monthly_comment_activity()`, `sa.monthly_project_shares()`, `sa.monthly_active_users()`, `sa.monthly_activity_trends()`
- Added functions for checking if a username / password is available and allowed: `sa.check_username("username")`, `sa.check_password("password")`
- Added `sa.aprilfools_get_counter()` and `sa.aprilfools_increment_counter()`
- Added scratchattach.BackpackAsset class representing an object saved in the backpack, with the .download() and .delete() methods

# 1.7.3

- Added `project.get_comment` and `studio.get_comment` functions (allow getting a comment by id)
- Added `user.does_exist()` and `user.is_new_scratcher()` functions
- Added `user.set_forum_signature("new_signature")` function - allows setting forum signature of logged in user

# 1.6.2

- Added `client.stop()` to cloud requests (will stop cloud request handler and all background event handlers)
- You can now access the letters used by the encoder: `scratch3.encoder.letters`
- Added `scratch3.Encoding.replace_char("old_char", "new_char")`
- Added `studio.accept_invite()`
- Added `project.upload_json_from("other_project_id")`
- `scratch3.connect_tw_cloud("project_id")` - "project_id" arg can now be a non-integer
- Added `daemon` argument to `client.run()` (cloud requests)

# 1.5.1

- Added `session.connect_tw_cloud` function which was mentioned in the documentation but missing in the code

# 1.5.0

- Fixed an issue with `WsCloudEvents`, updating is highly recommended

# 1.4.8

- Fixed `scratchattach.search_projects`, `scratchattach.User.projects`, `scratchattach.User.favorites` and `scratchattach.User.viewed_projects` (these broke in v1.4.0 due to changing the module names)
- Removed broken function `scratchattach.search_comments` entirely

# 1.4.7

- Fixed `scratchattach.get_cloud_logs` function (has been broken since v1.4.0)

# 1.4.6

- Fixed `project.studios()` function

# 1.4.5

- Added `studio.set_thumbnail(file="filename")` method
- Added `project.set_json(json_data)` method

# 1.4.0

- Changed module names (removed _ charaters from the filenames of the files in /scratchattach) in order to document the project with sphinx
- Added sphinx documentation (WIP): https://scratchattach.readthedocs.io/en/latest/
- Added comments to code
