"""
Tools for the BC3 AI Agent
"""

import json
import logging
from typing import List
from langchain_core.tools import tool

from entity_collection_manager import EntityCollectionManager
from entity_collection_models import CreateEntityRequest
from config import Config

logger = logging.getLogger(__name__)


@tool
def create_entities(session_id: str, entities_data: str) -> str:
    """
    Create entities in Firestore.
    
    Args:
        session_id: Session ID
        entities_data: JSON string with entities to create
    
    Returns:
        JSON string with creation results
    """
    try:
        logger.info(f"Creating entities for session: {session_id}")
        
        # Parse entities data
        entities = json.loads(entities_data)
        logger.info(f"Parsed {len(entities)} entities")
        
        # Create request
        request = CreateEntityRequest(
            session_id=session_id,
            entities_data=entities
        )
        
        # Create entities
        manager = EntityCollectionManager(Config.get_project_id(), database_id=Config.get_database_id())
        response = manager.create_entities(request)
        
        logger.info(f"Created {response.total_created} entities")
        
        return json.dumps({
            "success": response.success,
            "total_created": response.total_created,
            "message": response.message,
            "entities": [entity.model_dump(mode='json') for entity in response.created_entities]
        })
        
    except Exception as e:
        logger.error(f"Error creating entities: {e}")
        return json.dumps({
            "success": False,
            "total_created": 0,
            "message": f"Error: {str(e)}",
            "entities": []
        })


def get_all_tools() -> List:
    """Get all available tools"""
    return [create_entities]
