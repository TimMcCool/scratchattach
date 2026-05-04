from .keyhandler import get_auth

def vercel_auth() -> list[str]:
    data = get_auth()["vercel_auth"]
    return [
        data["vercel_token"],
        data["org_id"],
        data["project_id"]
    ]
