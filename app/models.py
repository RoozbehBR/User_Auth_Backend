from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    # ما پسورد خام (مثل 123456) رو ذخیره نمی‌کنیم! فقط نسخه هش‌شده رو ذخیره می‌کنیم
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # وضعیت فعال بودن کاربر (اگر False بشه، نمی‌تونه لاگین کنه)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )