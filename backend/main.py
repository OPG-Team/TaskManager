from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as router_auth
from config import FRONTEND_URL, REDIS_URL
from redis_tool import RedisDB
from tasks.router import router as router_tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.redis = RedisDB(url=REDIS_URL)
    print("Redis ready")

    try:
        yield
    finally:
        await app.redis.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_tasks)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)