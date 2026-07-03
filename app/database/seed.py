import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.api.routers.auth import get_password_hash
from app.core.config import settings
from app.models.user import User

USERS_TO_SEED = [
    {
        "email": "admin@price-tracker.com",
        "password": settings.SEED_ADMIN_PASSWORD,
        "is_superuser": True,
        "is_active": True,
    },
    {
        "email": "user4@example.com",
        "password": settings.SEED_USER_PASSWORD,
        "is_superuser": False,
        "is_active": True,
    },
    {
        "email": "user5@example.com",
        "password": settings.SEED_USER_PASSWORD,
        "is_superuser": False,
        "is_active": True,
    },
]


async def seed_database():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        for user_data in USERS_TO_SEED:
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"User {user_data['email']} already exists. Updating password.")
                existing_user.hashed_password = get_password_hash(user_data["password"])
                continue

            new_user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                is_superuser=user_data["is_superuser"],
                is_active=user_data["is_active"],
            )
            session.add(new_user)
            print(f"Seeding user: {user_data['email']}")

        await session.commit()
        print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
