from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status
from pydantic import BaseModel, Field
from config import settings
from auth.supabase import supabase_auth

class UserContext(BaseModel):
    id: str = "guest_user"
    email: str = "guest@example.com"
    role: str = "authenticated"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_guest: bool = False

async def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> UserContext:
    """
    FastAPI dependency that validates Supabase JWT bearer tokens.
    Provides seamless guest fallback when REQUIRE_AUTH is False.
    """
    token = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if token:
        user_info = await supabase_auth.verify_jwt(token)
        if user_info:
            return UserContext(
                id=user_info["id"],
                email=user_info.get("email", "unknown@user.com"),
                role=user_info.get("role", "authenticated"),
                metadata=user_info.get("user_metadata", {}),
                is_guest=False
            )

    # If auth is strictly required and token is invalid or missing
    if settings.REQUIRE_AUTH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Supabase bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Otherwise return Guest context
    return UserContext(
        id="guest_user_1",
        email="guest@Ocg-agent.local",
        role="guest",
        metadata={"auth_mode": "guest"},
        is_guest=True
    )
