import logging
from typing import Optional, Dict, Any
from supabase import create_client, Client
from config import settings

logger = logging.getLogger("Ocg_agent.auth")

class SupabaseAuthManager:
    """
    Supabase authentication and client wrapper.
    Handles user signup, signin, token verification, and session state.
    """

    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.anon_key = settings.SUPABASE_ANON_KEY
        self.client: Optional[Client] = None
        self._init_client()

    def _init_client(self):
        if not self.url or not self.anon_key or "mock" in self.url:
            logger.warning("Supabase URL / Anon Key not configured or using mock values.")
            return

        try:
            self.client = create_client(self.url, self.anon_key)
            logger.info("Supabase client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")

    def is_configured(self) -> bool:
        return self.client is not None

    async def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user in Supabase."""
        if not self.client:
            return {
                "user": {"id": "mock-user-id", "email": email},
                "session": {"access_token": "mock-access-token-demo"},
                "message": "Demo mode: Supabase credentials not configured in .env"
            }

        try:
            response = self.client.auth.sign_up({"email": email, "password": password})
            return {
                "user": {
                    "id": response.user.id if response.user else None,
                    "email": response.user.email if response.user else email
                },
                "session": {
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None
                }
            }
        except Exception as e:
            logger.error(f"Supabase SignUp error: {e}")
            raise

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in an existing user with email and password."""
        if not self.client:
            return {
                "user": {"id": "mock-user-id", "email": email},
                "session": {"access_token": "mock-access-token-demo"},
                "message": "Demo mode: Signed in as mock user"
            }

        try:
            response = self.client.auth.sign_in_with_password({"email": email, "password": password})
            return {
                "user": {
                    "id": response.user.id if response.user else None,
                    "email": response.user.email if response.user else email
                },
                "session": {
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None
                }
            }
        except Exception as e:
            logger.error(f"Supabase SignIn error: {e}")
            raise

    async def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify an access token and return user details."""
        if not self.client:
            # In demo mode, accept any non-empty token
            if token.startswith("mock-") or not settings.REQUIRE_AUTH:
                return {"id": "guest_user", "email": "guest@Ocg-agent.local", "role": "authenticated"}
            return None

        try:
            # Fetch user info using the access token
            user_resp = self.client.auth.get_user(token)
            if user_resp and user_resp.user:
                return {
                    "id": user_resp.user.id,
                    "email": user_resp.user.email,
                    "role": user_resp.user.role or "authenticated",
                    "user_metadata": user_resp.user.user_metadata or {}
                }
            return None
        except Exception as e:
            logger.warning(f"Failed to verify JWT token with Supabase: {e}")
            return None

# Global instance
supabase_auth = SupabaseAuthManager()
