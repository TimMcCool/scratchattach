Scratch API wrapper with support for almost all site features. Created by [TimMcCool](https://scratch.mit.edu/users/TimMcCool/).

This library can set cloud variables, follow Scratchers, post comments and do so much more! It has special features that make it easy to transmit data through cloud variables.

<p align="left">
  <img width="160" height="133" src="https://github.com/TimMcCool/scratchattach/blob/main/logos/logo_dark_transparent_eyes.svg">
</p>

[![PyPI status](https://img.shields.io/pypi/status/scratchattach.svg)](https://pypi.python.org/pypi/scratchattach/)
[![PyPI download month](https://img.shields.io/pypi/dm/scratchattach.svg)](https://pypi.python.org/pypi/scratchattach/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/scratchattach.svg)](https://pypi.python.org/pypi/scratchattach/)
[![GitHub license](https://badgen.net/github/license/TimMcCool/scratchattach)](https://github.com/TimMcCool/scratchattach/blob/master/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/scratchattach/badge/?version=latest)](https://scratchattach.readthedocs.io/en/latest/?badge=latest)

# Links

- **[Documentation](https://github.com/TimMcCool/scratchattach/wiki)**
- [Extended documentation (WIP)](https://scratchattach.readthedocs.io/en/latest/)
- [Examples](https://github.com/TimMcCool/scratchattach/wiki/Examples)
- [Hosting](https://github.com/TimMcCool/scratchattach/wiki/Hosting)
- [Change log](https://github.com/TimMcCool/scratchattach/blob/main/CHANGELOG.md)

Report bugs by opening an issue on this repository. If you need help or guideance, leave a comment in the [official forum topic](https://scratch.mit.edu/discuss/topic/603418/
). Projects made using scratchattach can be added to [this Scratch studio](https://scratch.mit.edu/studios/31478892/).

# Example usage

```py
import scratchattach as scratch3

session = scratch3.login("username", "password")
conn = session.connect_cloud("project_id")

conn.set_var("variable", value)
```

**[More examples](https://github.com/TimMcCool/scratchattach/wiki/Examples)**

# Getting started

**Installation:**

Run the following command in your command prompt / shell:

```
pip install -U scratchattach
```

If this doesn't work, pip was not added to path when you installed Python. Try running:
```
python -m pip install -U scratchattach
```


**Logging in with username / password:**

```python
import scratchattach as scratch3

session = scratch3.login("username", "password")
```

`login()` returns a `Session` object that saves your login.

**Logging in with a sessionId:** *You can get your session id from your browser's cookies. [More information](https://github.com/TimMcCool/scratchattach/wiki/Get-your-session-id)*
```python
import scratchattach as scratch3

session = scratch3.Session("sessionId", username="username") #The username field is case sensitive
```

**Connect to the Scratch cloud:**

```python
conn = session.connect_cloud("project_id")
```

**Get / Set a cloud var:**

```python
value = scratch3.get_var("project_id", "variable")
conn.set_var("variable", "value") #the variable name is specified without the cloud emoji
```

**Follow a user / love a project:**

```python
user_to_follow = session.connect_user("username")
user_to_follow.follow()
project_to_love = session.connect_project("project_id")
project_to_love.love()
```

**All scratchattach features are documented in the [documentation](https://github.com/TimMcCool/scratchattach/wiki/#cloud-variables).**

# Contributors

- Allmost all code by TimMcCool.
- See the GitHub repository for full list of contributors.
- Create a pull request to contribute code yourself.
