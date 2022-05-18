class Unauthorized(Exception):
    pass

class Unauthenticated(Exception):
    pass

class UserNotFound(Exception):
    pass

class ProjectNotFound(Exception):
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

class VarNotFound(Exception):
    """
    Raised when the variable has not been set from the TurboWarp client side (Variables need to be set before they can be read)
    """
    pass
