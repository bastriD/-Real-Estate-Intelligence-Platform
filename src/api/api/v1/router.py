from fastapi import APIRouter

from src.api.api.v1.endpoints.clients import router as clients_router
from src.api.api.v1.endpoints.health import router as health_router
from src.api.api.v1.endpoints.mandats import router as mandats_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(clients_router)
api_router.include_router(mandats_router)