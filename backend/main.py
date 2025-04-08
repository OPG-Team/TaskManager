import redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from auth.router import router as router_auth
from config import FRONTEND_URL_ARRAY, REDIS_URL
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
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
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
    allow_origins=FRONTEND_URL_ARRAY,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)
