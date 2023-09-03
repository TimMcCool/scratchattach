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
- [Change log](https://github.com/TimMcCool/scratchattach/blob/main/CHANGELOG.md)

# Examples
**Set a cloud var with scratchattach:**
```py
import scratchattach as scratch3

session = scratch3.login("username", "password")
conn = session.connect_cloud("project_id")

conn.set_var("variable", value)
```

**Cloud event handler:**
```py
import scratchattach as scratch3
events = scratch3.CloudEvents("project_id")

@events.event
def on_set(event): #Called when a cloud var is set
    print(f"{event.user} set the variable {event.var} to the valuee {event.value} at {event.timestamp}")

events.start()
```

**Comment on a project:**
```py
import scratchattach as scratch3

session = scratch3.login("username", "password")
project = session.connect_project("project_id")

project.post_comment("Hi guys!")
```

**Automatically update your profile with your follower count:**
```py
import scratchattach as scratch3
import time

session = scratch3.login("username", "password")
user = session.get_linked_user()

while True:
    follower_count = user.follower_count()
    user.set_bio(f"My follower count: {follower_count}")
    time.sleep(60) # The follower count is updated every 60 seconds
```

# Contributors

- Allmost all code by TimMcCool.
- See the GitHub repository for full list of contributors.
- Create a pull request to contribute code yourself.

# Support

If you need help with your code, leave a comment in the [official forum topic](https://scratch.mit.edu/discuss/topic/603418/
) on [TimMcCool's Scratch
profile](https://scratch.mit.edu/users/TimMcCool/) or open an issue on the github repo

<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>

# logging-in--scratch3session

This section was moved to a new link: [https://github.com/TimMcCool/scratchattach/wiki#logging-in](https://github.com/TimMcCool/scratchattach/wiki#logging-in)



<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
<br/><br/>
