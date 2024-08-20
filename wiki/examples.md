# Example scripts

**Set a cloud var with scratchattach:**
```py
# Example: Set Cloud Variable

import scratchattach as scratch3 # Import the scratchattach module

# Log in with your credintals to give you administrator permissions over your project.
session = scratch3.login("username", "password") # Login with Scratch login information
conn = session.connect_cloud("project_id") # Replace with your project ID

conn.set_var("variable", value) # Set a cloud variable to a certain int value. 
```

**Cloud event handler:**
```py
import scratchattach as scratch3 # Import the scratchattach module
events = scratch3.CloudEvents("project_id") # Get project_id. No login required.

# Get event listener.
@events.event
def on_set(event): #Called when a cloud var is set
    # Things inside here only happen if a cloud variable is set. 
    print(f"{event.user} set the variable {event.var} to the value {event.value} at {event.timestamp}")

events.start() # Start listening for events. 
```

**Comment on a project:**
```py
import scratchattach as scratch3 # Import the scratchattach module

session = scratch3.login("username", "password") # Login with Scratch login information
project = session.connect_project("project_id") # Get project by ID

project.post_comment("Hi guys!") # Post a comment on the project.
```

**Automatically update your profile with your follower count:**
```py
import scratchattach as scratch3 # Import the scratchattach module
import time # Import time module.

session = scratch3.login("username", "password") # Login with Scratch login information
user = session.get_linked_user() # Get information with the user session

while True:
    follower_count = user.follower_count() # Get follower count
    user.set_bio(f"My follower count: {follower_count}") # Update "bio" page on user profile
    time.sleep(60) # The follower count is updated every 60 seconds # Wait 60 seconds before updating them again. 
```

# Templates

[**replit.com: Template for interacting with Scratch's cloud variables using scratchattach**](https://replit.com/@1Tim/Scratch-Cloud-Variable-Template?v=1#README.md)

# Example projects

[Check out this repo: https://github.com/mas6y6/scratchattach-examples](https://github.com/mas6y6/scratchattach-examples)

[Also: https://github.com/programORdie2/servers24-7](https://github.com/programORdie2/servers24-7)

More coming soon 
