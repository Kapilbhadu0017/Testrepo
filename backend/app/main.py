import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your route modules
from app.routes import aqi, suggest, map

# Create FastAPI app instance
app = FastAPI(
    title="VayuCheck+ API",
    description="AI-Powered Air Quality Index monitoring and health suggestions API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Get CORS origins from environment
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers for different endpoints
app.include_router(aqi.router, prefix="/aqi", tags=["aqi"])
app.include_router(suggest.router, prefix="/suggest", tags=["suggestions"])
app.include_router(map.router, prefix="", tags=["map"])

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "VayuCheck+ API is running successfully!",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs",
        "developer": "KAPIL CHOUDHARY"
    }

# Health check endpoint
@app.get("/status")
def health_check():
    return {"status": "ok", "service": "VayuCheck+ API"}

# API info endpoint
@app.get("/info")
def api_info():
    return {
        "name": "VayuCheck+ API",
        "version": "1.0.0",
        "description": "AI-Powered Air Quality & Health Companion API",
        "endpoints": {
            "aqi": "/aqi", 
            "suggestions": "/suggest",
        },
        "developer": "KAPIL CHOUDHARY"
    }