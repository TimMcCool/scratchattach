# NOTE: There also exists typed dicts in site/typed_dicts. They should be moved here.

from typing_extensions import TypedDict

SessionIDDict = TypedDict(
    "SessionIDDict",
    {
        "username": str,
        "_auth_user_id": str,
        "testcookie": str,
        "_auth_user_backend": str,
        "token": str,
        "login-ip": str,
        "_language": str,
        "django_timezone": str,
        "_auth_user_hash": str,
    },
)
