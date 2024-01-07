import os

from dotenv import load_dotenv
from starlette.staticfiles import StaticFiles

from health.app.ws.socket_manager import SocketManager

load_dotenv()

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from health.api.v1.api import main_api_router
from health.core import settings


# Function to set up middleware
def setup_middleware(app):
    """
    Configure middleware settings for the FastAPI app.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Function to set up static files
def setup_static_files(app):
    """
    Configure static file directories for the FastAPI app.
    """
    os.makedirs("health/static/images", exist_ok=True)
    app.mount(
        "/health/static",
        StaticFiles(directory="health/static"),
        name="static",
    )


# Load environment variables
load_dotenv()

# Initialize the FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    root_path=settings.APP_ROOT_PATH,
)


@app.get("/api/health", response_model=dict)
async def health_check():
    return {"status": "healthy"}


# Setup Middleware
setup_middleware(app)

# Setup Static Files
setup_static_files(app)

# Include the main API router
app.include_router(main_api_router, prefix=settings.API_V1_STR)

sio = SocketManager(app=app)
