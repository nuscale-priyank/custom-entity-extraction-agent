from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class BC3Field(BaseModel):
    """Model for individual BC3 field definition"""
    definition: str = Field(description="Definition of the field")
    bc3_field: str = Field(description="BC3 field identifier")
    description: str = Field(description="Human-readable description")
    notes: str = Field(default="", description="Additional notes")
    valid_values: List[str] = Field(default=[], description="Valid values for the field")


class BC3Segment(BaseModel):
    """Model for BC3 segment data"""
    segment_name: str = Field(description="Name of the segment")
    data_dictionary: List[BC3Field] = Field(description="List of field definitions")


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


class ExtractedEntity(BaseModel):
    """Model for extracted entities"""
    entity_type: EntityType = Field(description="Type of entity extracted")
    entity_name: str = Field(description="Name of the extracted entity")
    entity_value: str = Field(description="Value of the extracted entity")
    confidence: float = Field(description="Confidence score (0-1)")
    source_field: str = Field(description="Source field")
    description: str = Field(description="Description of the entity")
    context_provider: str = Field(description="Context provider (e.g., BC3, generic)")


class ChatMessage(BaseModel):
    """Model for chat messages"""
    role: str = Field(description="Role of the message sender (user/assistant)")
    content: str = Field(description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentRequest(BaseModel):
    """Request model for the AI agent"""
    message: str = Field(description="User input message")
    data: Union[BC3Segment, GenericDocument, Dict[str, Any]] = Field(description="Data to analyze")
    context_provider: str = Field(default="generic", description="Context provider type")
    chat_history: List[ChatMessage] = Field(default=[], description="Previous chat messages")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    tools_enabled: bool = Field(default=True, description="Whether to enable tools")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class AgentResponse(BaseModel):
    """Response model for the AI agent"""
    response: str = Field(description="Agent's response message")
    extracted_entities: List[ExtractedEntity] = Field(description="List of extracted entities")
    chat_history: List[ChatMessage] = Field(description="Updated chat history")
    session_id: str = Field(description="Session identifier")
    confidence_score: float = Field(description="Overall confidence score")
    processing_time: float = Field(description="Processing time in seconds")
    metadata: Dict[str, Any] = Field(default={}, description="Additional response metadata")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="Service status")
    timestamp: datetime = Field(description="Current timestamp")
    version: str = Field(description="API version")


# Backward compatibility aliases
class BC3AgentRequest(AgentRequest):
    """Backward compatibility for BC3-specific requests"""
    bc3_data: BC3Segment = Field(description="BC3 data to analyze")
    
    @property
    def data(self) -> BC3Segment:
        return self.bc3_data
