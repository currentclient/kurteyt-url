"""
API

Main entrypoint to API
"""

from os import environ
from typing import Any, Dict, List, Optional

# from aws_xray_sdk.core import patch_all
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from starlette.requests import Request

from app.api.api_v1.api import api_public_router, api_router
from app.core.logger import get_logger
from app.core.security import JWTBearer
from app.core.settings import settings

IS_LOCAL: str = environ.get("IS_LOCAL", False)

# Setup x-ray
# if not IS_LOCAL:
#     patch_all()


LOGGER = get_logger(__name__)


# Set up tags details
tags_metadata: Optional[List[Dict[str, Any]]] = [
    {
        "name": "kurteyts",
        "description": "All the apis to create and manage a kurteyt. Create a kurteyt shell to start, and then proceed to add a clientform and contacts.",
    },
]

# Set up app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CurrentClient Kurteyts Microservice",
    version="1.0.0",
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
)

# Set up auth
auth = JWTBearer()

# Set up cors
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Set up routes
app.include_router(api_router, prefix=settings.API_V1_STR, dependencies=[Depends(auth)])
# Include public router
app.include_router(api_public_router, prefix=settings.API_V1_STR)


# Set up health check
@app.get("/health", tags=["health"])
def read_items(request: Request):
    """Health Check"""
    LOGGER.info("GET /health")

    # event = (
    #     request.scope["aws.event"]
    #     if request and request.get("aws") and request["aws.event"]
    #     else {}
    # )
    print(request)
    return {"health": "OK", "version": 1.0}


# Wrap in ASGI to deploy on lambda
handler = Mangum(app, enable_lifespan=False)
