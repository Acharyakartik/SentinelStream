from fastapi import APIRouter, Form

from app.core.security import create_access_token

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/token")
async def issue_token(username: str = Form(...), password: str = Form(...)) -> dict:
    # Replace with proper user verification against an identity provider.
    if not username or not password:
        return {"access_token": "", "token_type": "bearer"}

    return {"access_token": create_access_token(subject=username), "token_type": "bearer"}
