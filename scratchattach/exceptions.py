class Unauthenticated(Exception):
    """
    Raised when an action that requires a log in / session is performed on an object that wasn't created with a session.

    Example: If the :meth:`scratchattach.project.Project.love` function is called on a Project object created with :meth:`scratchattach.project.get_project`, it will raise this error.
    
    If Project / Studio / User objects are created using :meth:`scratchattach.get_project` / :meth:`scratchattach.get_studio` / :meth:`scratchattach.get_user`, they can't be used to perform action that require a session. Use :meth:`scratchattach.Session.connect_project` / :meth:`scratchattach.Session.connect_user` / :meth:`scratchattach.Session.connect_studio` instead.
    """
    def __init__(self, message=""):
        self.message = "You can't perform this action because you're not logged in. The object on which the method was called wasn't created with a session. More information: https://scratchattach.readthedocs.io/en/latest/scratchattach.html#scratchattach.exceptions.Unauthenticated"
        super().__init__(self.message)
    pass

class Unauthorized(Exception):
    """
    Raised when an action is performed that the user associated with the session that the object was created with is not allowed to do.
    
    Example: Changing the "about me" of other users will raise this error.
    """
    def __init__(self, message=""):
        self.message = "You are not authorized to perform this action."
        super().__init__(self.message)
    pass

class UserNotFound(Exception):
    """
    Raised when a non-existent user is requested.
    """
    pass

class ProjectNotFound(Exception):
    """
    Raised when a non-existent project is requested.
    """
    pass

class StudioNotFound(Exception):
    """
    Raised when a non-existent studio is requested.
    """
    pass

class ConnectionError(Exception):
    """
    Raised when connecting to Scratch's cloud server fails. This can have various reasons.
    """
    pass

class XTokenError(Exception):
    """
    Raised when an action can't be performed because there is no XToken available.
     
    This error can occur if the xtoken couldn't be fetched when the session was created. Some actions (like loving projects) require providing this token.
    """
    pass

class LoginFailure(Exception):
    """
    Raised when the Scratch server doesn't respond with a session id.

    This could be caused by an invalid username / password. Another cause could be that your IP address was banned from logging in to Scratch. If you're using an online IDE (like replit), try running the code on your computer.
    """
    pass

class InvalidCloudValue(Exception):
    """
    Raised when a cloud variable is set to an invalid value.
    """
    pass

class FetchError(Exception):
    """
    Raised when getting information from the Scratch API fails. This can have various reasons. Make sure all provided arguments are valid. If you provided an "offset" keyword argument, its value shouldn't exceed 40.
    """
    pass

class InvalidDecodeInput(Exception):
    """
    Raised when the built-in decoder :meth:`scratchattach.encoder.Encoding.decode` receives an invalid input.
    """
    pass

class BadRequest(Exception):
    """
    Raised when the Scratch API responds with a "Bad Request" error message. This can have various reasons. Make sure all provided arguments are valid. If you provided an "offset" keyword argument, its value shouldn't exceed 40.
    """
    pass

class Response429(Exception):
    """
    Raised when the Scratch API responds with a 429 error. This means that your network was ratelimited or blocked by Scratch. If you're using an online IDE (like replit.com), try running the code on your computer.
    """
    pass

class RequestNotFound(Exception):
    """
    Cloud Requests: Raised when a non-existent cloud request is edited using :meth:`scratchattach.cloud_requests.CloudRequests.edit_request`.
    """
    pass

class CommentPostFailure(Exception):
    """
    Raised when a comment fails to post. This can have various reasons.
    """
    pass
