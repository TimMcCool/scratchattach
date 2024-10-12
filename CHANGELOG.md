# 2.0.0

Some less important changes are not listed here. [How to migrate to v2 quicky](https://github.com/TimMcCool/scratchattach/wiki/Migrating-to-v2)

## General:

- Structured all the classes in three categories (site components, cloud, and event handlers). There are three base classes: BaseSiteComponent, BaseCloud and BaseEventHandler. All other classes inherit from one of these base classes, common methods are definied within the base class. This adds more abstraction to the library.
- Added utils > commons.py file with methods for getting an object of a class inheriting from BaseSiteComponent and for getting and parsing data from an iterative Scratch API.
- In method names "get_" always means that there's no Session connected to the returned object and that the returned object therefore can't be used for performing operations (like .love(), .follow()) that require authentication.
"connect_" always means that the Session will be connected to the returned object / saved in the object's ._session attribute.
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
