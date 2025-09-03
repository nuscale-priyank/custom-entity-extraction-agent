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


class ExtractedEntity(BaseModel):
    """Model for extracted entities"""
    entity_type: EntityType = Field(description="Type of entity extracted")
    entity_name: str = Field(description="Name of the extracted entity")
    entity_value: str = Field(description="Value of the extracted entity")
    confidence: float = Field(description="Confidence score (0-1)")
    source_field: str = Field(description="Source field")
    description: str = Field(description="Description of the entity")
    relationships: Dict[str, str] = Field(default={}, description="Relationships with other entities")
    context_provider: str = Field(description="Context provider (e.g., credit_domain, generic)")


class ChatMessage(BaseModel):
    """Model for chat messages"""
    role: str = Field(description="Role of the message sender (user/assistant)")
    content: str = Field(description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatState(BaseModel):
    """Model for chat state management"""
    session_id: str = Field(description="Session identifier")
    messages: List[ChatMessage] = Field(default=[], description="Chat messages")
    selected_segments: List[CreditDomainSegment] = Field(default=[], description="Selected credit domain segments")
    selected_assets: List[DataAsset] = Field(default=[], description="Selected data assets")
    selected_bc3_fields: List[Dict[str, Any]] = Field(default=[], description="Selected BC3 fields with context")
    selected_asset_columns: List[Dict[str, Any]] = Field(default=[], description="Selected asset columns with context")
    extracted_entities: List[ExtractedEntity] = Field(default=[], description="Extracted entities")
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
