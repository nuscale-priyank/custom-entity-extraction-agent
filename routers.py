"""
API routers for the BC3 AI Agent
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import List

from models import (
    ChatRequest, ChatResponse, EntityRequest, EntityResponse,
    CreateEntityRequest, UpdateEntityRequest, DeleteEntityRequest,
    AttributeRequest, CreateAttributeRequest, UpdateAttributeRequest, DeleteAttributeRequest,
    StandardResponse
)
from managers import EntityCollectionManager, ChatSessionManager
from entity_collection_models import (
    ReadEntityRequest, CreateEntityRequest as FirestoreCreateEntityRequest,
    UpdateEntityRequest as FirestoreUpdateEntityRequest, DeleteEntityRequest as FirestoreDeleteEntityRequest
)
from config import Config
from conversational_agent import ConversationalAgent

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize managers
entity_manager = EntityCollectionManager(Config.get_project_id(), database_id=Config.get_database_id())
conversational_agent = ConversationalAgent(Config.get_project_id())
chat_session_manager = ChatSessionManager(Config.get_project_id(), database_id=Config.get_database_id())


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for entity extraction"""
    try:
        logger.info(f"Chat request received - Session: {request.session_id}")
        logger.info(f"Message: {request.message}")
        logger.info(f"BC3 fields: {len(request.selected_bc3_fields)}")
        logger.info(f"Asset columns: {len(request.selected_asset_columns)}")
        
        # Import here to avoid circular imports
        from agent import SimpleAgent
        agent = SimpleAgent()
        
        # Process request
        result = agent.process_request(
            message=request.message,
            session_id=request.session_id,
            selected_bc3_fields=request.selected_bc3_fields,
            selected_asset_columns=request.selected_asset_columns
        )
        
        logger.info(f"Request processed - Success: {result['success']}, Entities: {result['entities_created']}")
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "simple"}


# Entity CRUD Operations

@router.get("/entities", response_model=EntityResponse)
async def read_entities(session_id: str, limit: int = 100, offset: int = 0):
    """Read entities for a session"""
    try:
        logger.info(f"Reading entities for session: {session_id}")
        
        request = ReadEntityRequest(
            session_id=session_id,
            limit=limit,
            offset=offset
        )
        
        response = entity_manager.read_entities(request)
        
        return EntityResponse(
            success=response.success,
            message=response.message,
            entities=[entity.model_dump(mode='json') for entity in response.entities],
            total_count=response.total_count
        )
        
    except Exception as e:
        logger.error(f"Error reading entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/entities", response_model=StandardResponse)
async def create_entity(request: CreateEntityRequest):
    """Create a new entity"""
    try:
        logger.info(f"Creating entity: {request.entity_name} for session: {request.session_id}")
        
        # Convert to Firestore request format
        firestore_request = FirestoreCreateEntityRequest(
            session_id=request.session_id,
            entities_data=[{
                "entity_name": request.entity_name,
                "entity_type": request.entity_type,
                "entity_value": request.entity_value,
                "description": request.description,
                "attributes": request.attributes
            }]
        )
        
        response = entity_manager.create_entities(firestore_request)
        
        return StandardResponse(
            success=response.success,
            message=response.message,
            data={"total_created": response.total_created}
        )
        
    except Exception as e:
        logger.error(f"Error creating entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/entities", response_model=StandardResponse)
async def update_entity(request: UpdateEntityRequest):
    """Update an existing entity"""
    try:
        logger.info(f"Updating entity: {request.entity_id} for session: {request.session_id}")
        
        # Convert to Firestore request format
        entity_data = {}
        if request.entity_name:
            entity_data["entity_name"] = request.entity_name
        if request.entity_type:
            entity_data["entity_type"] = request.entity_type
        if request.entity_value:
            entity_data["entity_value"] = request.entity_value
        if request.description:
            entity_data["description"] = request.description
        
        firestore_request = FirestoreUpdateEntityRequest(
            session_id=request.session_id,
            entity_id=request.entity_id,
            entity_data=entity_data
        )
        
        response = entity_manager.update_entities(firestore_request)
        
        return StandardResponse(
            success=response.success,
            message=response.message,
            data={"updated_entity": response.updated_entity.model_dump(mode='json') if response.updated_entity else None}
        )
        
    except Exception as e:
        logger.error(f"Error updating entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/entities", response_model=StandardResponse)
