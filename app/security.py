from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings

# تنظیم الگوریتم هش کردن (bcrypt استانداردترین الگوریتم است)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# این ابزار به FastAPI می‌گوید که توکن را از کجای هدر (Authorization) بخواند
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def get_password_hash(plain_password: str) -> str:
    """تبدیل پسورد خام (مثل 123456) به پسورد هش‌شده"""
    return password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """چک کردن اینکه پسورد خام با پسورد هش‌شده توی دیتابیس مطابقت دارد یا نه"""
    return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """ساخت توکن JWT برای کاربر"""
    if expires_delta:
        expire_time = datetime.now(timezone.utc) + expires_delta
    else:
        expire_time = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # داده‌هایی که داخل توکن قرار می‌گیرند (sub یعنی شناسه کاربر، exp یعنی زمان انقضا)
    payload_to_encode = {"exp": expire_time, "sub": str(subject)}
    
    # امضای توکن با کلید مخفی (SECRET_KEY)
    encoded_jwt = jwt.encode(payload_to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """این تابع یک Dependency است که توکن را می‌خواند و ایمیل کاربر را برمی‌گرداند"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="اعتبار توکن تایید نشد",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # باز کردن توکن با کلید مخفی
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_email: str = payload.get("sub")
        
        if user_email is None:
            raise credentials_exception
        return user_email
        
    except JWTError:
        # اگر توکن دستکاری شده باشد یا منقضی شده باشد، این خطا را می‌دهیم
        raise credentials_exception