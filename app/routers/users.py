from fastapi import APIRouter, Depends, HTTPException, status as http_status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.crud import create_user, get_user_by_email
from app.database import get_db
from app.schemas import UserCreate, UserResponse, Token
from app.security import verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=http_status.HTTP_201_CREATED)
async def register_new_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # چک می‌کنیم آیا ایمیل تکراری است یا نه
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="این ایمیل قبلاً ثبت‌نام کرده است")
    
    return await create_user(db, user_data)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    # پیدا کردن کاربر
    user = await get_user_by_email(db, form_data.username)
    
    # چک کردن پسورد (اگر کاربر وجود نداشت یا پسورد اشتباه بود)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="ایمیل یا پسورد اشتباه است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ساخت توکن با زمان انقضا
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.email, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user_email: str = Depends(get_current_user), # ← این API را قفل می‌کند
    db: AsyncSession = Depends(get_db)
):
    # گرفتن اطلاعات کاربری که لاگین کرده است
    user = await get_user_by_email(db, current_user_email)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر پیدا نشد")
    return user