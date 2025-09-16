"""
Entity Collection Manager for handling custom_entities collection in Firestore.
This manager handles all CRUD operations for entities separately from chat sessions.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from google.cloud import firestore

from models.entity_collection_models import (
    CustomEntity, EntityCollectionDocument, EntityAttribute,
    CreateEntityRequest, CreateEntityResponse,
    ReadEntityRequest, ReadEntityResponse,
    UpdateEntityRequest, UpdateEntityResponse,
    DeleteEntityRequest, DeleteEntityResponse,
    EntityType
)
from config import Config
from .relationship_detector import RelationshipDetector

logger = logging.getLogger(__name__)


class EntityCollectionManager:
    """Manages the custom_entities collection in Firestore"""
    
    def __init__(self, project_id: str, collection_name: str = None, database_id: str = None):
        """
        Initialize the Entity Collection Manager.
        
        Args:
            project_id: Google Cloud Project ID
            collection_name: Name of the Firestore collection for entities (defaults to config)
            database_id: Firestore database ID (defaults to config)
        """
        self.project_id = project_id
        self.collection_name = collection_name or Config.FIRESTORE_COLLECTION_CUSTOM_ENTITIES
        self.database_id = database_id or Config.get_database_id()
        self.db = firestore.Client(project=project_id, database=self.database_id)
        self.collection = self.db.collection(self.collection_name)
        self.relationship_detector = RelationshipDetector()
        
        logger.info(f"EntityCollectionManager initialized for project: {project_id}")
        logger.info(f"Using database: {self.database_id}")
        logger.info(f"Using collection: {self.collection_name}")
    
    def _get_entity_document(self, session_id: str) -> Optional[EntityCollectionDocument]:
        """Get the entity document for a session"""
        try:
            doc_ref = self.collection.document(session_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return EntityCollectionDocument(**data)
            else:
                # Create new document if it doesn't exist
                new_doc = EntityCollectionDocument(session_id=session_id)
                self._save_entity_document(session_id, new_doc)
                return new_doc
                
        except Exception as e:
            logger.error(f"❌ Error getting entity document for session {session_id}: {e}")
            return None
    
    def _save_entity_document(self, session_id: str, entity_doc: EntityCollectionDocument) -> bool:
        """Save the entity document to Firestore"""
        try:
            entity_doc.updated_at = datetime.now(timezone.utc)
            entity_doc.total_entities = len(entity_doc.entities)
            
            # Update last entity timestamps
            if entity_doc.entities:
                # Ensure all datetime objects are timezone-aware for comparison
                entity_created_times = []
                entity_updated_times = []
                
                for e in entity_doc.entities:
                    # Convert to timezone-aware if needed
                    created_at = e.created_at
                    updated_at = e.updated_at
                    
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=timezone.utc)
                    if updated_at.tzinfo is None:
                        updated_at = updated_at.replace(tzinfo=timezone.utc)
                    
                    entity_created_times.append(created_at)
                    entity_updated_times.append(updated_at)
                
                # Ensure document created_at is timezone-aware
                doc_created_at = entity_doc.created_at
                if doc_created_at.tzinfo is None:
                    doc_created_at = doc_created_at.replace(tzinfo=timezone.utc)
                
                entity_doc.last_entity_created = max(
                    entity_created_times, 
                    default=doc_created_at
                )
                entity_doc.last_entity_updated = max(
                    entity_updated_times, 
                    default=doc_created_at
                )
            
            data = entity_doc.model_dump()
            data["updated_at"] = firestore.SERVER_TIMESTAMP
            data["last_entity_created"] = firestore.SERVER_TIMESTAMP if entity_doc.last_entity_created else None
            data["last_entity_updated"] = firestore.SERVER_TIMESTAMP if entity_doc.last_entity_updated else None
            
            self.collection.document(session_id).set(data)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving entity document for session {session_id}: {e}")
            return False
    
    def create_entities(self, request: CreateEntityRequest) -> CreateEntityResponse:
        """
        Create new entities in the custom_entities collection.
        
        Args:
            request: CreateEntityRequest with session_id and entities data
            
        Returns:
            CreateEntityResponse with created entities
        """
        try:
            logger.info(f"➕ Creating entities for session: {request.session_id}")
            
            # Get existing entity document
            entity_doc = self._get_entity_document(request.session_id)
            if not entity_doc:
                return CreateEntityResponse(
                    created_entities=[],
                    total_created=0,
                    session_id=request.session_id,
                    success=False,
                    message="Failed to get or create entity document"
                )
            
            created_entities = []
            
            for entity_data in request.entities_data:
                try:
                    # Create attributes
                    attributes = []
                    if "attributes" in entity_data:
                        for attr_data in entity_data["attributes"]:
                            attribute = EntityAttribute(
                                attribute_name=attr_data.get("attribute_name", ""),
                                attribute_value=attr_data.get("attribute_value", ""),
                                attribute_type=attr_data.get("attribute_type", "string"),
                                confidence=attr_data.get("confidence", 0.8),
                                source_field=attr_data.get("source_field", ""),
                                description=attr_data.get("description", ""),
                                metadata=attr_data.get("metadata", {})
                            )
                            attributes.append(attribute)
                    
                    # Create entity
                    entity = CustomEntity(
                        session_id=request.session_id,
                        entity_type=EntityType(entity_data.get("entity_type", "METADATA")),
                        entity_name=entity_data.get("entity_name", ""),
                        entity_value=entity_data.get("entity_value", ""),
                        confidence=entity_data.get("confidence", 0.8),
                        source_field=entity_data.get("source_field", ""),
                        description=entity_data.get("description", ""),
                        relationships=entity_data.get("relationships", {}),
                        context_provider=entity_data.get("context_provider", "credit_domain"),
                        attributes=attributes,
                        metadata=entity_data.get("metadata", {}),
                        created_by=entity_data.get("created_by", "system")
                    )
                    
                    entity_doc.entities.append(entity)
                    created_entities.append(entity)
                    
                    logger.info(f"✅ Created entity: {entity.entity_name} (ID: {entity.entity_id})")
                    
                except Exception as e:
                    logger.error(f"❌ Error creating entity {entity_data.get('entity_name', 'unknown')}: {e}")
                    continue
            
            # Detect and update relationships
            if len(entity_doc.entities) > 1:
                self._detect_and_update_relationships(entity_doc)
            
            # Save the updated document
            if self._save_entity_document(request.session_id, entity_doc):
                logger.info(f"✅ Successfully created {len(created_entities)} entities for session {request.session_id}")
                return CreateEntityResponse(
                    created_entities=created_entities,
                    total_created=len(created_entities),
                    session_id=request.session_id,
                    success=True,
                    message=f"Successfully created {len(created_entities)} entities"
                )
            else:
                return CreateEntityResponse(
                    created_entities=[],
                    total_created=0,
                    session_id=request.session_id,
                    success=False,
                    message="Failed to save entities to Firestore"
                )
                
        except Exception as e:
            logger.error(f"❌ Error in create_entities: {e}")
            return CreateEntityResponse(
                created_entities=[],
                total_created=0,
                session_id=request.session_id,
                success=False,
                message=f"Error creating entities: {str(e)}"
            )
    
    def _detect_and_update_relationships(self, entity_doc: EntityCollectionDocument):
        """Detect and update relationships between entities"""
        try:
            logger.info(f"🔗 Detecting relationships between {len(entity_doc.entities)} entities")
            
            # Detect relationships
            relationships = self.relationship_detector.detect_relationships(entity_doc.entities)
            
            if relationships:
                # Update entities with relationship information
                for entity in entity_doc.entities:
                    if entity.entity_id in relationships:
                        entity = self.relationship_detector.update_entity_relationships(
                            entity, relationships[entity.entity_id]
                        )
                        logger.info(f"✅ Updated relationships for entity: {entity.entity_name}")
                
                logger.info(f"🔗 Successfully detected relationships for {len(relationships)} entities")
            else:
                logger.info("🔗 No relationships detected between entities")
                
        except Exception as e:
            logger.error(f"❌ Error detecting relationships: {e}")
            # Don't fail the entire operation if relationship detection fails
    
    def detect_relationships_for_session(self, session_id: str) -> bool:
        """Manually trigger relationship detection for all entities in a session"""
        try:
            logger.info(f"🔗 Manually detecting relationships for session: {session_id}")
            
            # Get the entity document
            entity_doc = self._get_entity_document(session_id)
            if not entity_doc or len(entity_doc.entities) < 2:
                logger.info(f"No entities or insufficient entities for relationship detection in session {session_id}")
                return False
            
            # Detect and update relationships
            self._detect_and_update_relationships(entity_doc)
            
            # Save the updated document
            if self._save_entity_document(session_id, entity_doc):
                logger.info(f"✅ Successfully updated relationships for session {session_id}")
                return True
            else:
                logger.error(f"❌ Failed to save relationship updates for session {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in manual relationship detection: {e}")
            return False
    
    def read_entities(self, request: ReadEntityRequest) -> ReadEntityResponse:
        """
        Read entities from the custom_entities collection.
        
        Args:
            request: ReadEntityRequest with session_id and optional filters
            
        Returns:
            ReadEntityResponse with entities
        """
        try:
            logger.info(f"🔍 Reading entities for session: {request.session_id}")
            
            entity_doc = self._get_entity_document(request.session_id)
            if not entity_doc:
                return ReadEntityResponse(
                    entities=[],
                    total_count=0,
                    session_id=request.session_id,
                    success=False,
                    message="Session not found"
                )
            
            entities = entity_doc.entities
            
            # Apply filters
            if request.entity_id:
                entities = [e for e in entities if e.entity_id == request.entity_id]
            
            if request.entity_type:
                entities = [e for e in entities if e.entity_type == request.entity_type]
            
            # Apply pagination
            total_count = len(entities)
            entities = entities[request.offset:request.offset + request.limit]
            
            logger.info(f"✅ Found {total_count} entities for session {request.session_id}")
            
            return ReadEntityResponse(
                entities=entities,
                total_count=total_count,
                session_id=request.session_id,
                success=True,
                message=f"Successfully retrieved {len(entities)} entities"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in read_entities: {e}")
            return ReadEntityResponse(
                entities=[],
                total_count=0,
                session_id=request.session_id,
                success=False,
                message=f"Error reading entities: {str(e)}"
            )
    
    def update_entities(self, request: UpdateEntityRequest) -> UpdateEntityResponse:
        """
        Update entities in the custom_entities collection.
        
        Args:
            request: UpdateEntityRequest with session_id, entity_id, and update data
            
        Returns:
            UpdateEntityResponse with updated entity
        """
        try:
            logger.info(f"✏️ Updating entity {request.entity_id} for session: {request.session_id}")
            
            entity_doc = self._get_entity_document(request.session_id)
            if not entity_doc:
                return UpdateEntityResponse(
                    updated_entity=None,
                    session_id=request.session_id,
                    success=False,
                    message="Session not found"
                )
            
            # Find the entity to update
            entity_to_update = None
            for i, entity in enumerate(entity_doc.entities):
                if entity.entity_id == request.entity_id:
                    entity_to_update = entity
                    break
            
            if not entity_to_update:
                return UpdateEntityResponse(
                    updated_entity=None,
                    session_id=request.session_id,
                    success=False,
                    message="Entity not found"
                )
            
            # Update entity fields
            for key, value in request.entity_data.items():
                if hasattr(entity_to_update, key) and key not in ['entity_id', 'created_at', 'session_id']:
                    setattr(entity_to_update, key, value)
            
            # Update attributes if provided
            if request.attribute_updates:
                for attr_update in request.attribute_updates:
                    attr_id = attr_update.get("attribute_id")
                    if attr_id:
                        # Update existing attribute
                        for attr in entity_to_update.attributes:
                            if attr.attribute_id == attr_id:
                                for key, value in attr_update.items():
                                    if hasattr(attr, key) and key != "attribute_id":
                                        setattr(attr, key, value)
                                attr.updated_at = datetime.now(timezone.utc)
                                break
                    else:
                        # Create new attribute
                        new_attr = EntityAttribute(
                            attribute_name=attr_update.get("attribute_name", ""),
                            attribute_value=attr_update.get("attribute_value", ""),
                            attribute_type=attr_update.get("attribute_type", "string"),
                            confidence=attr_update.get("confidence", 0.8),
                            source_field=attr_update.get("source_field", ""),
                            description=attr_update.get("description", ""),
                            metadata=attr_update.get("metadata", {})
                        )
                        entity_to_update.attributes.append(new_attr)
            
            entity_to_update.updated_at = datetime.now(timezone.utc)
            entity_to_update.version += 1
            
            # Save the updated document
            if self._save_entity_document(request.session_id, entity_doc):
                logger.info(f"✅ Successfully updated entity {request.entity_id}")
                return UpdateEntityResponse(
                    updated_entity=entity_to_update,
                    session_id=request.session_id,
                    success=True,
                    message="Entity updated successfully"
                )
            else:
                return UpdateEntityResponse(
                    updated_entity=None,
                    session_id=request.session_id,
                    success=False,
                    message="Failed to save updated entity"
                )
                
        except Exception as e:
            logger.error(f"❌ Error in update_entities: {e}")
            return UpdateEntityResponse(
                updated_entity=None,
                session_id=request.session_id,
                success=False,
                message=f"Error updating entity: {str(e)}"
            )
    
    def delete_entities(self, request: DeleteEntityRequest) -> DeleteEntityResponse:
        """
        Delete entities or attributes from the custom_entities collection.
        
        Args:
            request: DeleteEntityRequest with session_id and deletion criteria
            
        Returns:
            DeleteEntityResponse with deletion results
        """
        try:
            logger.info(f"🗑️ Deleting entities/attributes for session: {request.session_id}")
            
            entity_doc = self._get_entity_document(request.session_id)
            if not entity_doc:
                return DeleteEntityResponse(
                    deleted_entities=[],
                    deleted_attributes=[],
                    total_deleted=0,
                    session_id=request.session_id,
                    success=False,
                    message="Session not found"
                )
            
            deleted_entities = []
            deleted_attributes = []
            
            if request.delete_all:
                # Delete all entities
                deleted_entities = [e.entity_id for e in entity_doc.entities]
                entity_doc.entities = []
                
            elif request.entity_id:
                if request.attribute_ids:
                    # Delete specific attributes from entity
                    entity_to_update = None
                    for entity in entity_doc.entities:
                        if entity.entity_id == request.entity_id:
                            entity_to_update = entity
                            break
                    
                    if entity_to_update:
                        original_count = len(entity_to_update.attributes)
                        entity_to_update.attributes = [
                            attr for attr in entity_to_update.attributes 
                            if attr.attribute_id not in request.attribute_ids
                        ]
                        deleted_attributes = [
                            attr_id for attr_id in request.attribute_ids
                            if any(attr.attribute_id == attr_id for attr in entity_to_update.attributes)
                        ]
                        entity_to_update.updated_at = datetime.now(timezone.utc)
                else:
                    # Delete entire entity
                    entity_doc.entities = [
                        e for e in entity_doc.entities 
                        if e.entity_id != request.entity_id
                    ]
                    deleted_entities = [request.entity_id]
            
            # Save the updated document
            if self._save_entity_document(request.session_id, entity_doc):
                total_deleted = len(deleted_entities) + len(deleted_attributes)
                logger.info(f"✅ Successfully deleted {total_deleted} items")
                return DeleteEntityResponse(
                    deleted_entities=deleted_entities,
                    deleted_attributes=deleted_attributes,
                    total_deleted=total_deleted,
                    session_id=request.session_id,
                    success=True,
                    message=f"Successfully deleted {total_deleted} items"
                )
            else:
                return DeleteEntityResponse(
                    deleted_entities=[],
                    deleted_attributes=[],
                    total_deleted=0,
                    session_id=request.session_id,
                    success=False,
                    message="Failed to save deletion changes"
                )
                
        except Exception as e:
            logger.error(f"❌ Error in delete_entities: {e}")
            return DeleteEntityResponse(
                deleted_entities=[],
                deleted_attributes=[],
                total_deleted=0,
                session_id=request.session_id,
                success=False,
                message=f"Error deleting entities: {str(e)}"
            )
