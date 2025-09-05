"""
Tools for the Credit Domain Entity Extraction Agent

This module contains all the LangChain tools that the agent can use for:
- Entity extraction from BC3 segment data and data assets
- CRUD operations on entities (read, update, delete)
"""

import json
import logging
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool

from models import (
    ReadEntityRequest, DeleteEntityRequest, UpdateEntityRequest, EntityType
)
from agent import EntityExtractor

logger = logging.getLogger(__name__)


def create_extraction_tools(entity_extractor: EntityExtractor) -> List:
    """Create extraction tools for BC3 segment data and data assets"""
    
    @tool
    def extract_credit_domain_entities(segment_data: str) -> str:
        """
        Extract structured entities from Credit Domain (BC3) segment data.
        
        This tool analyzes BC3 segment data including business dictionary fields, 
        known implementations, valid values, and notes to extract meaningful entities
        with their attributes and relationships.
        
        Args:
            segment_data (str): JSON string containing BC3 segment data with fields:
                - segment_name: Name of the credit domain segment
                - business_dictionary: List of business dictionary fields with:
                    - uuid: Unique identifier
                    - description: Field description
                    - definition: Field definition
                    - known_implementations: List of known implementations
                    - valid_values: List of valid values
                    - notes: Additional notes
        
        Returns:
            str: JSON string containing extracted entities with:
                - entity_type: Type of entity (FIELD, SEGMENT, METADATA, VALUE)
                - entity_name: Name of the entity
                - entity_value: Value or description
                - confidence: Confidence score (0.0-1.0)
                - source_field: Source field identifier
                - description: Business significance
                - context_provider: Always "credit_domain"
        
        Example:
            segment_data = '{"segment_name": "Credit Accounts", "business_dictionary": [...]}'
            result = extract_credit_domain_entities(segment_data)
        """
        try:
            segment_dict = json.loads(segment_data)
            entities = entity_extractor.extract_credit_domain_entities(segment_dict)
            return json.dumps(entities, indent=2)
        except Exception as e:
            return f"Error extracting credit domain entities: {str(e)}"
    
    @tool
    def extract_data_asset_entities(asset_data: str) -> str:
        """
        Extract structured entities from data asset information.
        
        This tool analyzes data asset information including asset metadata, 
        column definitions, and workspace context to extract meaningful entities
        with their attributes and relationships.
        
        Args:
            asset_data (str): JSON string containing data asset information with fields:
                - asset_name: Name of the data asset
                - workspace_name: Name of the workspace
                - big_query_table_name: BigQuery table name
                - columns: List of column definitions with:
                    - column_name: Name of the column
                    - column: Column identifier
                    - data_type: Data type of the column
                    - description: Column description
        
        Returns:
            str: JSON string containing extracted entities with:
                - entity_type: Type of entity (FIELD, ASSET, METADATA, VALUE)
                - entity_name: Name of the entity
                - entity_value: Value or description
                - confidence: Confidence score (0.0-1.0)
                - source_field: Source field identifier
                - description: Business significance
                - context_provider: Always "data_asset"
        
        Example:
            asset_data = '{"asset_name": "Consumer Credit Database", "columns": [...]}'
            result = extract_data_asset_entities(asset_data)
        """
        try:
            asset_dict = json.loads(asset_data)
            entities = entity_extractor.extract_data_asset_entities(asset_dict)
            return json.dumps(entities, indent=2)
        except Exception as e:
            return f"Error extracting data asset entities: {str(e)}"
    
    return [extract_credit_domain_entities, extract_data_asset_entities]


