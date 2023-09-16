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