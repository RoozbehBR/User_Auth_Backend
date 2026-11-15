from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserCreate
from app.security import get_password_hash


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    # پیدا کردن کاربر بر اساس ایمیل (برای لاگین و چک کردن تکراری نبودن)
    database_query = select(User).where(User.email == email)
    result = await db.execute(database_query)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    # قبل از ذخیره، پسورد خام را هش می‌کنیم
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password # فقط هش را ذخیره می‌کنیم
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user