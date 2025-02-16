from typing import Optional
from fastapi import FastAPI
import asyncpg
import os

DB_USER = os.getenv("DATABASE_USER")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_NAME = os.getenv("DATABASE_NAME")
DB_PORT = os.getenv("DATABASE_PORT")
DB_HOST = os.getenv("DATABASE_HOST")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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


# Create Single Instance of DatabaseConnector
db_connector = DatabaseConnector(DATABASE_URL)

async def get_db(app: FastAPI):
    return db_connector