async def delete_entity(request: DeleteEntityRequest):
    """Delete an entity"""
    try:
        logger.info(f"Deleting entity: {request.entity_id} for session: {request.session_id}")
        
        # Convert to Firestore request format
        firestore_request = FirestoreDeleteEntityRequest(
            session_id=request.session_id,
            entity_id=request.entity_id,
            delete_all=False
        )
        
        response = entity_manager.delete_entities(firestore_request)
        
        return StandardResponse(
            success=response.success,
            message=response.message,
            data={
                "deleted_entities": response.deleted_entities,
                "deleted_attributes": response.deleted_attributes,
                "total_deleted": response.total_deleted
            }
        )
        
    except Exception as e:
        logger.error(f"Error deleting entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Attribute CRUD Operations

@router.get("/entities/{entity_id}/attributes", response_model=StandardResponse)
async def read_attributes(session_id: str, entity_id: str):
    """Read attributes for a specific entity"""
    try:
        logger.info(f"Reading attributes for entity: {entity_id} in session: {session_id}")
        
        # First get the entity
        entity_request = ReadEntityRequest(session_id=session_id)
        entity_response = entity_manager.read_entities(entity_request)
        
        # Find the specific entity
        target_entity = None
        for entity in entity_response.entities:
            if entity.entity_id == entity_id:
                target_entity = entity
                break
        
        if not target_entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return StandardResponse(
            success=True,
            message="Attributes retrieved successfully",
            data={
                "entity_id": entity_id,
                "attributes": [attr.model_dump(mode='json') for attr in target_entity.attributes]
            }
        )
        
    except Exception as e:
        logger.error(f"Error reading attributes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/entities/{entity_id}/attributes", response_model=StandardResponse)
async def create_attribute(entity_id: str, request: CreateAttributeRequest):
    """Create a new attribute for an entity"""
    try:
        logger.info(f"Creating attribute: {request.attribute_name} for entity: {entity_id}")
        
        # This would require extending the entity manager to support attribute operations
        # For now, return a placeholder response
        return StandardResponse(
            success=True,
            message="Attribute creation not yet implemented",
            data={"attribute_name": request.attribute_name}
        )
        
    except Exception as e:
        logger.error(f"Error creating attribute: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/entities/{entity_id}/attributes/{attribute_id}", response_model=StandardResponse)
async def update_attribute(entity_id: str, attribute_id: str, request: UpdateAttributeRequest):
    """Update an existing attribute"""
    try:
        logger.info(f"Updating attribute: {attribute_id} for entity: {entity_id}")
        
        # This would require extending the entity manager to support attribute operations
        # For now, return a placeholder response
        return StandardResponse(
            success=True,
            message="Attribute update not yet implemented",
            data={"attribute_id": attribute_id}
        )
        
    except Exception as e:
        logger.error(f"Error updating attribute: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/entities/{entity_id}/attributes/{attribute_id}", response_model=StandardResponse)
async def delete_attribute(entity_id: str, attribute_id: str, request: DeleteAttributeRequest):
    """Delete an attribute"""
    try:
        logger.info(f"Deleting attribute: {attribute_id} for entity: {entity_id}")
        
        # Use the delete_entities method with attribute_ids
        firestore_request = FirestoreDeleteEntityRequest(
            session_id=request.session_id,
            entity_id=entity_id,
            attribute_ids=[attribute_id],
            delete_all=False
        )
        
        response = entity_manager.delete_entities(firestore_request)
        
        return StandardResponse(
            success=response.success,
            message=response.message,
            data={
                "deleted_attributes": response.deleted_attributes,
                "total_deleted": response.total_deleted
            }
        )
        
    except Exception as e:
        logger.error(f"Error deleting attribute: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Conversational Agent Endpoints

@router.post("/conversation", response_model=ChatResponse)
async def conversation(request: ChatRequest, user_id: str = None):
    """Conversational endpoint for natural entity building (Now using LangGraph)"""
    try:
        # Use default user_id if not provided
        if user_id is None:
            user_id = Config.get_default_user_id()
        
        logger.info(f"Conversation request received - Session: {request.session_id}")
        logger.info(f"Message: {request.message}")
        logger.info(f"BC3 fields: {len(request.selected_bc3_fields)}")
        logger.info(f"Asset columns: {len(request.selected_asset_columns)}")
        logger.info(f"User ID: {user_id}")
        
        # Process with LangGraph-based conversational agent
        result = conversational_agent.process_message(
            session_id=request.session_id,
            user_message=request.message,
            selected_bc3_fields=request.selected_bc3_fields,
            selected_asset_columns=request.selected_asset_columns,
            user_id=user_id
        )
        
        logger.info(f"Conversation processed - Success: {result['success']}, Entities: {result['entities_created']}")
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{session_id}/history")
async def get_conversation_history(session_id: str, user_id: str = None, limit: int = None):
    """Get conversation history for a session (Now using LangGraph)"""
    try:
        # Use default values if not provided
        if user_id is None:
            user_id = Config.get_default_user_id()
        if limit is None:
            limit = Config.get_default_conversation_limit()
        
        logger.info(f"Getting conversation history for session: {session_id}, user: {user_id}")
        
        history = conversational_agent.get_conversation_history(session_id, user_id, limit)
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "messages": history,
            "total_messages": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{session_id}/summary")
async def get_session_summary(session_id: str, user_id: str = None):
    """Get session summary (Now using LangGraph)"""
    try:
        # Use default user_id if not provided
        if user_id is None:
            user_id = Config.get_default_user_id()
        
        logger.info(f"Getting session summary for: {session_id}, user: {user_id}")
        
        summary = conversational_agent.get_session_summary(session_id, user_id)
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting session summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation/{session_id}/context")
async def update_session_context(session_id: str, context_updates: dict):
    """Update session context with BC3 fields or asset columns"""
    try:
        logger.info(f"Updating context for session: {session_id}")
        
        success = chat_session_manager.update_context(session_id, context_updates)
        
        if success:
            return {"success": True, "message": "Context updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
        
    except Exception as e:
        logger.error(f"Error updating session context: {e}")
        raise HTTPException(status_code=500, detail=str(e))
