from contextlib import asynccontextmanager
from pathlib import Path
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.management import router as management_router
from app.api.v1.activity import router as activity_router
from app.api.v1.admin import router as admin_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.auth import router as auth_router
from app.api.v1.certificate import router as certificate_router
from app.api.v1.event import router as event_router
from app.api.v1.notification import router as notification_router
from app.api.v1.participant import router as participant_router
from app.api.v1.registration import router as registration_router
from app.api.v1.scoring import router as scoring_router
from app.api.v1.upload import router as upload_router

from app.config import settings
from app.core.exceptions import validation_exception_handler
from app.database.indexes import create_indexes
from app.database.mongodb import connect_db, close_db, mongodb


logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
CERTIFICATES_DIR = BASE_DIR / "certificates"


# ---------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.

    Startup:
        1. Ensure required storage directories exist.
        2. Connect to MongoDB (with SSL/certifi support).
        3. Create MongoDB indexes safely.

    Shutdown:
        1. Close MongoDB connection.
    """

    try:
        # ---------------------------------------------
        # Prepare filesystem
        # ---------------------------------------------

        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        (UPLOADS_DIR / "profile").mkdir(parents=True, exist_ok=True)
        (UPLOADS_DIR / "pitchdeck").mkdir(parents=True, exist_ok=True)
        (UPLOADS_DIR / "images").mkdir(parents=True, exist_ok=True)
        CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("Upload and certificate directories verified.")

        # ---------------------------------------------
        # Connect database
        # ---------------------------------------------

        await connect_db()

        # ---------------------------------------------
        # Seed Super Admin and Default Events
        # ---------------------------------------------

        try:
            from app.database.seed import seed_admin_user, seed_default_events, seed_mentor_users
            await seed_mentor_users()
            await seed_default_events()
        except Exception as seed_err:
            logger.warning("Database seeding notice: %s", seed_err)

        # ---------------------------------------------
        # Create indexes
        # ---------------------------------------------

        try:
            await create_indexes()
            logger.info("MongoDB indexes verified.")
        except Exception as idx_err:
            logger.warning("MongoDB index creation notice: %s", idx_err)

        logger.info("Nexora server started successfully.")

        yield

    except Exception:
        logger.exception("Application startup failed.")
        raise

    finally:
        # ---------------------------------------------
        # Close database
        # ---------------------------------------------

        try:
            await close_db()
            logger.info("MongoDB connection closed.")
        except Exception:
            logger.exception("Error while closing MongoDB connection.")


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Nexora Innovation Portal API. "
        "Backend services for authentication, registration, "
        "teams, projects, certificates, notifications and administration."
    ),
    debug=settings.DEBUG,
    lifespan=lifespan,
)
# ---------------------------------------------------------
# Validation exception handler
# ---------------------------------------------------------

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)


# ---------------------------------------------------------
# CORS (Production & Development Friendly)
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "https://nexora-ecell.netlify.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:4173",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# API Routes
# ---------------------------------------------------------

app.include_router(auth_router)
app.include_router(registration_router)
app.include_router(participant_router)
app.include_router(admin_router)
app.include_router(attendance_router)
app.include_router(scoring_router)
app.include_router(upload_router)
app.include_router(certificate_router)
app.include_router(event_router)
app.include_router(notification_router)
app.include_router(activity_router)
app.include_router(management_router)

# ---------------------------------------------------------
# Static uploads & certificates
# ---------------------------------------------------------

app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOADS_DIR)),
    name="uploads",
)


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get(
    "/",
    tags=["System"],
)
async def root():
    return {
        "success": True,
        "message": "Welcome to Nexora Innovation Portal API.",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


# ---------------------------------------------------------
# Health Check (Used by Render / Cloud monitors)
# ---------------------------------------------------------

@app.get(
    "/health",
    tags=["System"],
)
async def health():
    """
    Health check endpoint for Render, container orchestrators, and uptime monitors.
    """
    db_status = "disconnected"
    try:
        if mongodb.client is not None:
            await mongodb.client.admin.command("ping")
            db_status = "connected"
    except Exception as e:
        db_status = f"unreachable ({str(e)})"

    return {
        "success": True,
        "status": "healthy",
        "database": db_status,
        "project": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": getattr(settings, "ENVIRONMENT", "production"),
    }


# ---------------------------------------------------------
# API Version
# ---------------------------------------------------------

@app.get(
    "/api/v1",
    tags=["System"],
)
async def api_version():
    return {
        "success": True,
        "message": "Nexora API v1 is running successfully.",
        "version": "v1",
    }