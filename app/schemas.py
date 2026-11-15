from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field


# ==========================================
# ۱. قالب‌های کاربر
# ==========================================
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="پسورد باید حداقل ۸ کاراکتر باشد")

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ۲. قالب‌های توکن (JWT)
# ==========================================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None