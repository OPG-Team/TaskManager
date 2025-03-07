from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as router_auth
from config import FRONTEND_URL
from tasks.router import router as router_tasks


app = FastAPI()

app.include_router(router_auth)
app.include_router(router_tasks)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)