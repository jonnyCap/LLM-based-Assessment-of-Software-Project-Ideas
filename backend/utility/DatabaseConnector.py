from fastapi import Request
from typing import Optional
import asyncpg
import os
import urllib.parse

# Load environment variables safely
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "app-db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_HOST = os.getenv("DB_HOST", "db")

# Encode password to handle special characters safely
DB_PASSWORD_ENCODED = urllib.parse.quote_plus(DB_PASSWORD)

# Construct the DATABASE_URL safely
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"Using database URL: {DATABASE_URL}")  # Debugging

class DatabaseConnector:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.database_url)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)


async def get_models_from_db(db: DatabaseConnector):
    # TODO: Load this on startup and cache it
    """Fetch available models from ENUM type in the database."""
    query = "SELECT unnest(enum_range(NULL::model_enum)) AS model_name"
    models = await db.fetch(query)
    return [model["model_name"] for model in models]


async def get_db(request: Request) -> DatabaseConnector:
    return request.app.state.db_connector