def create_crud_tools(entity_manager) -> List:
    """Create CRUD tools for entity management"""
    
    @tool
    def read_entities(session_id: str, entity_id: str = None, entity_type: str = None, include_attributes: bool = True) -> str:
        """
        Read entities from a session with optional filtering capabilities.
        
        This tool allows you to retrieve entities from a specific session with various
        filtering options. You can read all entities, filter by type, or get a specific
        entity by ID. The tool supports reading entity attributes as well.
        
        Args:
            session_id (str): Unique session identifier to read entities from
            entity_id (str, optional): Specific entity ID to retrieve. If provided,
                only this entity will be returned. Defaults to None (read all).
            entity_type (str, optional): Filter entities by type. Valid types include:
                - 'field': Business dictionary fields
                - 'business_metric': Derived business metrics
                - 'relationship': Entity relationships
                - 'derived_insight': AI-generated insights
                - 'operational_rule': Business rules
                Defaults to None (no type filtering).
            include_attributes (bool, optional): Whether to include entity attributes
                in the response. Defaults to True.
        
        Returns:
            str: JSON string containing:
                - entities: List of matching entities with full details
                - total_count: Total number of entities found
                - filtered_count: Number of entities after filtering
                - session_id: Session identifier
                - state_version: Current state version
                - metadata: Additional metadata about the query
        
        Example:
            # Read all entities from a session
            result = read_entities("session_123")
            
            # Read only field entities
            result = read_entities("session_123", entity_type="field")
            
            # Read specific entity with attributes
            result = read_entities("session_123", entity_id="entity_456", include_attributes=True)
        """
        try:
            entity_type_enum = None
            if entity_type:
                try:
                    entity_type_enum = EntityType(entity_type.lower())
                except ValueError:
                    return f"Invalid entity type: {entity_type}. Valid types: {[e.value for e in EntityType]}"
            
            request = ReadEntityRequest(
                session_id=session_id,
                entity_id=entity_id,
                entity_type=entity_type_enum,
                include_attributes=include_attributes
            )
            
            if entity_manager:
                response = entity_manager.read_entities(request)
                return json.dumps({
                    "entities": [entity.model_dump() for entity in response.entities],
                    "state_version": response.state_version,
                    "total_count": response.total_count,
                    "success": response.success,
                    "message": response.message
                }, indent=2)
            else:
                return "Entity manager not available"
        except Exception as e:
            return f"Error reading entities: {str(e)}"
    
    @tool
    def delete_entities(session_id: str, entity_id: str = None, attribute_ids: str = None, delete_all: bool = False) -> str:
        """
        Delete entities or specific attributes from a session.
        
        This tool provides flexible deletion capabilities for entities and their attributes.
        You can delete entire entities, specific attributes within entities, or all entities
        in a session. The tool maintains referential integrity and updates state versions.
        
        Args:
            session_id (str): Unique session identifier to delete entities from
            entity_id (str, optional): Specific entity ID to delete. If provided along with
                attribute_ids, only those attributes will be deleted from the entity.
                If provided without attribute_ids, the entire entity will be deleted.
                Defaults to None.
            attribute_ids (str, optional): Comma-separated list of attribute IDs to delete.
                Must be used with entity_id. Only these specific attributes will be removed
                from the entity, keeping the entity intact. Defaults to None.
            delete_all (bool, optional): If True, deletes all entities in the session.
                This is a destructive operation and should be used with caution.
                Defaults to False.
        
        Returns:
            str: JSON string containing:
                - deleted_entities: List of deleted entity IDs
                - deleted_attributes: List of deleted attribute IDs
                - total_deleted: Total number of items deleted
                - session_id: Session identifier
                - state_version: Updated state version after deletion
                - message: Human-readable deletion summary
        
        Example:
            # Delete entire entity
            result = delete_entities("session_123", entity_id="entity_456")
            
            # Delete specific attributes from entity
            result = delete_entities("session_123", entity_id="entity_456", attribute_ids="attr_1,attr_2")
            
            # Delete all entities in session (use with caution)
            result = delete_entities("session_123", delete_all=True)
        """
        try:
            attribute_ids_list = None
            if attribute_ids:
                attribute_ids_list = [aid.strip() for aid in attribute_ids.split(',')]
            
            request = DeleteEntityRequest(
                session_id=session_id,
                entity_id=entity_id,
                attribute_ids=attribute_ids_list,
                delete_all=delete_all
            )
            
            if entity_manager:
                response = entity_manager.delete_entities(request)
                return json.dumps({
                    "deleted_entities": response.deleted_entities,
                    "deleted_attributes": response.deleted_attributes,
                    "state_version": response.state_version,
                    "success": response.success,
                    "message": response.message
                }, indent=2)
            else:
                return "Entity manager not available"
        except Exception as e:
            return f"Error deleting entities: {str(e)}"
    
    @tool
    def update_entities(session_id: str, entity_id: str, entity_updates: str = None, attribute_updates: str = None) -> str:
        """
        Update entities or their attributes with new information.
        
        This tool allows you to modify existing entities and their attributes. You can
        update entity-level fields (name, value, description, confidence) or add/update
        specific attributes within an entity. The tool maintains data integrity and
        automatically increments state versions.
        
        Args:
            session_id (str): Unique session identifier containing the entity to update
            entity_id (str): Unique identifier of the entity to update
            entity_updates (str, optional): JSON string containing entity field updates:
                - entity_name: Updated entity name
                - entity_value: Updated entity value
                - description: Updated description
                - confidence: Updated confidence score (0.0-1.0)
                - relationships: Updated relationships object
            attribute_updates (str, optional): JSON string containing attribute updates:
                - List of attribute objects with:
                    - attribute_name: Name of the attribute
                    - attribute_value: Value of the attribute
                    - attribute_type: Type (string, number, boolean, object)
                    - confidence: Confidence score (0.0-1.0)
                    - description: Attribute description
        
        Returns:
            str: JSON string containing:
                - updated_entity: Complete updated entity object with all fields
                - updated_attributes: List of updated attribute objects
                - session_id: Session identifier
                - state_version: Updated state version after modification
                - message: Human-readable update summary
        
        Example:
            # Update entity fields
            entity_updates = '{"entity_name": "Updated Name", "confidence": 0.95}'
            result = update_entities("session_123", "entity_456", entity_updates=entity_updates)
            
            # Update/add attributes
            attribute_updates = '[{"attribute_name": "risk_score", "attribute_value": 750, "attribute_type": "number", "confidence": 0.9}]'
            result = update_entities("session_123", "entity_456", attribute_updates=attribute_updates)
            
            # Update both entity and attributes
            result = update_entities("session_123", "entity_456", entity_updates, attribute_updates)
        """
        try:
            entity_updates_dict = None
            if entity_updates:
                entity_updates_dict = json.loads(entity_updates)
            
            attribute_updates_list = None
            if attribute_updates:
                attribute_updates_list = json.loads(attribute_updates)
            
            request = UpdateEntityRequest(
                session_id=session_id,
                entity_id=entity_id,
                entity_updates=entity_updates_dict,
                attribute_updates=attribute_updates_list
            )
            
            if entity_manager:
                response = entity_manager.update_entities(request)
                return json.dumps({
                    "updated_entity": response.updated_entity.model_dump() if response.updated_entity else None,
                    "state_version": response.state_version,
                    "success": response.success,
                    "message": response.message
                }, indent=2)
            else:
                return "Entity manager not available"
        except Exception as e:
            return f"Error updating entities: {str(e)}"
    
    return [read_entities, delete_entities, update_entities]


def create_all_tools(entity_extractor: EntityExtractor, entity_manager) -> List:
    """Create all tools for the agent"""
    extraction_tools = create_extraction_tools(entity_extractor)
    crud_tools = create_crud_tools(entity_manager)
    return extraction_tools + crud_tools
