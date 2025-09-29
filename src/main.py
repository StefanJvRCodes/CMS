"""Main FastAPI application for the CMS Event-Driven System."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.cms.api.routes import router as api_router
from src.cms.events.connection import rabbitmq_connection
from config.settings import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info("Starting CMS Event-Driven System...")
    
    # Initialize RabbitMQ connection
    if rabbitmq_connection.connect():
        logger.info("RabbitMQ connection established")
    else:
        logger.warning("Failed to connect to RabbitMQ - some features may not work")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CMS Event-Driven System...")
    rabbitmq_connection.disconnect()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Event-driven Content Management System with RabbitMQ and n8n integration",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1", tags=["CMS API"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the CMS Event-Driven System",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/info")
async def info():
    """System information endpoint."""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "rabbitmq_status": "connected" if rabbitmq_connection.is_connected() else "disconnected",
        "n8n_webhook_url": settings.n8n_webhook_url,
        "debug_mode": settings.debug
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )