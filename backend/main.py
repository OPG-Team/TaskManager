import redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as router_auth
from config import FRONTEND_URL, REDIS_URL
from logger import app_logger
from redis_tool import RedisDB
from tasks.router import router as router_tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.redis = RedisDB(url=REDIS_URL)
        await app.redis.ping()
        app_logger.info("Redis connection established successfully")

        yield
    except (redis.ConnectionError, redis.TimeoutError) as e:
        app_logger.error(f"Redis connection failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Redis connection failed: {str(e)}"
        )
    finally:
        await app.redis.close()
        app_logger.info("Redis connection closed")


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