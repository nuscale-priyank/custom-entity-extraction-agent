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
from entity_collection_manager import EntityCollectionManager
from entity_collection_models import (
    ReadEntityRequest, CreateEntityRequest as FirestoreCreateEntityRequest,
    UpdateEntityRequest as FirestoreUpdateEntityRequest, DeleteEntityRequest as FirestoreDeleteEntityRequest
)
from config import Config

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize entity manager
entity_manager = EntityCollectionManager(Config.get_project_id())


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
