class Unauthorized(Exception):
    pass

class Unauthenticated(Exception):
    pass

class UserNotFound(Exception):
    pass

class ProjectNotFound(Exception):
    pass

class StudioNotFound(Exception):
    pass

class ConnectionError(Exception):
    pass

class XTokenError(Exception):
    """
    Raised when there are no XToken headers available
    """
    pass

class LoginFailure(Exception):
    """
    Raised when there are no XToken headers available
    """
    pass

class InvalidCloudValue(Exception):
    pass

class FetchError(Exception):
    pass

class InvalidDecodeInput(Exception):
    pass

class BadRequest(Exception):
    pass

class Response429(Exception):
    pass

class RequestNotFound(Exception):
    pass
