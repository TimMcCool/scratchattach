from typing_extensions import TypedDict, Literal

SessionIDDict = TypedDict(
    "SessionIDDict",
    {
        "username": str,
        "_auth_user_id": str,
        "testcookie": Literal["worked"],
        "_auth_user_backend": Literal["authentication.backends.ReplicationBackend"],
        "token": str,
        "login-ip": str,
        "_language": str,  #'en'
        "django_timezone": Literal["America/New_York"],
        "_auth_user_hash": str,
    },
)
