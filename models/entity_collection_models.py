"""
Models for the custom_entities collection in Firestore.
This collection stores all entity-related data separately from chat sessions.
"""

from datetime import datetime, timezone
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
    attribute_value: Any  # Allow any type (str, int, float, bool, etc.)
    attribute_type: str = "string"  # string, number, boolean, object
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    source_field: str = ""
    description: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"  # system, user, llm
    version: int = 1


class EntityCollectionDocument(BaseModel):
    """Document model for the custom_entities collection"""
    session_id: str  # Primary key - links to chat_sessions
    entities: List[CustomEntity] = Field(default_factory=list)
    total_entities: int = 0
    last_entity_created: Optional[datetime] = None
    last_entity_updated: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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


# API Request/Response models for endpoints
class ChatRequest(BaseModel):
    """Request model for chat/conversation endpoint"""
    message: str
    session_id: str
    selected_bc3_fields: Optional[List[Dict]] = []
    selected_asset_columns: Optional[List[Dict]] = []


class ChatResponse(BaseModel):
    """Response model for chat/conversation endpoint"""
    response: str
    success: bool
    entities_created: int
    entities: List[Dict]


class EntityResponse(BaseModel):
    """Response model for entity read operations"""
    success: bool
    message: str
    entities: List[Dict]
    total_count: int


class ApiCreateEntityRequest(BaseModel):
    """API request model for creating entities (renamed to avoid conflict)"""
    session_id: str
    entity_name: str
    entity_type: str
    entity_value: str
    description: str
    attributes: List[Dict] = []


class ApiUpdateEntityRequest(BaseModel):
    """API request model for updating entities (renamed to avoid conflict)"""
    session_id: str
    entity_id: str
    entity_name: Optional[str] = None
    entity_type: Optional[str] = None
    entity_value: Optional[str] = None
    description: Optional[str] = None


class ApiDeleteEntityRequest(BaseModel):
    """API request model for deleting entities (renamed to avoid conflict)"""
    session_id: str
    entity_id: str


class CreateAttributeRequest(BaseModel):
    """Request model for creating attributes"""
    session_id: str
    entity_id: str
    attribute_name: str
    attribute_value: str
    attribute_type: str
    description: str


class UpdateAttributeRequest(BaseModel):
    """Request model for updating attributes"""
    session_id: str
    entity_id: str
    attribute_id: str
    attribute_name: Optional[str] = None
    attribute_value: Optional[str] = None
    attribute_type: Optional[str] = None
    description: Optional[str] = None


class DeleteAttributeRequest(BaseModel):
    """Request model for deleting attributes"""
    session_id: str
    entity_id: str
    attribute_id: str


class StandardResponse(BaseModel):
    """Standard response model for API endpoints"""
    success: bool
    message: str
    data: Optional[Dict] = None
