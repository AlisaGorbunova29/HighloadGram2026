from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import master_engine
from app.models import Base
from app.clickhouse_client import ch_client
from app.routers import channels, messages, analytics, users
from app.services import analytics_job


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with master_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    ch_client.connect()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(analytics_job.update_analytics, "interval", minutes=1)
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(title="Messenger API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(channels.router, prefix="/channels", tags=["channels"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


@app.get("/health")
async def health():
    return {"status": "ok"}
