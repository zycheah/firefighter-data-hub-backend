from fastapi import APIRouter

from app.api.v1.web_api.endpoints.gps_data import send_location_router
from app.api.v1.web_api.endpoints.auth import web_auth
from app.api.v1.web_api.endpoints.dashboard import dashboard
from app.api.v1.web_api.endpoints.download_file import export_table_router
from app.api.v1.web_api.endpoints.eventtable import event_table_router

web_api_router = APIRouter()

web_api_router.include_router(send_location_router, prefix="/data", tags=["gps-table"])
web_api_router.include_router(web_auth, prefix="/auth", tags=["web-auth"])
web_api_router.include_router(dashboard, prefix="/dashboard", tags=["dashboard", "dashboard-summary"])
web_api_router.include_router(export_table_router, prefix="/table", tags=["table-export"])
web_api_router.include_router(event_table_router, prefix="/table", tags=["event-table"])