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