# Example scripts

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
    print(f"{event.user} set the variable {event.var} to the value {event.value} at {event.timestamp}")

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

# Templates

[**replit.com: Template for interacting with Scratch's cloud variables using scratchattach**](https://replit.com/@1Tim/Scratch-Cloud-Variable-Template?v=1#README.md)

# Example projects

[Check out this repo: https://github.com/mas6y6/scratchattach-examples](https://github.com/mas6y6/scratchattach-examples)

[Also: https://github.com/programORdie2/servers24-7](https://github.com/programORdie2/servers24-7)

More coming soon 