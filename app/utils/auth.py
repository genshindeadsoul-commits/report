from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt # PyJWT
import os

# These would be in .env
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "your-secret-here")

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Extracts and verifies the Supabase JWT to identify the user.
    """
    token = credentials.credentials
    try:
        # In a real Supabase environment, the secret is the JWT Secret from the dashboard
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
        return payload # Contains 'sub' (the user UUID)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

def role_required(allowed_roles: list[str]):
    """
    Dependency factory that restricts access to specific roles.
    Expects a 'role' claim in the JWT or a database lookup in the profiles table.
    """
    async def role_checker(user: dict = Depends(get_current_user)):
        # Ideally, we'd query the 'profiles' table in the DB here.
        # For this implementation, we assume the role is encoded in the JWT metadata
        # as set by the handle_new_user trigger and Supabase auth.
        user_role = user.get("app_metadata", {}).get("role", "student")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user_role} is not authorized to access this resource. Required: {allowed_roles}"
            )
        return user

    return role_checker

# Convenience dependencies
def admin_only(user: dict = Depends(role_required(["admin"]))):
    return user

def teacher_or_admin(user: dict = Depends(role_required(["admin", "teacher"]))):
    return user
