**scratchattach is a Scratch API wrapper with support for almost all site features.** Created by [TimMcCool](https://scratch.mit.edu/users/TimMcCool/).

The library allows setting cloud variables, following users, updating your profile, and
so much more! Additionally, it provides frameworks that simplify sending data through cloud variables.

<p align="left" style="margin:10px">
  <img width="160" src="https://raw.githubusercontent.com/TimMcCool/scratchattach/refs/heads/main/logos/logo.svg">

[![PyPI status](https://img.shields.io/pypi/status/scratchattach.svg)](https://pypi.python.org/pypi/scratchattach/)
[![PyPI download month](https://img.shields.io/pypi/dm/scratchattach.svg)](https://pypi.python.org/pypi/scratchattach/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/scratchattach.svg)](https://pypi.python.org/pypi/scratchattach/)
[![GitHub license](https://badgen.net/github/license/TimMcCool/scratchattach)](https://github.com/TimMcCool/scratchattach/blob/master/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/scratchattach/badge/?version=latest)](https://scratchattach.readthedocs.io/en/latest/?badge=latest)

# Documentation

- **[Documentation](https://github.com/TimMcCool/scratchattach/wiki/Documentation)**

- [Cloud Variables](https://github.com/TimMcCool/scratchattach/wiki/Documentation#cloud-variables)
- [Cloud Requests](https://github.com/TimMcCool/scratchattach/wiki/Cloud-Requests)
- [Cloud Storage](https://github.com/TimMcCool/scratchattach/wiki/Cloud-Storage)
- [Filterbot](https://github.com/TimMcCool/scratchattach/wiki/Filterbot)
- [Self-hosting a TW cloud websocket](https://github.com/TimMcCool/scratchattach/wiki/Documentation#hosting-a-cloud-server)

# Helpful resources

- [Get your session id](https://github.com/TimMcCool/scratchattach/wiki/Get-your-session-id)

- [Examples](https://github.com/TimMcCool/scratchattach/wiki/Examples)
- [Hosting](https://github.com/TimMcCool/scratchattach/wiki/Hosting)

Report bugs by opening an issue on this repository. If you need help or guideance, leave a comment in the [official forum topic](https://scratch.mit.edu/discuss/topic/603418/
). Projects made using scratchattach can be added to [this Scratch studio](https://scratch.mit.edu/studios/31478892/).

# Helpful for contributors

- **[Structure of the library](https://github.com/TimMcCool/scratchattach/wiki/Structure-of-the-library)**

- [Extended documentation (WIP)](https://scratchattach.readthedocs.io/en/latest/)

- [Change log](https://github.com/TimMcCool/scratchattach/blob/main/CHANGELOG.md)

Contribute code by opening a pull request on this repository.

# ️Example usage

Set a cloud variable:

```py
import scratchattach as sa

session = sa.login("username", "password")
cloud = session.connect_cloud("project_id")

cloud.set_var("variable", value)
```

**[More examples](https://github.com/TimMcCool/scratchattach/wiki/Examples)**

# Getting started

**Installation:**

Run the following command in your command prompt / shell:

```
pip install -U scratchattach
```

If this doesn't work, try running:
```
python -m pip install -U scratchattach
```


**Logging in with username / password:**

```python
import scratchattach as sa

session = sa.login("username", "password")
```

`login()` returns a `Session` object that saves your login and can be used to connect objects like users, projects, clouds etc.

**Logging in with a sessionId:** *You can get your session id from your browser's cookies. [More information](https://github.com/TimMcCool/scratchattach/wiki/Get-your-session-id)*
```python
import scratchattach as sa

session = sa.login_by_id("sessionId", username="username") #The username field is case sensitive
```

**Cloud variables:**

```py
cloud = session.connect_cloud("project_id") # connect to the cloud

value = cloud.get_var("variable")
cloud.set_var("variable", "value") # the variable name is specified without the cloud emoji
```

**Cloud events:**

```py
cloud = session.connect_cloud('project_id')
events = cloud.events()

@events.event
def on_set(activity):
    print("variable", activity.var, "was set to", activity.value)
events.start()
```

**Follow users, love their projects and comment:**

```python
user = session.connect_user('username')
user.follow()

project = user.projects()[0]
project.love()
project.post_comment('Great project!')
```

**All scratchattach features are documented in the [documentation](https://github.com/TimMcCool/scratchattach/wiki/Documentation).**
