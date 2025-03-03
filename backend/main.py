from fastapi import FastAPI
from auth.router import router as router_auth
from tasks.router import router as router_tasks


app = FastAPI()


app.include_router(router_auth)
app.include_router(router_tasks)