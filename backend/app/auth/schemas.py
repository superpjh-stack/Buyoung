from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from uuid import UUID


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    OPERATOR = "OPERATOR"
    INSPECTOR = "INSPECTOR"


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserOut"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    user_id: UUID
    username: str
    role: UserRole
    department: Optional[str] = None

    model_config = {"from_attributes": True}


TokenResponse.model_rebuild()
