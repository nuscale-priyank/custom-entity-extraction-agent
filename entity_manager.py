"""
Entity Management System for CRUD operations on entities and attributes
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from models import (
    ExtractedEntity, EntityAttribute, ChatState, EntityType,
    ReadEntityRequest, ReadEntityResponse, DeleteEntityRequest, DeleteEntityResponse,
    UpdateEntityRequest, UpdateEntityResponse
)
from session_managers import SessionManager

logger = logging.getLogger(__name__)


class EntityManager:
    """Manages CRUD operations for entities and attributes"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    def _get_session(self, session_id: str) -> Optional[ChatState]:
        """Get session by ID"""
        return self.session_manager.get_session(session_id)
    
    def _save_session(self, session_id: str, chat_state: ChatState) -> bool:
        """Save session with updated state version"""
        chat_state.state_version += 1
        chat_state.last_updated = datetime.now()
        return self.session_manager.save_session(session_id, chat_state)
    
    def _generate_entity_id(self) -> str:
        """Generate unique entity ID"""
        return f"entity_{uuid.uuid4().hex[:8]}"
    
    def _generate_attribute_id(self) -> str:
        """Generate unique attribute ID"""
        return f"attr_{uuid.uuid4().hex[:8]}"
    
    def read_entities(self, request: ReadEntityRequest) -> ReadEntityResponse:
        """
        Read entities from a session with optional filtering.
        
        Args:
            request: ReadEntityRequest with session_id and optional filters
            
        Returns:
            ReadEntityResponse with entities and metadata
        """
        try:
            logger.info(f"🔍 Reading entities for session: {request.session_id}")
            
            # Get session
            chat_state = self._get_session(request.session_id)
            if not chat_state:
                return ReadEntityResponse(
                    entities=[],
                    state_version=0,
                    total_count=0,
                    success=False,
                    message=f"Session {request.session_id} not found"
                )
            
            # Filter entities
            entities = chat_state.extracted_entities
            
            # Filter by entity ID
            if request.entity_id:
                entities = [e for e in entities if e.entity_id == request.entity_id]
            
            # Filter by entity type
            if request.entity_type:
                entities = [e for e in entities if e.entity_type == request.entity_type]
            
            # Filter by state version
            if request.state_version:
                entities = [e for e in entities if e.state_version <= request.state_version]
            
            # Remove attributes if not requested
            if not request.include_attributes:
                for entity in entities:
                    entity.attributes = []
            
            logger.info(f"✅ Found {len(entities)} entities for session {request.session_id}")
            
            return ReadEntityResponse(
                entities=entities,
                state_version=chat_state.state_version,
                total_count=len(entities),
                success=True,
                message=f"Successfully retrieved {len(entities)} entities"
            )
            
        except Exception as e:
            logger.error(f"❌ Error reading entities: {e}")
            return ReadEntityResponse(
                entities=[],
                state_version=0,
                total_count=0,
                success=False,
                message=f"Error reading entities: {str(e)}"
            )
    
    def delete_entities(self, request: DeleteEntityRequest) -> DeleteEntityResponse:
        """
        Delete entities or attributes from a session.
        
        Args:
            request: DeleteEntityRequest with session_id and deletion criteria
            
        Returns:
            DeleteEntityResponse with deletion results
        """
        try:
            logger.info(f"🗑️ Deleting entities/attributes for session: {request.session_id}")
            
            # Get session
            chat_state = self._get_session(request.session_id)
            if not chat_state:
                return DeleteEntityResponse(
                    deleted_entities=[],
                    deleted_attributes=[],
                    state_version=0,
                    success=False,
                    message=f"Session {request.session_id} not found"
                )
            
            deleted_entities = []
            deleted_attributes = []
            
            if request.delete_all:
                # Delete all entities
                deleted_entities = [e.entity_id for e in chat_state.extracted_entities]
                chat_state.extracted_entities = []
                logger.info(f"🗑️ Deleted all {len(deleted_entities)} entities")
                
            elif request.entity_id:
                # Delete specific entity
                original_count = len(chat_state.extracted_entities)
                chat_state.extracted_entities = [
                    e for e in chat_state.extracted_entities if e.entity_id != request.entity_id
                ]
                if len(chat_state.extracted_entities) < original_count:
                    deleted_entities.append(request.entity_id)
                    logger.info(f"🗑️ Deleted entity: {request.entity_id}")
                else:
                    logger.warning(f"⚠️ Entity {request.entity_id} not found")
            
            elif request.attribute_ids:
                # Delete specific attributes from entities
                for entity in chat_state.extracted_entities:
                    original_attr_count = len(entity.attributes)
                    entity.attributes = [
                        attr for attr in entity.attributes 
                        if attr.attribute_id not in request.attribute_ids
                    ]
                    deleted_count = original_attr_count - len(entity.attributes)
                    if deleted_count > 0:
                        deleted_attributes.extend(request.attribute_ids[:deleted_count])
                        entity.updated_at = datetime.now()
                        entity.state_version += 1
                        logger.info(f"🗑️ Deleted {deleted_count} attributes from entity {entity.entity_id}")
            
            # Save updated session
            if self._save_session(request.session_id, chat_state):
                logger.info(f"✅ Successfully saved session {request.session_id}")
                return DeleteEntityResponse(
                    deleted_entities=deleted_entities,
                    deleted_attributes=deleted_attributes,
                    state_version=chat_state.state_version,
                    success=True,
                    message=f"Successfully deleted {len(deleted_entities)} entities and {len(deleted_attributes)} attributes"
                )
            else:
                return DeleteEntityResponse(
                    deleted_entities=[],
                    deleted_attributes=[],
                    state_version=0,
                    success=False,
                    message="Failed to save session after deletion"
                )
                
        except Exception as e:
            logger.error(f"❌ Error deleting entities: {e}")
            return DeleteEntityResponse(
                deleted_entities=[],
                deleted_attributes=[],
                state_version=0,
                success=False,
                message=f"Error deleting entities: {str(e)}"
            )
    
    def update_entities(self, request: UpdateEntityRequest) -> UpdateEntityResponse:
        """
        Update entities or their attributes.
        
        Args:
            request: UpdateEntityRequest with session_id and update data
            
        Returns:
            UpdateEntityResponse with updated entity
        """
        try:
            logger.info(f"✏️ Updating entity {request.entity_id} for session: {request.session_id}")
            
            # Get session
            chat_state = self._get_session(request.session_id)
            if not chat_state:
                return UpdateEntityResponse(
                    updated_entity=None,
                    state_version=0,
                    success=False,
                    message=f"Session {request.session_id} not found"
                )
            
            # Find entity to update
            entity_to_update = None
            entity_index = -1
            for i, entity in enumerate(chat_state.extracted_entities):
                if entity.entity_id == request.entity_id:
                    entity_to_update = entity
                    entity_index = i
                    break
            
            if not entity_to_update:
                # Create new entity if it doesn't exist
                logger.info(f"➕ Creating new entity {request.entity_id} as it doesn't exist")
                entity_to_update = ExtractedEntity(
                    entity_id=request.entity_id,
                    entity_type=EntityType.METADATA,
                    entity_name="New Entity",
                    entity_value="",
                    confidence=0.8,
                    source_field="system",
                    description="Newly created entity",
                    relationships={},
                    context_provider="credit_domain",
                    attributes=[],
                    state_version=1
                )
                chat_state.extracted_entities.append(entity_to_update)
                entity_index = len(chat_state.extracted_entities) - 1
            
            # Update entity fields
            if request.entity_updates:
                for field, value in request.entity_updates.items():
                    if hasattr(entity_to_update, field):
                        setattr(entity_to_update, field, value)
                        logger.info(f"✏️ Updated entity field {field} to {value}")
            
            # Update attributes
            if request.attribute_updates:
                for attr_update in request.attribute_updates:
                    attr_id = attr_update.get('attribute_id')
                    if not attr_id:
                        # Create new attribute
                        new_attr = EntityAttribute(
                            attribute_id=self._generate_attribute_id(),
                            attribute_name=attr_update.get('attribute_name', ''),
                            attribute_value=attr_update.get('attribute_value', ''),
                            attribute_type=attr_update.get('attribute_type', 'string'),
                            confidence=attr_update.get('confidence', 0.8),
                            source_field=attr_update.get('source_field', ''),
                            description=attr_update.get('description', ''),
                            metadata=attr_update.get('metadata', {})
                        )
                        entity_to_update.attributes.append(new_attr)
                        logger.info(f"➕ Added new attribute: {new_attr.attribute_name}")
                    else:
                        # Update existing attribute
                        for attr in entity_to_update.attributes:
                            if attr.attribute_id == attr_id:
                                for field, value in attr_update.items():
                                    if field != 'attribute_id' and hasattr(attr, field):
                                        setattr(attr, field, value)
                                attr.updated_at = datetime.now()
                                logger.info(f"✏️ Updated attribute {attr_id}")
                                break
            
            # Update entity metadata
            entity_to_update.updated_at = datetime.now()
            entity_to_update.state_version += 1
            
            # Replace entity in session
            chat_state.extracted_entities[entity_index] = entity_to_update
            
            # Save updated session
            if self._save_session(request.session_id, chat_state):
                logger.info(f"✅ Successfully updated entity {request.entity_id}")
                return UpdateEntityResponse(
                    updated_entity=entity_to_update,
                    state_version=chat_state.state_version,
                    success=True,
                    message=f"Successfully updated entity {request.entity_id}"
                )
            else:
                return UpdateEntityResponse(
                    updated_entity=None,
                    state_version=chat_state.state_version,
                    success=False,
                    message="Failed to save session after update"
                )
                
        except Exception as e:
            logger.error(f"❌ Error updating entity: {e}")
            return UpdateEntityResponse(
                updated_entity=None,
                state_version=0,
                success=False,
                message=f"Error updating entity: {str(e)}"
            )
    
    def create_entity_with_attributes(self, session_id: str, entity_data: Dict[str, Any], attributes_data: List[Dict[str, Any]] = None) -> ExtractedEntity:
        """
        Create a new entity with attributes and add it to the session.
        
        Args:
            session_id: Session ID to add entity to
            entity_data: Entity data dictionary
            attributes_data: List of attribute data dictionaries
            
        Returns:
            Created ExtractedEntity
        """
        try:
            logger.info(f"➕ Creating new entity for session: {session_id}")
            
            # Get session
            chat_state = self._get_session(session_id)
            if not chat_state:
                raise ValueError(f"Session {session_id} not found")
            
            # Create attributes
            attributes = []
            if attributes_data:
                for attr_data in attributes_data:
                    attribute = EntityAttribute(
                        attribute_id=self._generate_attribute_id(),
                        attribute_name=attr_data.get('attribute_name', ''),
                        attribute_value=attr_data.get('attribute_value', ''),
                        attribute_type=attr_data.get('attribute_type', 'string'),
                        confidence=attr_data.get('confidence', 0.8),
                        source_field=attr_data.get('source_field', ''),
                        description=attr_data.get('description', ''),
                        metadata=attr_data.get('metadata', {})
                    )
                    attributes.append(attribute)
            
            # Create entity
            entity = ExtractedEntity(
                entity_id=self._generate_entity_id(),
                entity_type=entity_data.get('entity_type', EntityType.METADATA),
                entity_name=entity_data.get('entity_name', ''),
                entity_value=entity_data.get('entity_value', ''),
                confidence=entity_data.get('confidence', 0.8),
                source_field=entity_data.get('source_field', ''),
                description=entity_data.get('description', ''),
                relationships=entity_data.get('relationships', {}),
                context_provider=entity_data.get('context_provider', 'credit_domain'),
                attributes=attributes,
                metadata=entity_data.get('metadata', {})
            )
            
            # Add to session
            chat_state.extracted_entities.append(entity)
            
            # Save session
            if self._save_session(session_id, chat_state):
                logger.info(f"✅ Successfully created entity {entity.entity_id}")
                return entity
            else:
                raise Exception("Failed to save session after creating entity")
                
        except Exception as e:
            logger.error(f"❌ Error creating entity: {e}")
            raise
