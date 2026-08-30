"""
Main FastAPI application for SIH Compliance Checker
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from app.config import settings
from app.database import engine, Base
from app.models import User, Scan, Image, OCRResult, ExtractedField, ComplianceResult
from app.api.routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="AI-assisted compliance checker for packaged commodities"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(f"Starting SIH Compliance Checker API (env: {settings.environment})")
    logger.info(f"Database: {settings.database_url}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down SIH Compliance Checker API")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
