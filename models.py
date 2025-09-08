"""
Pydantic models for the BC3 AI Agent API
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ChatRequest(BaseModel):
    message: str
    session_id: str
    selected_bc3_fields: Optional[List[Dict]] = []
    selected_asset_columns: Optional[List[Dict]] = []


class ChatResponse(BaseModel):
    response: str
    success: bool
    entities_created: int
    entities: List[Dict]


class EntityRequest(BaseModel):
    session_id: str
    entity_id: Optional[str] = None


class EntityResponse(BaseModel):
    success: bool
    message: str
    entities: List[Dict]
    total_count: int


class CreateEntityRequest(BaseModel):
    session_id: str
    entity_name: str
    entity_type: str
    entity_value: str
    description: str
    attributes: List[Dict] = []


class UpdateEntityRequest(BaseModel):
    session_id: str
    entity_id: str
    entity_name: Optional[str] = None
    entity_type: Optional[str] = None
    entity_value: Optional[str] = None
    description: Optional[str] = None


class DeleteEntityRequest(BaseModel):
    session_id: str
    entity_id: str


class AttributeRequest(BaseModel):
    session_id: str
    entity_id: str
    attribute_id: Optional[str] = None


class CreateAttributeRequest(BaseModel):
    session_id: str
    entity_id: str
    attribute_name: str
    attribute_value: str
    attribute_type: str
    description: str


class UpdateAttributeRequest(BaseModel):
    session_id: str
    entity_id: str
    attribute_id: str
    attribute_name: Optional[str] = None
    attribute_value: Optional[str] = None
    attribute_type: Optional[str] = None
    description: Optional[str] = None


class DeleteAttributeRequest(BaseModel):
    session_id: str
    entity_id: str
    attribute_id: str


class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None
