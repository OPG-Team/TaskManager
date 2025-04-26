import redis
import smtplib
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from auth.router import router as router_auth
from logger import app_logger
from redis_tool import RedisTools
from smtp import SmtpTools
from tasks.router import router as router_tasks
from res_passwd.router import router as router_res_passwd
from config import (
    FRONTEND_URL_ARRAY,
    REDIS_URL,
    SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.redis = RedisTools(url=REDIS_URL)
        await app.redis.ping()
        app_logger.info("Redis connection established successfully")

        app.smtp = SmtpTools(SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD)
        await app.smtp.ping()
        app_logger.info("SMTP connection established successfully")

        yield
    except (redis.ConnectionError, redis.TimeoutError) as e:
        app_logger.error(f"Redis connection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis connection failed: {str(e)}"
        )
    except smtplib.SMTPException as e:
        app_logger.error(f"SMTP connection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"SMTP connection failed: {str(e)}"
        )
    except Exception as e:
        app_logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        await app.redis.close()
        app_logger.info("Redis connection closed")

        await app.smtp.__del__()
        app_logger.info("SMTP connection closed")


app = FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_tasks)
app.include_router(router_res_passwd)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URL_ARRAY,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)
