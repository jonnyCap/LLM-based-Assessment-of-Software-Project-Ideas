from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.llm_router import router as llm_router
from utility.DatabaseConnector import get_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_connector = await get_db(app)
    try:
        await db_connector.connect()
        yield db_connector
    finally:
        await db_connector.disconnect()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm_router, prefix="/api/llm", tags=["llm"])



@app.get("/api/hello-world")
def read_root():
    return {"message": "Hello, FastAPI!"}
