from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt  # PyJWT
import os

# These would be in .env
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "your-secret-here")

# ---------------------------------------------------------------------------
# AUTH DISABLED (temporary, at user's request, for test-phase development).
#
# Every route that previously required a valid Supabase JWT now gets a fixed
# fake "admin" user instead of actually checking anything. No token is
# required on any request. This is NOT safe for anything but local/private
# testing - re-enable real verification (see the commented-out version
# below) before this app has real users or real student data in it.
# ---------------------------------------------------------------------------

security = HTTPBearer(auto_error=False)

_FAKE_USER = {
    "sub": "00000000-0000-0000-0000-000000000000",
    "aud": "authenticated",
    "role": "authenticated",
    "app_metadata": {"role": "admin"},
}


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return _FAKE_USER


def role_required(allowed_roles: list[str]):
    async def role_checker(user: dict = Depends(get_current_user)):
        return user
    return role_checker


# Convenience dependencies
def admin_only(user: dict = Depends(role_required(["admin"]))):
    return user


def teacher_or_admin(user: dict = Depends(role_required(["admin", "teacher"]))):
    return user


# ---------------------------------------------------------------------------
# Real implementation, kept here so it's a one-line swap to turn auth back
# on later: replace get_current_user/role_required above with this.
# ---------------------------------------------------------------------------
#
# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
#     token = credentials.credentials
#     try:
#         payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
#
# def role_required(allowed_roles: list[str]):
#     async def role_checker(user: dict = Depends(get_current_user)):
#         user_role = user.get("app_metadata", {}).get("role", "student")
#         if user_role not in allowed_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Role {user_role} is not authorized to access this resource. Required: {allowed_roles}"
#             )
#         return user
#     return role_checker
