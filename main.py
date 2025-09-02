import os
import sys
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from agent import CreditDomainEntityExtractionAgent
from models import (
    AgentRequest, AgentResponse, HealthResponse, 
    CreditDomainSegment, DataAsset, ChatState
)
from config import load_config_from_env, get_session_manager_kwargs
from session_managers import create_session_manager

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('fastapi.log')
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Add CORS middleware (will be added after app initialization)

# Global agent instance
agent: Optional[CreditDomainEntityExtractionAgent] = None


def get_agent() -> CreditDomainEntityExtractionAgent:
    """Get or create the agent instance"""
    global agent
    if agent is None:
        # Load configuration from environment
        agent_config, session_config, logging_config = load_config_from_env()
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, logging_config.level),
            format=logging_config.format,
            filename=logging_config.file_path
        )
        
        # Create session manager
        session_manager_kwargs = get_session_manager_kwargs(session_config)
        session_manager = create_session_manager(
            session_config.manager_type, 
            **session_manager_kwargs
        )
        
        # Initialize agent with configuration
        agent = CreditDomainEntityExtractionAgent(
            project_id=agent_config.project_id,
            location=agent_config.location,
            session_manager=session_manager
        )
        
        logger.info(f"Initialized CreditDomainEntityExtractionAgent with project: {agent_config.project_id}")
        logger.info(f"Using {session_config.manager_type} session manager")
    
    return agent


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI"""
    try:
        get_agent()
        logger.info("Credit Domain Entity Extraction Chat Agent initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Credit Domain Entity Extraction Chat Agent API",
    description="AI Chat Agent for extracting custom entities from Credit Domain data and data assets using LangGraph and Vertex AI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="2.0.0"
    )


@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(
    request: AgentRequest,
    agent: CreditDomainEntityExtractionAgent = Depends(get_agent)
):
    """
    Chat with the Credit Domain Entity Extraction Agent
    
    This endpoint provides a conversational interface for entity extraction.
    The agent will analyze selected BC3 fields and asset columns to extract
    relevant entities based on the user's request and selected context.
    
    **Features:**
    - Context-aware entity extraction
    - Individual BC3 field and asset column selection
    - Session management with state persistence
    - Intelligent entity relevance determination
    - LLM-driven entity extraction
    - Context combination analysis
    
    **Workflow:**
    1. User selects specific BC3 fields and asset columns
    2. User sends a message requesting entity extraction
    3. Agent analyzes the selected context combinations
    4. LLM determines relevant entities based on context
    5. Response includes extracted entities and analysis
    """
    try:
        start_time = time.time()
        
        logger.info(f"Chat request received - Session: {request.session_id}")
        logger.info(f"Message: {request.message[:100]}...")
        logger.info(f"Selected BC3 fields: {len(request.selected_bc3_fields or [])}")
        logger.info(f"Selected asset columns: {len(request.selected_asset_columns or [])}")
        
        # Process the request
        response = agent.process_request(request)
        
        processing_time = time.time() - start_time
        response.processing_time = processing_time
        
        logger.info(f"Chat request processed successfully - Time: {processing_time:.2f}s")
        logger.info(f"Extracted entities: {len(response.extracted_entities)}")
        
        # Enhanced entity logging
        if response.extracted_entities:
            logger.info("🔍 DETAILED ENTITY EXTRACTION RESULTS:")
            logger.info("=" * 60)
            
            for i, entity in enumerate(response.extracted_entities, 1):
                logger.info(f"📊 Entity #{i}:")
                logger.info(f"   Type: {entity.entity_type}")
                logger.info(f"   Name: {entity.entity_name}")
                logger.info(f"   Value: {entity.entity_value}")
                logger.info(f"   Confidence: {entity.confidence}")
                logger.info(f"   Source: {entity.source_field}")
                logger.info(f"   Description: {entity.description}")
                logger.info(f"   Context Provider: {entity.context_provider}")
                logger.info("   " + "-" * 40)
            
            logger.info("=" * 60)
            logger.info(f"✅ Total entities extracted: {len(response.extracted_entities)}")
        else:
            logger.warning("⚠️ No entities were extracted from the request")
        
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error processing chat request: {e}")
        logger.error(f"Processing time: {processing_time:.2f}s")
        
        # Return error response
        error_response = AgentResponse(
            response=f"Error processing request: {str(e)}",
            extracted_entities=[],
            chat_state=ChatState(
                session_id=request.session_id or "unknown",
                messages=[],
                selected_segments=[],
                selected_assets=[],
                selected_bc3_fields=[],
                selected_asset_columns=[],
                extracted_entities=[],
                metadata={"error": str(e)}
            ),
            metadata={
                "session_id": request.session_id,
                "processing_time": processing_time,
                "error": str(e),
                "timestamp": datetime.now()
            }
        )
        
        return JSONResponse(
            content=error_response.model_dump(),
            status_code=500
        )


@app.post("/chat/credit-domain", response_model=AgentResponse)
async def chat_with_credit_domain_data(
    request: AgentRequest,
    agent: CreditDomainEntityExtractionAgent = Depends(get_agent)
):
    """
    Chat with Credit Domain data specifically
    
    This endpoint is optimized for Credit Domain (BC3) data analysis.
    It automatically sets the context provider to 'credit_domain' for specialized processing.
    
    **Credit Domain Data Structure:**
    - segment_name: Business segment identifier
    - business_dictionary: Array of field definitions with:
      - uuid: Unique field identifier
      - known_implementations: Known implementation names
      - valid_values: Acceptable values
      - definition: Field description
      - notes: Additional context
      - description: Human-readable name
    """
    try:
        # Ensure context provider is set to credit_domain
        request.context_provider = "credit_domain"
        
        logger.info(f"Processing Credit Domain chat request for session: {request.session_id}")
        
        # Process the request
        response = agent.process_request(request)
        
        # Check for errors and return appropriate status code
        if response.metadata.get("error"):
            logger.warning(f"Credit Domain chat request completed with errors: {response.metadata.get('error', 'Unknown error')}")
            return Response(
                content=response.model_dump_json(),
                status_code=500,
                media_type="application/json"
            )
        else:
            logger.info(f"Successfully processed Credit Domain chat request with {len(response.extracted_entities)} entities")
            return response
        
    except Exception as e:
        logger.error(f"Error processing Credit Domain chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Credit Domain chat request: {str(e)}"
        )


@app.get("/sessions/{session_id}", response_model=ChatState)
async def get_session(
    session_id: str,
    agent: CreditDomainEntityExtractionAgent = Depends(get_agent)
):
    """
    Get session information by session ID
    
    Retrieve the current state of a chat session including:
    - Chat messages
    - Selected Credit Domain segments
    - Selected data assets
    - Extracted entities
    - Session metadata
    """
    try:
        session = agent.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve session: {str(e)}"
        )


@app.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    agent: CreditDomainEntityExtractionAgent = Depends(get_agent)
):
    """
    Delete a session by session ID
    
    Remove a chat session and all its associated data including:
    - Chat messages
    - Selected segments and assets
    - Extracted entities
    - Session metadata
    """
    try:
        deleted = agent.delete_session(session_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return {"message": f"Session {session_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


@app.get("/context-providers")
async def get_context_providers():
    """Get list of supported context providers"""
    return {
        "context_providers": [
            {
                "name": "credit_domain",
                "description": "Credit Domain (BC3) data structures with business dictionary",
                "features": ["Segment analysis", "Business dictionary extraction", "Field validation", "Implementation mapping"]
            },
            {
                "name": "data_assets",
                "description": "Data assets with column information and BigQuery integration",
                "features": ["Asset analysis", "Column extraction", "Workspace integration", "BigQuery table mapping"]
            },
            {
                "name": "generic",
                "description": "Generic data structures and documents",
                "features": ["Flexible processing", "Custom entity types", "Adaptive analysis"]
            }
        ]
    }

@app.get("/logs")
async def get_logs(lines: int = 50):
    """Get recent FastAPI logs"""
    try:
        log_file = "fastapi.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                # Get the last N lines
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return {
                    "log_file": log_file,
                    "total_lines": len(all_lines),
                    "recent_lines": recent_lines,
                    "timestamp": datetime.now().isoformat()
                }
        else:
            return {
                "log_file": log_file,
                "total_lines": 0,
                "recent_lines": [],
                "message": "Log file not found. Check terminal output for logs.",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/entities/{session_id}")
async def get_session_entities(
    session_id: str,
    agent: CreditDomainEntityExtractionAgent = Depends(get_agent)
):
    """Get extracted entities for a specific session in a clean, ordered format"""
    try:
        # Get the session
        session = agent.session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # Format entities for clean display
        formatted_entities = []
        for i, entity in enumerate(session.extracted_entities, 1):
            formatted_entity = {
                "entity_number": i,
                "entity_type": entity.entity_type,
                "entity_name": entity.entity_name,
                "entity_value": entity.entity_value,
                "confidence": entity.confidence,
                "source_field": entity.source_field,
                "description": entity.description,
                "context_provider": entity.context_provider
            }
            formatted_entities.append(formatted_entity)
        
        return {
            "session_id": session_id,
            "total_entities": len(formatted_entities),
            "entities": formatted_entities,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session entities: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session entities: {str(e)}"
        )


@app.get("/sessions")
async def list_sessions(
    agent: CreditDomainEntityExtractionAgent = Depends(get_agent)
):
    """List all active sessions"""
    try:
        sessions = list(agent.sessions.keys())
        return {
            "sessions": sessions,
            "total_sessions": len(sessions)
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sessions: {str(e)}"
        )


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
    
    print(f"Starting Credit Domain Entity Extraction Chat Agent on port {port}")
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
