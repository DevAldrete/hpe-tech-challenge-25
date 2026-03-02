import asyncio
import os

from src.storage.database import db
from src.storage.models import Base

# EnsureDATABASE_URL is set for script execution
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://aegis_user:aegis_secure_pass_2026@localhost:5432/aegis_db"
    )


async def init_models():
    print("Connecting to db...")
    db.connect()

    print("Creating tables...")
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully.")
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(init_models())
