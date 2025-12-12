"""
Agent Workflow Engine - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import router
# Import workflows to register tools
import app.workflows.code_review

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agent Workflow Engine",
    description="A minimal workflow/graph engine for executing agent workflows with nodes, edges, and state management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, tags=["Workflow Engine"])


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Agent Workflow Engine starting up...")
    logger.info("Tools registered and ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Agent Workflow Engine shutting down...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agent Workflow Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
