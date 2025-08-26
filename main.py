import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from agent import CustomEntityExtractionAgent
from models import (
    AgentRequest, AgentResponse, HealthResponse, 
    BC3Segment, GenericDocument, ChatMessage
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Custom Entity Extraction Agent API",
    description="AI Agent for extracting custom entities from various data structures using LangGraph and Vertex AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[CustomEntityExtractionAgent] = None


def get_agent() -> CustomEntityExtractionAgent:
    """Get or create the agent instance"""
    global agent
    if agent is None:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_CLOUD_PROJECT environment variable not set"
            )
        
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        agent = CustomEntityExtractionAgent(project_id=project_id, location=location)
        logger.info(f"Initialized CustomEntityExtractionAgent with project: {project_id}")
    
    return agent


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    try:
        get_agent()
        logger.info("Custom Entity Extraction Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.post("/extract-entities", response_model=AgentResponse)
async def extract_entities(
    request: AgentRequest,
    agent: CustomEntityExtractionAgent = Depends(get_agent)
):
    """
    Extract custom entities from data structures
    
    This endpoint processes various types of data structures and extracts meaningful entities.
    Supports BC3 data, generic JSON documents, and other structured data formats.
    
    **Features:**
    - Entity extraction from multiple data types
    - Chat history maintenance
    - Context-aware analysis
    - Confidence scoring
    - Processing time tracking
    
    **Supported Context Providers:**
    - `bc3`: Business Credit Bureau data
    - `generic`: Generic JSON documents
    - `custom`: Custom data structures
    """
    try:
        logger.info(f"Processing entity extraction request for session: {request.session_id}")
        
        # Process the request
        response = agent.process_request(request)
        
        # Check for errors and return appropriate status code
        if response.metadata.get("has_error", False):
            logger.warning(f"Entity extraction completed with errors: {response.metadata.get('error_message', 'Unknown error')}")
            # Return response with 500 status code using FastAPI Response
            return Response(
                content=response.model_dump_json(),
                status_code=500,
                media_type="application/json"
            )
        else:
            logger.info(f"Successfully extracted {len(response.extracted_entities)} entities")
            return response
        
    except Exception as e:
        logger.error(f"Error processing entity extraction request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract entities: {str(e)}"
        )


@app.post("/extract-entities/bc3", response_model=AgentResponse)
async def extract_bc3_entities(
    request: AgentRequest,
    agent: CustomEntityExtractionAgent = Depends(get_agent)
):
    """
    Extract entities specifically from BC3 data structures
    
    This endpoint is optimized for BC3 (Business Credit Bureau) data analysis.
    It automatically sets the context provider to 'bc3' for specialized processing.
    
    **BC3 Data Structure:**
    - segment_name: Business segment identifier
    - data_dictionary: Array of field definitions with:
      - definition: Field description
      - bc3_field: Technical field identifier
      - description: Human-readable name
      - notes: Additional context
      - valid_values: Acceptable values
    """
    try:
        # Ensure context provider is set to bc3
        request.context_provider = "bc3"
        
        logger.info(f"Processing BC3 entity extraction request for session: {request.session_id}")
        
        # Process the request
        response = agent.process_request(request)
        
        # Check for errors and return appropriate status code
        if response.metadata.get("has_error", False):
            logger.warning(f"BC3 entity extraction completed with errors: {response.metadata.get('error_message', 'Unknown error')}")
            # Return response with 500 status code using FastAPI Response
            return Response(
                content=response.model_dump_json(),
                status_code=500,
                media_type="application/json"
            )
        else:
            logger.info(f"Successfully extracted {len(response.extracted_entities)} BC3 entities")
            return response
        
    except Exception as e:
        logger.error(f"Error processing BC3 entity extraction request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract BC3 entities: {str(e)}"
        )


@app.post("/extract-entities/generic", response_model=AgentResponse)
async def extract_generic_entities(
    request: AgentRequest,
    agent: CustomEntityExtractionAgent = Depends(get_agent)
):
    """
    Extract entities from generic data structures
    
    This endpoint processes generic JSON documents and other data structures.
    It automatically sets the context provider to 'generic' for flexible processing.
    
    **Supported Data Types:**
    - Nested JSON objects
    - Arrays and lists
    - Mixed data structures
    - Custom document formats
    """
    try:
        # Ensure context provider is set to generic
        request.context_provider = "generic"
        
        logger.info(f"Processing generic entity extraction request for session: {request.session_id}")
        
        # Process the request
        response = agent.process_request(request)
        
        # Check for errors and return appropriate status code
        if response.metadata.get("has_error", False):
            logger.warning(f"Generic entity extraction completed with errors: {response.metadata.get('error_message', 'Unknown error')}")
            # Return response with 500 status code using FastAPI Response
            return Response(
                content=response.model_dump_json(),
                status_code=500,
                media_type="application/json"
            )
        else:
            logger.info(f"Successfully extracted {len(response.extracted_entities)} generic entities")
            return response
        
    except Exception as e:
        logger.error(f"Error processing generic entity extraction request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract generic entities: {str(e)}"
        )


@app.get("/context-providers")
async def get_context_providers():
    """Get list of supported context providers"""
    return {
        "context_providers": [
            {
                "name": "bc3",
                "description": "Business Credit Bureau data structures",
                "features": ["Segment analysis", "Field extraction", "Value validation"]
            },
            {
                "name": "generic",
                "description": "Generic JSON documents and data structures",
                "features": ["Nested object analysis", "Array processing", "Type detection"]
            },
            {
                "name": "custom",
                "description": "Custom data structures",
                "features": ["Flexible processing", "Custom entity types", "Adaptive analysis"]
            }
        ]
    }


if __name__ == "__main__":
    import sys
    
    # Get port from command line argument or default to 8000
    port = 8000
    if len(sys.argv) > 1 and sys.argv[1] == "--port" and len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port number: {sys.argv[2]}")
            sys.exit(1)
    
    print(f"Starting Custom Entity Extraction Agent on port {port}")
    print(f"API Documentation: http://localhost:{port}/docs")
    print(f"Health Check: http://localhost:{port}/health")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
