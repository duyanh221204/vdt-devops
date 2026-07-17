from sqlalchemy import select

from configuration.authentication import hash_password
from configuration.database import AsyncSessionLocal
from enums.role import Role
from model.user import User


async def init():
    async with AsyncSessionLocal() as db:
        admin = await db.execute(select(User).where(User.username == 'admin'))
        if admin.scalar_one_or_none() is None:
            admin = User(
                username='admin',
                hashed_password=hash_password('admin'),
                role=Role.ADMIN.value
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)

        user = await db.execute(select(User).where(User.username == 'user'))
        if user.scalar_one_or_none() is None:
            user = User(
                username='user',
                hashed_password=hash_password('user'),
                role=Role.USER.value
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
