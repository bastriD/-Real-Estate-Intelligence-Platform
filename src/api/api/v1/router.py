from fastapi import APIRouter

from src.api.api.v1.endpoints.auth import router as auth_router
from src.api.api.v1.endpoints.biens import router as biens_router
from src.api.api.v1.endpoints.clients import router as clients_router
from src.api.api.v1.endpoints.demandes import router as demandes_router
from src.api.api.v1.endpoints.health import router as health_router
from src.api.api.v1.endpoints.mandats import router as mandats_router
from src.api.api.v1.endpoints.presentations import router as presentations_router
from src.api.api.v1.endpoints.recommendations import (
    router as recommendations_router,
)
from src.api.api.v1.endpoints.visites import router as visites_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(clients_router)
api_router.include_router(mandats_router)
api_router.include_router(demandes_router)
api_router.include_router(biens_router)
api_router.include_router(presentations_router)
api_router.include_router(recommendations_router)
api_router.include_router(visites_router)