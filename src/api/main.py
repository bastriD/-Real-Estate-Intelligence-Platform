from fastapi import FastAPI

from src.api.api.v1.router import api_router


app = FastAPI(
    title="Real Estate Intelligence API",
    description="Business API for the Chasse Immobiliere platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.include_router(api_router)
app.include_router(api_router, prefix="/api/v1")
