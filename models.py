from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class BusinessDictionaryField(BaseModel):
    """Model for individual business dictionary field definition"""
    uuid: str = Field(description="Unique identifier for the field")
    known_implementations: List[str] = Field(description="Known implementation names")
    valid_values: List[str] = Field(default=[], description="Valid values for the field")
    definition: str = Field(description="Definition of the field")
    notes: str = Field(default="", description="Additional notes")
    description: str = Field(description="Human-readable description")


class CreditDomainSegment(BaseModel):
    """Model for Credit Domain segment data"""
    segment_name: str = Field(description="Name of the segment")
    business_dictionary: List[BusinessDictionaryField] = Field(description="List of business dictionary fields")


class DataAssetColumn(BaseModel):
    """Model for data asset column information"""
    column_name: str = Field(description="Name of the column")
    column: str = Field(description="Column identifier")


class DataAsset(BaseModel):
    """Model for data asset information"""
    asset_id: str = Field(description="Unique asset identifier")
    asset_name: str = Field(description="Name of the asset")
    workspace_id: str = Field(description="Workspace identifier")
    workspace_name: str = Field(description="Name of the workspace")
    big_query_table_name: str = Field(description="BigQuery table name")
    columns: List[DataAssetColumn] = Field(description="List of columns")


class GenericDataField(BaseModel):
    """Generic model for data field definition"""
    field_name: str = Field(description="Name of the field")
    field_value: Any = Field(description="Value of the field")
    field_type: str = Field(description="Type of the field")
    description: Optional[str] = Field(default=None, description="Description of the field")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class GenericDocument(BaseModel):
    """Generic model for document data"""
    document_type: str = Field(description="Type of document")
    document_id: Optional[str] = Field(default=None, description="Document identifier")
    content: Dict[str, Any] = Field(description="Document content")
    metadata: Dict[str, Any] = Field(default={}, description="Document metadata")


class EntityType(str, Enum):
    """Types of entities that can be extracted"""
    FIELD = "field"
    SEGMENT = "segment"
    VALUE = "value"
    METADATA = "metadata"
    DOCUMENT = "document"
    OBJECT = "object"
    ARRAY = "array"
    ASSET = "asset"
    COLUMN = "column"
    BUSINESS_METRIC = "business_metric"
    RELATIONSHIP = "relationship"
    DERIVED_INSIGHT = "derived_insight"
    OPERATIONAL_RULE = "operational_rule"


class EntityAttribute(BaseModel):
    """Model for entity attributes"""
    attribute_id: str = Field(description="Unique identifier for the attribute")
    attribute_name: str = Field(description="Name of the attribute")
    attribute_value: Any = Field(description="Value of the attribute")
    attribute_type: str = Field(description="Type of the attribute")
    confidence: float = Field(description="Confidence score (0-1)")
    source_field: str = Field(description="Source field for this attribute")
    description: str = Field(description="Description of the attribute")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class ExtractedEntity(BaseModel):
    """Model for extracted entities with attributes"""
    entity_id: str = Field(description="Unique identifier for the entity")
    entity_type: EntityType = Field(description="Type of entity extracted")
    entity_name: str = Field(description="Name of the extracted entity")
    entity_value: str = Field(description="Value of the extracted entity")
    confidence: float = Field(description="Confidence score (0-1)")
    source_field: str = Field(description="Source field")
    description: str = Field(description="Description of the entity")
    relationships: Dict[str, str] = Field(default={}, description="Relationships with other entities")
    context_provider: str = Field(description="Context provider (e.g., credit_domain, generic)")
    attributes: List[EntityAttribute] = Field(default=[], description="List of entity attributes")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    state_version: int = Field(default=1, description="State version for tracking changes")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class ChatMessage(BaseModel):
    """Model for chat messages"""
    role: str = Field(description="Role of the message sender (user/assistant)")
    content: str = Field(description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatState(BaseModel):
    """Model for chat state management with state versioning"""
    session_id: str = Field(description="Session identifier")
    messages: List[ChatMessage] = Field(default=[], description="Chat messages")
    selected_segments: List[CreditDomainSegment] = Field(default=[], description="Selected credit domain segments")
    selected_assets: List[DataAsset] = Field(default=[], description="Selected data assets")
    selected_bc3_fields: List[Dict[str, Any]] = Field(default=[], description="Selected BC3 fields with context")
    selected_asset_columns: List[Dict[str, Any]] = Field(default=[], description="Selected asset columns with context")
    extracted_entities: List[ExtractedEntity] = Field(default=[], description="Extracted entities")
    state_version: int = Field(default=1, description="Current state version")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class AgentRequest(BaseModel):
    """Request model for the AI agent"""
    message: str = Field(description="User input message")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    credit_domain_data: Optional[List[CreditDomainSegment]] = Field(default=None, description="Credit domain data")
    data_assets: Optional[List[DataAsset]] = Field(default=None, description="Data assets")
    selected_bc3_fields: Optional[List[Dict[str, Any]]] = Field(default=None, description="Selected BC3 fields with context")
    selected_asset_columns: Optional[List[Dict[str, Any]]] = Field(default=None, description="Selected asset columns with context")
    generic_data: Optional[Union[GenericDocument, Dict[str, Any]]] = Field(default=None, description="Generic data")
    context_provider: str = Field(default="credit_domain", description="Context provider type")
    tools_enabled: bool = Field(default=True, description="Whether to enable tools")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class AgentResponse(BaseModel):
    """Response model for the AI agent"""
    response: str = Field(description="Agent's response message")
    chat_output: str = Field(description="Formatted chat output with bulleted entities and relationships")
    extracted_entities: List[ExtractedEntity] = Field(description="List of extracted entities")
    chat_state: ChatState = Field(description="Updated chat state")
    confidence_score: float = Field(description="Overall confidence score")
    processing_time: float = Field(description="Processing time in seconds")
    metadata: Dict[str, Any] = Field(default={}, description="Additional response metadata")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="Service status")
    timestamp: datetime = Field(description="Current timestamp")
    version: str = Field(description="API version")


