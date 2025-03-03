from fastapi import APIRouter


router = APIRouter(prefix="/tasks", tags=["Tasks 📚"])


@router.get(
    path="/",
)
async def get_all_tasks():
    pass


@router.post(
    path="/",
)
async def create_new_task():
    pass


@router.put(
    path="/{id}",
)
async def update_task(id: int):
    pass


@router.delete(
    path="/{id}",
)
async def delete_task(id: int):
    pass