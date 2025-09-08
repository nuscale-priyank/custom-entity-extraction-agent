"""
Simplified FastAPI app with minimal complexity
"""

import logging
from fastapi import FastAPI

from config import Config
from routers import router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BC3 AI Agent - Entity Extraction and Management")

# Include routers
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