# CRUD Request/Response Models
class ReadEntityRequest(BaseModel):
    """Request to read entity/entities"""
    session_id: str = Field(description="Session identifier")
    entity_id: Optional[str] = Field(default=None, description="Specific entity ID to read")
    entity_type: Optional[EntityType] = Field(default=None, description="Filter by entity type")
    include_attributes: bool = Field(default=True, description="Include entity attributes")
    state_version: Optional[int] = Field(default=None, description="Specific state version to read")


class ReadEntityResponse(BaseModel):
    """Response for reading entities"""
    entities: List[ExtractedEntity] = Field(description="List of entities")
    state_version: int = Field(description="Current state version")
    total_count: int = Field(description="Total number of entities")
    success: bool = Field(description="Operation success status")
    message: str = Field(description="Response message")


class DeleteEntityRequest(BaseModel):
    """Request to delete entity/entities or attributes"""
    session_id: str = Field(description="Session identifier")
    entity_id: Optional[str] = Field(default=None, description="Entity ID to delete")
    attribute_ids: Optional[List[str]] = Field(default=None, description="Attribute IDs to delete")
    delete_all: bool = Field(default=False, description="Delete all entities in session")


class DeleteEntityResponse(BaseModel):
    """Response for deleting entities/attributes"""
    deleted_entities: List[str] = Field(description="List of deleted entity IDs")
    deleted_attributes: List[str] = Field(description="List of deleted attribute IDs")
    state_version: int = Field(description="New state version after deletion")
    success: bool = Field(description="Operation success status")
    message: str = Field(description="Response message")


class UpdateEntityRequest(BaseModel):
    """Request to update entity or attributes"""
    session_id: str = Field(description="Session identifier")
    entity_id: str = Field(description="Entity ID to update")
    entity_updates: Optional[Dict[str, Any]] = Field(default=None, description="Entity field updates")
    attribute_updates: Optional[List[Dict[str, Any]]] = Field(default=None, description="Attribute updates")


class UpdateEntityResponse(BaseModel):
    """Response for updating entities/attributes"""
    updated_entity: Optional[ExtractedEntity] = Field(description="Updated entity")
    state_version: int = Field(description="New state version after update")
    success: bool = Field(description="Operation success status")
    message: str = Field(description="Response message")


# Backward compatibility aliases
class BC3Segment(CreditDomainSegment):
    """Backward compatibility for BC3-specific requests"""
    pass


class BC3Field(BusinessDictionaryField):
    """Backward compatibility for BC3 field definitions"""
    bc3_field: str = Field(description="BC3 field identifier")
    
    @property
    def known_implementations(self) -> List[str]:
        return [self.bc3_field] if hasattr(self, 'bc3_field') else []


class BC3AgentRequest(AgentRequest):
    """Backward compatibility for BC3-specific requests"""
    bc3_data: Optional[List[BC3Segment]] = Field(default=None, description="BC3 data to analyze")
    
    @property
    def credit_domain_data(self) -> Optional[List[CreditDomainSegment]]:
        return self.bc3_data
