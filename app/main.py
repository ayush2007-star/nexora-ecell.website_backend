from contextlib import asynccontextmanager
from app.api.v1.activity import router as activity_router
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.notification import router as notification_router
from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.registration import router as registration_router
from app.api.v1.upload import router as upload_router
from app.config import settings
from app.core.exceptions import validation_exception_handler
from app.core.responses import ApiResponse
from app.database.indexes import create_indexes
from app.database.mongodb import connect_db, close_db
from app.api.v1.certificate import router as certificate_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    await create_indexes()
    print("🚀 Nexora Server Started")

    yield

    # Shutdown
    await close_db()
    print("🛑 Nexora Server Stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Later frontend URL yahan denge
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(certificate_router)
app.include_router(registration_router)
app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(admin_router)
app.include_router(notification_router)
app.include_router(activity_router)
app.mount(
    "/uploads",
    StaticFiles(directory="app/uploads"),
    name="uploads"
)

# -----------------------------
# Root API
# -----------------------------
@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Welcome to Nexora Innovation Portal API 🚀",
        "version": settings.APP_VERSION
    }


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "connected",
        "project": settings.APP_NAME
    }


# -----------------------------
# API Version
# -----------------------------
@app.get("/api/v1")
async def api_version():
    return {
        "success": True,
        "message": "Nexora API v1 Running Successfully"
    }


# -----------------------------
# Temporary Test Endpoint
# -----------------------------
@app.get("/test")
async def test():
    return ApiResponse.success(
        message="Backend Working Perfectly",
        data={
            "project": "Nexora",
            "version": "1.0.0"
        }
    )