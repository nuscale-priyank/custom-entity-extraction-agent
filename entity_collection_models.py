"""
Models for the custom_entities collection in Firestore.
This collection stores all entity-related data separately from chat sessions.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class EntityType(str, Enum):
    """Entity types for the custom entities collection"""
    FIELD = "field"
    BUSINESS_METRIC = "business_metric"
    RELATIONSHIP = "relationship"
    DERIVED_INSIGHT = "derived_insight"
    OPERATIONAL_RULE = "operational_rule"
    DATA_ASSET = "data_asset"
    SEGMENT = "segment"
    METADATA = "metadata"
    VALUE = "value"
    COLUMN = "column"
    ASSET = "asset"


class EntityAttribute(BaseModel):
    """Entity attribute model for custom entities collection"""
    attribute_id: str = Field(default_factory=lambda: f"attr_{uuid.uuid4().hex[:8]}")
    attribute_name: str
    attribute_value: str
    attribute_type: str = "string"  # string, number, boolean, object
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    source_field: str = ""
    description: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CustomEntity(BaseModel):
    """Custom entity model for the custom_entities collection"""
    entity_id: str = Field(default_factory=lambda: f"entity_{uuid.uuid4().hex[:8]}")
    session_id: str  # Links to chat_sessions collection
    entity_type: EntityType
    entity_name: str
    entity_value: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    source_field: str = ""
    description: str = ""
    relationships: Dict[str, Any] = Field(default_factory=dict)
    context_provider: str = "credit_domain"  # credit_domain, data_asset, user_created
    attributes: List[EntityAttribute] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str = "system"  # system, user, llm
    version: int = 1


class EntityCollectionDocument(BaseModel):
    """Document model for the custom_entities collection"""
    session_id: str  # Primary key - links to chat_sessions
    entities: List[CustomEntity] = Field(default_factory=list)
    total_entities: int = 0
    last_entity_created: Optional[datetime] = None
    last_entity_updated: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Request/Response models for entity operations
class CreateEntityRequest(BaseModel):
    """Request model for creating entities"""
    session_id: str
    entities_data: List[Dict[str, Any]]


class CreateEntityResponse(BaseModel):
    """Response model for creating entities"""
    created_entities: List[CustomEntity]
    total_created: int
    session_id: str
    success: bool
    message: str


class ReadEntityRequest(BaseModel):
    """Request model for reading entities"""
    session_id: str
    entity_id: Optional[str] = None
    entity_type: Optional[EntityType] = None
    limit: int = 100
    offset: int = 0


class ReadEntityResponse(BaseModel):
    """Response model for reading entities"""
    entities: List[CustomEntity]
    total_count: int
    session_id: str
    success: bool
    message: str


class UpdateEntityRequest(BaseModel):
    """Request model for updating entities"""
    session_id: str
    entity_id: str
    entity_data: Dict[str, Any]
    attribute_updates: Optional[List[Dict[str, Any]]] = None


class UpdateEntityResponse(BaseModel):
    """Response model for updating entities"""
    updated_entity: Optional[CustomEntity]
    session_id: str
    success: bool
    message: str


class DeleteEntityRequest(BaseModel):
    """Request model for deleting entities"""
    session_id: str
    entity_id: Optional[str] = None
    attribute_ids: Optional[List[str]] = None
    delete_all: bool = False


class DeleteEntityResponse(BaseModel):
    """Response model for deleting entities"""
    deleted_entities: List[str]
    deleted_attributes: List[str]
    total_deleted: int
    session_id: str
    success: bool
    message: str
