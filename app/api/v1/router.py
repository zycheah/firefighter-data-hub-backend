from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.locations import router as locations_router
from app.api.v1.endpoints.files import router as files_router
from app.api.v1.endpoints.locationEntries import locationEntries_Router
from app.api.v1.endpoints import dataTransfer
from app.api.v1.endpoints.smoke_sampler import smoke_sampler_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)

# Keep this because frontend currently uses /api/v1/locationEntries/
api_router.include_router(
    locationEntries_Router,
    prefix="/locationEntries",
    tags=["locationEntries"],
)

# # Keep this optional newer route too
# api_router.include_router(
#     locations_router,
#     prefix="/locations",
#     tags=["locations"],
# )

api_router.include_router(
    files_router,
    prefix="/files",
    tags=["files"],
)

api_router.include_router(
    dataTransfer.router,
    prefix="/data-transfer",
    tags=["data-transfer"],
)

api_router.include_router(
    smoke_sampler_router,
    prefix="/smokeSampler",
    tags=["smokeSampler"],
)