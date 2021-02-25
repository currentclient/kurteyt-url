"""
API

Setup api router, including routers from domains
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import shorturl

api_router = APIRouter()

api_router.include_router(shorturl.router, prefix="/shorten", tags=["shorturl"])
