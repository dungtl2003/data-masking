from fastapi import APIRouter
from app.api.v1.persons.route import api_router as persons_router
from app.api.v1.auth.route import api_router as auth_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(persons_router)
api_router.include_router(auth_router)
