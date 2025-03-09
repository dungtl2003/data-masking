from fastapi import APIRouter


api_router = APIRouter(prefix="/health")


@api_router.get("/")
async def health():
    return {"status": "ok"}
