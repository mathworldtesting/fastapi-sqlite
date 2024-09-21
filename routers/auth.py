from fastapi import APIRouter

router = APIRouter()


@router.get("/auth/")
async def get_users():
    """
    Returns a JSON object with a single key-value pair, where the key is "user"
    and the value is "authenticated".

    This endpoint is meant to be used to test authentication. It does not
    actually return any user information.
    """
    return {"user": "authenticated"}