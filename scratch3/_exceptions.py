class UnauthorizedError(Exception):
    """
    A function that requires authentication was called without being authenticated.
    """
    pass
