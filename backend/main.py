from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.llm_router import router as llm_router
from utility.DatabaseConnector import DatabaseConnector, DATABASE_URL
from contextlib import asynccontextmanager


db_connector = DatabaseConnector(DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_connector = db_connector
    try:
        await app.state.db_connector.connect()
        yield
    finally:
        await app.state.db_connector.disconnect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm_router, prefix="/api/llm", tags=["llm"])
