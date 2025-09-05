import os
import time
import uuid
import json
import logging
from typing import Dict, List, Any, Optional, Union, TypedDict, Annotated
from datetime import datetime
from abc import ABC, abstractmethod

# Configure logger
logger = logging.getLogger(__name__)

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_vertexai import ChatVertexAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from models import (
    CreditDomainSegment, BusinessDictionaryField, DataAsset, DataAssetColumn,
    ExtractedEntity, EntityAttribute, EntityType, ChatMessage, AgentRequest, AgentResponse, 
    ChatState, GenericDocument, GenericDataField
)
from session_managers import SessionManager, InMemorySessionManager
from config import create_session_manager_from_config, SessionConfig
from entity_manager import EntityManager


class AgentState(TypedDict):
    """State schema for LangGraph - following LangGraph best practices"""
    messages: Annotated[List[Any], "Chat messages"]
    session_id: Annotated[str, "Session identifier"]
    selected_segments: Annotated[List[Dict], "Selected credit domain segments"]
    selected_assets: Annotated[List[Dict], "Selected data assets"]
    selected_bc3_fields: Annotated[List[Dict], "Selected BC3 fields with context"]
    selected_asset_columns: Annotated[List[Dict], "Selected asset columns with context"]
    extracted_entities: Annotated[List[Dict], "Extracted entities"]
    user_intent: Annotated[str, "Detected user intent (extract|update_entity|update_attribute|delete_entity|delete_attribute|read)"]
    action_required: Annotated[str, "Specific action to perform based on intent"]
    metadata: Annotated[Dict[str, Any], "Additional metadata"]





class EntityExtractor:
    """Separate class for entity extraction logic"""
    
    @staticmethod
    def extract_credit_domain_entities(segment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities from Credit Domain segment data"""
        try:
            segment = CreditDomainSegment(**segment_data)
            entities = []
            
            # Extract segment-level entity
            entities.append({
                "entity_type": EntityType.SEGMENT,
                "entity_name": "segment_name",
                "entity_value": segment.segment_name,
                "confidence": 1.0,
                "source_field": "segment_name",
                "description": f"Credit Domain segment: {segment.segment_name}",
                "context_provider": "credit_domain"
            })
            
            # Extract field-level entities from business dictionary
            for field in segment.business_dictionary:
                # Field entity
                entities.append({
                    "entity_type": EntityType.FIELD,
                    "entity_name": field.description,
                    "entity_value": field.definition,
                    "confidence": 0.95,
                    "source_field": field.uuid,
                    "description": f"Business dictionary field: {field.description}",
                    "context_provider": "credit_domain"
                })
                
                # Known implementations
                for impl in field.known_implementations:
                    entities.append({
                        "entity_type": EntityType.METADATA,
                        "entity_name": f"{field.description}_implementation",
                        "entity_value": impl,
                        "confidence": 0.9,
                        "source_field": field.uuid,
                        "description": f"Known implementation for {field.description}: {impl}",
                        "context_provider": "credit_domain"
                    })
                
                # Valid values
                for value in field.valid_values:
                    entities.append({
                        "entity_type": EntityType.VALUE,
                        "entity_name": f"{field.description}_value",
                        "entity_value": value,
                        "confidence": 0.9,
                        "source_field": field.uuid,
                        "description": f"Valid value for {field.description}: {value}",
                        "context_provider": "credit_domain"
                    })
                
                # Notes
                if field.notes:
                    entities.append({
                        "entity_type": EntityType.METADATA,
                        "entity_name": f"{field.description}_notes",
                        "entity_value": field.notes,
                        "confidence": 0.85,
                        "source_field": field.uuid,
                        "description": f"Notes for {field.description}",
                        "context_provider": "credit_domain"
                    })
            
            return entities
            
        except Exception as e:
            return [{
                "entity_type": EntityType.METADATA,
                "entity_name": "error",
                "entity_value": str(e),
                "confidence": 0.0,
                "source_field": "system",
                "description": f"Error extracting Credit Domain entities: {str(e)}",
                "context_provider": "credit_domain"
            }]
    
    @staticmethod
    def extract_data_asset_entities(asset_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities from data asset information"""
        try:
            asset = DataAsset(**asset_data)
            entities = []
            
            # Asset-level entity
            entities.append({
                "entity_type": EntityType.ASSET,
                "entity_name": "asset_name",
                "entity_value": asset.asset_name,
                "confidence": 1.0,
                "source_field": "asset_name",
                "description": f"Data asset: {asset.asset_name}",
                "context_provider": "data_asset"
            })
            
            # Workspace information
            entities.append({
                "entity_type": EntityType.METADATA,
                "entity_name": "workspace_name",
                "entity_value": asset.workspace_name,
                "confidence": 0.95,
                "source_field": "workspace_name",
                "description": f"Workspace: {asset.workspace_name}",
                "context_provider": "data_asset"
            })
            
            # BigQuery table
            entities.append({
                "entity_type": EntityType.METADATA,
                "entity_name": "big_query_table",
                "entity_value": asset.big_query_table_name,
                "confidence": 0.95,
                "source_field": "big_query_table_name",
                "description": f"BigQuery table: {asset.big_query_table_name}",
                "context_provider": "data_asset"
            })
            
            # Column information
            for column in asset.columns:
                entities.append({
                    "entity_type": EntityType.COLUMN,
                    "entity_name": "column_name",
                    "entity_value": column.column_name,
                    "confidence": 0.9,
                    "source_field": column.column,
                    "description": f"Column: {column.column_name}",
                    "context_provider": "data_asset"
                })
            
            return entities
            
        except Exception as e:
            return [{
                "entity_type": EntityType.METADATA,
                "entity_name": "error",
                "entity_value": str(e),
                "confidence": 0.0,
                "source_field": "system",
                "description": f"Error extracting data asset entities: {str(e)}",
                "context_provider": "data_asset"
            }]


class LLMManager:
    """Separate class for LLM management"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
    
    def _initialize_llm(self) -> ChatVertexAI:
        """Initialize Vertex AI LLM"""
        return ChatVertexAI(
            model_name="gemini-2.5-flash-lite",
            project=self.project_id,
            location=self.location,
            temperature=0.1,
            max_output_tokens=2048
        )
    
    def _initialize_tools(self) -> List:
        """Initialize extraction and CRUD tools"""
        from tools import create_all_tools
        
        # Create tools with entity extractor and entity manager
        entity_extractor = EntityExtractor()
        entity_manager = getattr(self, 'entity_manager', None)
        
        return create_all_tools(entity_extractor, entity_manager)
    
    def get_system_prompt(self, intent: str = "extract") -> str:
        """Get system prompt based on user intent"""
        base_prompt = """You are a specialized AI agent designed to help users manage entities from Credit Domain (BC3) data and data assets.

AVAILABLE TOOLS:
- extract_credit_domain_entities: Extract structured entities from BC3 segment data
- extract_data_asset_entities: Extract structured entities from data asset information  
- read_entities: Read entities from a session with optional filtering
- delete_entities: Delete entities or attributes from a session
- update_entities: Update entities or their attributes

CRITICAL: For read, update, and delete operations, you MUST use the appropriate tools. Do not provide responses without using tools.

INTENT-BASED RESPONSES:"""

        if intent == "extract":
            return base_prompt + """
**INTENT: EXTRACT ENTITIES**
Your goal is to extract entities from the provided context and create meaningful derived insights.

CRITICAL: The context is ALREADY provided below. Do not ask for more context.

**Response Structure**: Your response MUST be in JSON format:
```json
{{
  "extracted_entities": [
    {{
      "entity_type": "FIELD|BUSINESS_METRIC|RELATIONSHIP|DERIVED_INSIGHT|OPERATIONAL_RULE",
      "entity_name": "Entity Name",
      "entity_value": "Entity Value or Description",
      "confidence": 0.95,
      "source_field": "BC3 Fields or Asset Columns used",
      "description": "Business significance explanation",
      "relationships": {{
        "influences": "Related Entity",
        "correlates_with": "Another Entity", 
        "depends_on": "Dependency Entity"
      }},
      "attributes": [
        {{
          "attribute_name": "Attribute Name",
          "attribute_value": "Attribute Value",
          "attribute_type": "string|number|boolean|object",
          "confidence": 0.9,
          "source_field": "Source field for this attribute",
          "description": "Attribute description"
        }}
      ]
    }}
  ],
  "analysis": "Explain how these entities provide value and insights",
  "suggestions": [
    "Additional BC3 fields that would be valuable",
    "Additional asset columns that would enhance analysis"
  ]
}}
```

**Entity Examples**:
- **Obvious Entities**: "Account Number", "Credit Limit", "Credit Score"
- **Derived Business Metrics**: "Credit Utilization Ratio", "Risk Score"  
- **Relationship Entities**: "Account-Credit Correlation", "Risk Patterns"
- **Operational Insights**: "Account Health Status", "Risk Category"

**Quality Requirements**:
- Minimum 3 entities per response (mix of obvious and derived)
   - Confidence scores 0.7-1.0 for clear context
   - Business-focused explanations
- Valid JSON format that can be parsed

⚠️ CRITICAL: DO NOT ask for more context. Use what's provided to extract and create entities.
⚠️ CRITICAL: ALWAYS respond in valid JSON format as specified above."""

        elif intent == "update_entity":
            return base_prompt + """
**INTENT: UPDATE ENTITY**
Your goal is to update an existing entity with new information.

**CRITICAL: You MUST use the update_entities tool to modify entities in the session.**

**Tool Usage Instructions:**
1. First, identify the entity_id from the user's request or use read_entities to find it
2. Call the update_entities tool with the session_id and entity_id
3. Provide entity_updates and/or attribute_updates as JSON strings
4. Confirm the update was successful

**Response Structure**: After using the tool, provide a summary in JSON format:
```json
{{
  "action": "update_entity",
  "tool_used": "update_entities",
  "entity_id": "entity_id_updated",
  "session_id": "session_id_from_context",
  "message": "Entity updated successfully with new information"
}}
```

**Example Tool Call:**
- update_entities(session_id="session_123", entity_id="entity_456", entity_updates='{"confidence": 0.95}')

**IMPORTANT: Always call the update_entities tool first, then provide the summary.**"""

        elif intent == "update_attribute":
            return base_prompt + """
**INTENT: UPDATE ATTRIBUTE**
Your goal is to update specific attributes of an existing entity.

**CRITICAL: You MUST use the update_entities tool to modify entity attributes.**

**Tool Usage Instructions:**
1. First, identify the entity_id from the user's request or use read_entities to find it
2. Call the update_entities tool with the session_id, entity_id, and attribute_updates
3. Provide attribute_updates as a JSON string with the new attribute values
4. Confirm the attribute update was successful

**Response Structure**: After using the tool, provide a summary in JSON format:
```json
{{
  "action": "update_attribute",
  "tool_used": "update_entities",
  "entity_id": "entity_id_updated",
  "session_id": "session_id_from_context",
  "message": "Attributes updated successfully"
}}
```

**Example Tool Call:**
- update_entities(session_id="session_123", entity_id="entity_456", attribute_updates='[{"attribute_name": "risk_score", "attribute_value": 750, "attribute_type": "number"}]')

**IMPORTANT: Always call the update_entities tool first, then provide the summary.**"""

        elif intent == "delete_entity":
            return base_prompt + """
**INTENT: DELETE ENTITY**
Your goal is to delete an entity or specific attributes.

**CRITICAL: You MUST use the delete_entities tool to remove entities or attributes.**

**Tool Usage Instructions:**
1. First, identify the entity_id from the user's request or use read_entities to find it
2. Call the delete_entities tool with the session_id and appropriate parameters
3. Use entity_id to delete entire entity, or entity_id + attribute_ids to delete specific attributes
4. Confirm the deletion was successful

**Response Structure**: After using the tool, provide a summary in JSON format:
```json
{{
  "action": "delete_entity",
  "tool_used": "delete_entities",
  "entity_id": "entity_id_deleted",
  "session_id": "session_id_from_context",
  "message": "Entity/attributes deleted successfully"
}}
```

**Example Tool Call:**
- Delete entire entity: delete_entities(session_id="session_123", entity_id="entity_456")
- Delete specific attributes: delete_entities(session_id="session_123", entity_id="entity_456", attribute_ids="attr_1,attr_2")

**IMPORTANT: Always call the delete_entities tool first, then provide the summary.**"""

        elif intent == "delete_attribute":
            return base_prompt + """
**INTENT: DELETE ATTRIBUTE**
Your goal is to delete specific attributes from an entity.

**CRITICAL: You MUST use the delete_entities tool to remove specific attributes.**

**Tool Usage Instructions:**
1. First, identify the entity_id and attribute_ids from the user's request or use read_entities to find them
2. Call the delete_entities tool with the session_id, entity_id, and attribute_ids
3. Provide attribute_ids as a comma-separated string
4. Confirm the attribute deletion was successful

**Response Structure**: After using the tool, provide a summary in JSON format:
```json
{{
  "action": "delete_attribute",
  "tool_used": "delete_entities",
  "entity_id": "entity_id",
  "attribute_ids": ["attr_id1", "attr_id2"],
  "session_id": "session_id_from_context",
  "message": "Attributes deleted successfully"
}}
```

**Example Tool Call:**
- delete_entities(session_id="session_123", entity_id="entity_456", attribute_ids="attr_1,attr_2")

**IMPORTANT: Always call the delete_entities tool first, then provide the summary.**"""

        elif intent == "read":
            return base_prompt + """
**INTENT: READ ENTITIES**
Your goal is to read and display existing entities from the session.

**IMPORTANT: The entities have already been retrieved for you. Use the tool_result in the context to display them.**

**Response Structure**: Provide a user-friendly summary of the retrieved entities:
```json
{{
  "action": "read_entities",
  "tool_used": "read_entities",
  "session_id": "session_id_from_context",
  "entities_found": "number_of_entities",
  "message": "Entities retrieved and displayed successfully"
}}
```

**Instructions:**
1. Parse the tool_result from the context (it contains the entities data)
2. Display the entities in a clear, organized format
3. Show entity names, types, descriptions, and attributes
4. Provide a summary of how many entities were found

**IMPORTANT: The entities are already retrieved - just format and display them nicely.**"""

        else:
            return base_prompt + """
**INTENT: GENERAL ASSISTANCE**
Your goal is to help the user with entity management tasks.

Analyze the user's request and determine the appropriate action:
- If they want to extract entities from context → use "extract" intent
- If they want to update an entity → use "update_entity" intent  
- If they want to update attributes → use "update_attribute" intent
- If they want to delete an entity → use "delete_entity" intent
- If they want to delete attributes → use "delete_attribute" intent
- If they want to read entities → use "read" intent

Provide helpful guidance based on their request."""
    
    def detect_intent(self, message: str) -> str:
        """Detect user intent from the message"""
        message_lower = message.lower()
        
        # Intent detection patterns
        if any(word in message_lower for word in ['extract', 'create', 'identify', 'find', 'analyze', 'discover']):
            return "extract"
        elif any(word in message_lower for word in ['update', 'modify', 'change', 'edit', 'revise']):
            if any(word in message_lower for word in ['attribute', 'property', 'field']):
                return "update_attribute"
            else:
                return "update_entity"
        elif any(word in message_lower for word in ['delete', 'remove', 'clear', 'drop']):
            if any(word in message_lower for word in ['attribute', 'property', 'field']):
                return "delete_attribute"
            else:
                return "delete_entity"
        elif any(word in message_lower for word in ['read', 'show', 'display', 'list', 'get', 'retrieve', 'view']):
            return "read"
        else:
            return "extract"  # Default to extract for general requests
    
    def generate_response(self, messages: List[Any], context: str, intent: str = "extract", session_id: str = None) -> AIMessage:
        """Generate response using the LLM"""
        try:
            # Create prompt template
            system_prompt = self.get_system_prompt(intent)
            logger.info(f"🤖 System prompt length: {len(system_prompt)} characters")
            logger.info(f"🤖 System prompt preview: {system_prompt[:200]}...")
            
            # Add session context for tool usage
            session_context = f"\n\nSESSION CONTEXT:\n- Session ID: {session_id or 'unknown'}\n- Available tools: read_entities, update_entities, delete_entities, extract_credit_domain_entities, extract_data_asset_entities\n- Use these tools to interact with the session data\n\n"
            enhanced_context = context + session_context
            
            # Log the full context being sent
            logger.info(f"📋 Full context being sent to LLM: {enhanced_context}")
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                ("system", f"Current Context:\n{enhanced_context}")
            ])
            
            logger.info(f"📝 Full prompt template created with {len(prompt.messages)} message types")
            
            # Log what's being sent to the LLM
            logger.info(f"📤 Messages being sent to LLM: {[msg.content if hasattr(msg, 'content') else str(msg) for msg in messages]}")
            
            # Generate response with tools and retry logic
            # Try with tools first, fallback to no tools if empty response
            try:
                logger.info(f"🔧 Binding {len(self.tools)} tools to LLM...")
                for i, tool in enumerate(self.tools):
                    logger.info(f"  Tool {i+1}: {tool.name}")
                chain = prompt | self.llm.bind_tools(self.tools)
                logger.info("🔄 Invoking LLM chain with tools...")
            except Exception as e:
                logger.warning(f"⚠️ Tool binding failed: {e}, falling back to no tools")
                chain = prompt | self.llm
                logger.info("🔄 Invoking LLM chain without tools (fallback)...")
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"🔄 LLM attempt {attempt + 1}/{max_retries}")
                    response = chain.invoke({
                        "messages": messages
                    })
                    
                    if not response or not response.content:
                        logger.warning(f"⚠️ LLM returned empty response on attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            # Try switching to no tools on second attempt
                            if attempt == 1 and hasattr(self, 'tools'):
                                logger.info("🔄 Switching to no tools for retry...")
                                chain = prompt | self.llm
                            logger.info("🔄 Retrying...")
                            continue
                        else:
                            logger.error("❌ LLM returned empty response after all retries")
                            return AIMessage(content="I encountered an error: The LLM returned an empty response after multiple attempts. Please try again.")
                    
                    logger.info(f"✅ LLM response received: {len(response.content)} characters")
                    
                    # Check if the response contains tool calls
                    if hasattr(response, 'tool_calls') and response.tool_calls:
                        logger.info(f"🔧 LLM made {len(response.tool_calls)} tool calls:")
                        for i, tool_call in enumerate(response.tool_calls):
                            logger.info(f"  Tool call {i+1}: {tool_call['name']} with args: {tool_call.get('args', {})}")
                    else:
                        logger.info("⚠️ LLM did not make any tool calls")
                    
                    return response
                    
                except Exception as e:
                    logger.error(f"❌ Error during LLM invocation (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        logger.info("🔄 Retrying due to error...")
                        continue
                    else:
                        logger.error(f"❌ Failed after {max_retries} attempts")
                        return AIMessage(content=f"I encountered an error while processing your request: {str(e)}. Please try again.")
            
        except Exception as e:
            logger.error(f"❌ Error in LLM generation: {e}")
            return AIMessage(content=f"I encountered an error while processing your request: {str(e)}. Please try again or provide more specific information.")


class CreditDomainEntityExtractionAgent:
    """AI Agent for Credit Domain entity extraction with chat/QA capabilities using LangGraph"""
    
    def __init__(self, project_id: str, location: str = "us-central1", session_manager: Optional[SessionManager] = None):
        """Initialize the Credit Domain Entity Extraction Agent"""
        print(f"🚀 Initializing CreditDomainEntityExtractionAgent with project: {project_id}")
        self.project_id = project_id
        self.location = location
        
        # Initialize components
        self.llm_manager = LLMManager(project_id, location)
        self.entity_extractor = EntityExtractor()
        
        # Initialize session manager - use Firestore by default
        if session_manager is not None:
            self.session_manager = session_manager
        else:
            # Create Firestore session manager by default
            session_config = SessionConfig(
                manager_type="firestore",
                firestore_project_id=project_id
            )
            self.session_manager = create_session_manager_from_config(session_config)
            print(f"🗄️ Session manager initialized: {type(self.session_manager).__name__}")
        
        # Initialize entity manager
        self.entity_manager = EntityManager(self.session_manager)
        
        # Set entity manager in LLM manager for tools
        self.llm_manager.entity_manager = self.entity_manager
        
        # Re-initialize tools with the entity manager
        self.llm_manager.tools = self.llm_manager._initialize_tools()
        
        print("🤖 LLM initialized successfully")
        print("🔧 Starting graph construction...")
        self.graph = self._build_graph()
        print("🔧 Graph construction completed")
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow following best practices"""
        
        # Define the workflow with proper state schema
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_request", self._analyze_request)
        workflow.add_node("detect_intent", self._detect_intent)
        workflow.add_node("route_action", self._route_action)
        workflow.add_node("extract_entities", self._extract_entities)
        workflow.add_node("update_entities", self._update_entities)
        workflow.add_node("delete_entities", self._delete_entities)
        workflow.add_node("read_entities", self._read_entities)
        workflow.add_node("generate_response", self._generate_response)
        
        # Add edges
        workflow.add_edge("analyze_request", "detect_intent")
        workflow.add_edge("detect_intent", "route_action")
        
        # Conditional routing based on intent
        workflow.add_conditional_edges(
            "route_action",
            self._route_condition,
            {
                "extract": "extract_entities",
                "update_entity": "update_entities", 
                "update_attribute": "update_entities",
                "delete_entity": "delete_entities",
                "delete_attribute": "delete_entities",
                "read": "read_entities"
            }
        )
        
        workflow.add_edge("extract_entities", "generate_response")
        workflow.add_edge("update_entities", "generate_response")
        workflow.add_edge("delete_entities", "generate_response")
        workflow.add_edge("read_entities", "generate_response")
        workflow.add_edge("generate_response", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_request")
        
        return workflow.compile()
    
    def _detect_intent(self, state: AgentState) -> AgentState:
        """Detect user intent from the message"""
        logger.info("🔍 INTENT DETECTION: Starting intent detection...")
        messages = state["messages"]
        
        # Find the last HumanMessage (user message)
        last_user_message = None
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                last_user_message = message
                break
        
        logger.info(f"🔍 INTENT DETECTION: Messages count: {len(messages)}")
        logger.info(f"🔍 INTENT DETECTION: Last user message type: {type(last_user_message)}")
        
        if not last_user_message:
            logger.info("🔍 INTENT DETECTION: No valid user message, defaulting to extract")
            state["user_intent"] = "extract"
            state["action_required"] = "extract"
            return state
        
        logger.info(f"🔍 INTENT DETECTION: Message content: {last_user_message.content}")
        
        # Detect intent from the message
        intent = self.llm_manager.detect_intent(last_user_message.content)
        state["user_intent"] = intent
        state["action_required"] = intent
        
        logger.info(f"🎯 Detected user intent: {intent}")
        return state
    
    def _route_action(self, state: AgentState) -> AgentState:
        """Route to appropriate action based on intent"""
        intent = state.get("user_intent", "extract")
        action = state.get("action_required", "extract")
        
        logger.info(f"🔄 Routing to action: {action}")
        
        # The routing is handled by the graph edges
        # This method just logs the routing decision
        return state
    
    def _route_condition(self, state: AgentState) -> str:
        """Determine which node to route to based on intent"""
        intent = state.get("user_intent", "extract")
        logger.info(f"🎯 Routing condition: {intent}")
        return intent
    
    def _update_entities(self, state: AgentState) -> AgentState:
        """Handle entity update operations"""
        logger.info("✏️ Processing entity update request")
        
        # For now, just pass through to generate_response
        # In a full implementation, this would call the update_entities tool
        return state
    
    def _delete_entities(self, state: AgentState) -> AgentState:
        """Handle entity deletion operations"""
        logger.info("🗑️ Processing entity deletion request")
        
        # For now, just pass through to generate_response
        # In a full implementation, this would call the delete_entities tool
        return state
    
    def _read_entities(self, state: AgentState) -> AgentState:
        """Handle entity read operations"""
        logger.info("📖 Processing entity read request")
        
        try:
            # Call the read_entities tool directly
            session_id = state.get("session_id", "unknown")
            logger.info(f"📖 Reading entities for session: {session_id}")
            
            # Find the read_entities tool
            read_tool = None
            for tool in self.llm_manager.tools:
                if tool.name == "read_entities":
                    read_tool = tool
                    break
            
            if read_tool:
                logger.info("🔧 Calling read_entities tool directly...")
                result = read_tool.invoke({"session_id": session_id})
                logger.info(f"📖 Tool result: {result[:200]}...")
                
                # Add the tool result to the state for the LLM to use
                state["tool_result"] = result
                state["tool_used"] = "read_entities"
            else:
                logger.error("❌ read_entities tool not found")
                state["tool_result"] = "Error: read_entities tool not available"
                state["tool_used"] = "none"
                
        except Exception as e:
            logger.error(f"❌ Error in _read_entities: {e}")
            state["tool_result"] = f"Error reading entities: {str(e)}"
            state["tool_used"] = "error"
        
        return state
    
    def _analyze_request(self, state: AgentState) -> AgentState:
        """Analyze the user request and determine next steps"""
        messages = state["messages"]
        last_message = messages[-1] if messages else None
        
        if not last_message or not isinstance(last_message, HumanMessage):
            return state
        
        # Check if this is the first message (welcome)
        if len(messages) == 1:
            # Only show welcome if no context is provided
            if not state.get("selected_bc3_fields") and not state.get("selected_asset_columns"):
                welcome_message = AIMessage(content="Hello! I am here to help you create/extract custom entities. Before you ask me to create the required entities, please select the right Credit Domain (BC3) entities alongside relevant data assets to provide more context. This will help me better understand your data and extract the most relevant entities for you.")
                state["messages"].append(welcome_message)
                return state
        
        # Check if user has provided BC3 fields and asset columns
        if not state.get("selected_bc3_fields") and not state.get("selected_asset_columns"):
            guidance_message = AIMessage(content="I notice you haven't selected any BC3 fields or asset columns yet. To help you extract entities effectively, please provide:\n\n1. **BC3 Fields**: Select the relevant business dictionary fields from credit domain segments\n2. **Asset Columns**: Choose the specific columns from data assets that contain the context you want to analyze\n\nOnce you provide these, I can help you extract custom entities from your data!")
            state["messages"].append(guidance_message)
            return state
        
        return state
    
    def _extract_entities(self, state: AgentState) -> AgentState:
        """Let the LLM decide entities based on the selected context"""
        try:
            logger.info("🔍 Starting entity extraction workflow...")
            logger.info(f"📝 Current message: {state.get('message', 'No message')}")
            logger.info(f"📊 Selected BC3 fields: {len(state.get('selected_bc3_fields', []))}")
            logger.info(f"🗄️ Selected asset columns: {len(state.get('selected_asset_columns', []))}")
            
            # For now, we'll let the LLM analyze the context and extract entities
            # The actual entity extraction will happen in the response generation
            # where the LLM provides structured entity information
            state["extracted_entities"] = []
            
            logger.info("✅ Entity extraction workflow completed (LLM-driven)")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error in entity extraction: {e}")
            error_entity = {
                "entity_type": EntityType.METADATA,
                "entity_name": "error",
                "entity_value": str(e),
                "confidence": 0.0,
                "source_field": "system",
                "description": f"Error in entity extraction: {str(e)}",
                "context_provider": "credit_domain"
            }
            state["extracted_entities"] = [error_entity]
            return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate the final response using the LLM"""
        try:
            logger.info("🤖 Starting LLM response generation...")
            
            # Prepare context for the LLM
            context = self._prepare_context(state)
            logger.info(f"📋 Prepared context length: {len(context)} characters")
            logger.info(f"📋 Context preview: {context[:200]}...")
            
            # Generate response using LLM manager with intent
            intent = state.get("user_intent", "extract")
            session_id = state.get("session_id", "unknown")
            logger.info(f"🔄 Calling LLM with context and intent: {intent}")
            response = self.llm_manager.generate_response(state["messages"], context, intent, session_id)
            logger.info(f"🤖 LLM response received: {len(response.content)} characters")
            logger.info(f"🤖 Response preview: {response.content[:200]}...")
            
            # Add response to messages
            state["messages"].append(response)
            
            logger.info("✅ Response generation completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error in response generation: {e}")
            error_message = AIMessage(content=f"I encountered an error while processing your request: {str(e)}. Please try again or provide more specific information.")
            state["messages"].append(error_message)
            return state
    
    def _prepare_context(self, state: AgentState) -> str:
        """Prepare context information for the LLM"""
        logger.info("🔧 Preparing context for LLM...")
        context_parts = []
        
        # Add selected BC3 fields info
        if state.get("selected_bc3_fields"):
            logger.info(f"📊 Processing {len(state['selected_bc3_fields'])} selected BC3 fields")
            context_parts.append("Selected BC3 Fields:")
            for field_data in state["selected_bc3_fields"]:
                field = field_data["field"]
                segment = field_data["segment_context"]
                context_parts.append(f"  • {field['description']} ({segment['segment_name']})")
                context_parts.append(f"    Definition: {field['definition']}")
                if field.get('known_implementations'):
                    context_parts.append(f"    Implementations: {', '.join(field['known_implementations'])}")
                if field.get('valid_values'):
                    context_parts.append(f"    Valid Values: {', '.join(field['valid_values'])}")
                if field.get('notes'):
                    context_parts.append(f"    Notes: {field['notes']}")
                context_parts.append("")
        
        # Add selected asset columns info
        if state.get("selected_asset_columns"):
            logger.info(f"🗄️ Processing {len(state['selected_asset_columns'])} selected asset columns")
            context_parts.append("Selected Asset Columns:")
            for column_data in state["selected_asset_columns"]:
                column = column_data["column"]
                asset = column_data["asset_context"]
                context_parts.append(f"  • {column['column_name']} ({asset['asset_name']})")
                context_parts.append(f"    Asset: {asset['asset_name']}")
                context_parts.append(f"    Workspace: {asset['workspace_name']}")
                context_parts.append(f"    BigQuery Table: {asset['big_query_table_name']}")
                context_parts.append("")
        
        # Add extracted entities info if any
        if state.get("extracted_entities"):
            context_parts.append(f"Previously Extracted Entities: {len(state['extracted_entities'])}")
        
        # Add tool result if available
        if state.get("tool_result"):
            context_parts.append(f"Tool Result: {state['tool_result']}")
        
        final_context = "\n".join(context_parts) if context_parts else "No context available"
        logger.info(f"📋 Final context prepared: {len(final_context)} characters")
        return final_context
    
    def _parse_llm_response_for_entities(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse the LLM response to extract structured entities"""
        try:
            logger.info("🔍 Parsing LLM response for entities...")
            entities = []
            
            # Try to parse as JSON first
            try:
                import json
                # Clean the response text - remove markdown code blocks if present
                cleaned_response = response_text.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]  # Remove ```
                cleaned_response = cleaned_response.strip()
                
                response_data = json.loads(cleaned_response)
                logger.info("✅ Successfully parsed JSON response")
                
                # Extract entities from JSON structure
                if "extracted_entities" in response_data:
                    for entity_data in response_data["extracted_entities"]:
                        try:
                            # Map entity type from string to EntityType enum
                            entity_type_str = entity_data.get("entity_type", "METADATA")
                            mapped_entity_type = self._map_entity_type(entity_type_str)
                            
                            # Create entity object with new structure
                            entity = {
                                "entity_id": f"entity_{uuid.uuid4().hex[:8]}",
                                "entity_type": mapped_entity_type,
                                "entity_name": entity_data.get("entity_name") or "Unknown",
                                "entity_value": entity_data.get("entity_value") or "",
                                "confidence": float(entity_data.get("confidence") or 0.8),
                                "source_field": entity_data.get("source_field") or "Unknown",
                                "description": entity_data.get("description") or "",
                                "relationships": entity_data.get("relationships", {}),
                                "context_provider": "credit_domain",
                                "attributes": [],  # Will be populated with attributes if provided
                                "state_version": 1
                            }
                            
                            # Add attributes if provided in the entity data
                            if "attributes" in entity_data and entity_data["attributes"]:
                                for attr_data in entity_data["attributes"]:
                                    attribute = {
                                        "attribute_id": f"attr_{uuid.uuid4().hex[:8]}",
                                        "attribute_name": attr_data.get("attribute_name", ""),
                                        "attribute_value": attr_data.get("attribute_value", ""),
                                        "attribute_type": attr_data.get("attribute_type", "string"),
                                        "confidence": float(attr_data.get("confidence", 0.8)),
                                        "source_field": attr_data.get("source_field", ""),
                                        "description": attr_data.get("description", ""),
                                        "metadata": attr_data.get("metadata", {})
                                    }
                                    entity["attributes"].append(attribute)
                            
                            entities.append(entity)
                            logger.info(f"✅ Parsed JSON entity: {entity['entity_name']} ({entity_type_str}) with {len(entity['relationships'])} relationships")
                        
                        except Exception as e:
                            logger.error(f"❌ Error parsing individual JSON entity: {e}")
                            continue
                
                    logger.info(f"✅ Successfully parsed {len(entities)} entities from JSON response")
                    return entities
                    
                else:
                    logger.warning("⚠️ No 'extracted_entities' found in JSON response")
                    
            except json.JSONDecodeError as e:
                logger.info(f"⚠️ Response is not valid JSON: {e}")
                logger.info("🔄 Falling back to text parsing...")
                
                # Fallback: Extract basic entities from context if LLM fails
                if "error" in response_text.lower() or "empty response" in response_text.lower():
                    logger.info("🔄 LLM failed, attempting fallback entity extraction from context...")
                    entities = self._extract_fallback_entities()
            
            return entities
            
        except Exception as e:
            logger.error(f"❌ Error parsing LLM response for entities: {e}")
            return []
    
    def _extract_fallback_entities(self) -> List[Dict[str, Any]]:
        """Extract basic entities from context when LLM fails"""
        try:
            logger.info("🔄 Extracting fallback entities from context...")
            entities = []
            
            # Extract entities from selected BC3 fields
            if hasattr(self, 'current_context') and self.current_context:
                # This would be populated with the current context
                # For now, return a generic entity
                entities.append({
                    "entity_type": EntityType.METADATA,
                    "entity_name": "Context Analysis",
                    "entity_value": "LLM processing failed, using context-based extraction",
                    "confidence": 0.7,
                    "source_field": "fallback_system",
                    "description": "Entities extracted from context due to LLM failure",
                    "context_provider": "credit_domain"
                })
            
            logger.info(f"✅ Extracted {len(entities)} fallback entities")
            return entities
            
        except Exception as e:
            logger.error(f"❌ Error in fallback entity extraction: {e}")
            return []
    
    def _map_entity_type(self, entity_type: str) -> EntityType:
        """Map entity type string to EntityType enum"""
        entity_type_lower = entity_type.lower()
        
        if "bc3" in entity_type_lower or "field" in entity_type_lower:
            return EntityType.FIELD
        elif "asset" in entity_type_lower or "column" in entity_type_lower:
            return EntityType.COLUMN
        elif "segment" in entity_type_lower:
            return EntityType.SEGMENT
        elif "value" in entity_type_lower:
            return EntityType.VALUE
        elif "implementation" in entity_type_lower:
            return EntityType.METADATA
        elif "business" in entity_type_lower and "metric" in entity_type_lower:
            return EntityType.BUSINESS_METRIC
        elif "relationship" in entity_type_lower:
            return EntityType.RELATIONSHIP
        elif "derived" in entity_type_lower and "insight" in entity_type_lower:
            return EntityType.DERIVED_INSIGHT
        elif "operational" in entity_type_lower and "rule" in entity_type_lower:
            return EntityType.OPERATIONAL_RULE
        else:
            return EntityType.METADATA
    
    def _generate_chat_output(self, entities: List[ExtractedEntity], response_text: str) -> str:
        """Generate formatted chat output with bulleted entities and relationships"""
        try:
            output_lines = []
            
            # Add the main response
            if response_text and not response_text.startswith("```json"):
                output_lines.append("🤖 **AI Response:**")
                output_lines.append(response_text)
                output_lines.append("")
            
            # Add extracted entities section
            if entities:
                output_lines.append("🔍 **Extracted Entities & Relationships:**")
                output_lines.append("")
                
                # Group entities by type
                entity_groups = {}
                for entity in entities:
                    entity_type = entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type)
                    if entity_type not in entity_groups:
                        entity_groups[entity_type] = []
                    entity_groups[entity_type].append(entity)
                
                # Format each group
                for entity_type, group_entities in entity_groups.items():
                    # Format entity type header
                    type_header = entity_type.replace('_', ' ').title()
                    output_lines.append(f"**{type_header}s:**")
                    
                    for entity in group_entities:
                        # Main entity bullet
                        confidence_emoji = "🟢" if entity.confidence >= 0.9 else "🟡" if entity.confidence >= 0.7 else "🔴"
                        output_lines.append(f"  • **{entity.entity_name}** {confidence_emoji} (Confidence: {entity.confidence:.2f})")
                        
                        # Entity details
                        if entity.description:
                            output_lines.append(f"    - Description: {entity.description}")
                        if entity.source_field:
                            output_lines.append(f"    - Source: {entity.source_field}")
                        if entity.entity_value:
                            output_lines.append(f"    - Value: {entity.entity_value}")
                        
                        # Relationships
                        if entity.relationships:
                            output_lines.append(f"    - Relationships:")
                            for rel_type, rel_target in entity.relationships.items():
                                output_lines.append(f"      • {rel_type}: {rel_target}")
                        
                        output_lines.append("")
                
                # Add summary
                output_lines.append(f"📊 **Summary:** Extracted {len(entities)} entities across {len(entity_groups)} categories")
            else:
                output_lines.append("⚠️ **No entities extracted** - Please check your input data and try again.")
            
            return "\n".join(output_lines)
            
        except Exception as e:
            logger.error(f"❌ Error generating chat output: {e}")
            return f"Error generating formatted output: {str(e)}"
    
    def process_request(self, request: AgentRequest) -> AgentResponse:
        """Process a chat request and return response"""
        start_time = time.time()
        
        try:
            # Get or create session
            session_id = request.session_id or str(uuid.uuid4())
            chat_state = self._get_or_create_session(session_id)
            
            # Update session with new data if provided
            if request.credit_domain_data:
                chat_state.selected_segments = [seg.model_dump() for seg in request.credit_domain_data]
            if request.data_assets:
                chat_state.selected_assets = [asset.model_dump() for asset in request.data_assets]
            
            # Handle selected BC3 fields and asset columns
            selected_bc3_fields = request.selected_bc3_fields or []
            selected_asset_columns = request.selected_asset_columns or []
            
            # Add user message to chat history
            user_message = ChatMessage(
                role="user",
                content=request.message,
                timestamp=datetime.now()
            )
            chat_state.messages.append(user_message)
            
            # Prepare state for LangGraph
            graph_state = AgentState(
                messages=[HumanMessage(content=request.message)],
                session_id=session_id,
                selected_segments=chat_state.selected_segments,
                selected_assets=chat_state.selected_assets,
                selected_bc3_fields=selected_bc3_fields,
                selected_asset_columns=selected_asset_columns,
                extracted_entities=[],
                user_intent="extract",
                action_required="extract",
                metadata=request.metadata
            )
            
            # Run the graph
            logger.info("🚀 Invoking LangGraph workflow...")
            result = self.graph.invoke(graph_state)
            logger.info(f"✅ LangGraph workflow completed. Result keys: {list(result.keys())}")
            
            # Update chat state with results
            logger.info(f"📊 Updating chat state with {len(result.get('extracted_entities', []))} entities")
            chat_state.extracted_entities = [
                ExtractedEntity(**entity) for entity in result["extracted_entities"]
            ]
            
            # Get the last AI message
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            
            if not ai_messages:
                logger.error("❌ No AI messages found in result")
                response_text = "I'm here to help you extract entities from your Credit Domain data and data assets!"
            else:
                last_ai_message = ai_messages[-1]
                response_text = last_ai_message.content if last_ai_message.content else "I'm here to help you extract entities from your Credit Domain data and data assets!"
                logger.info(f"📝 AI response text: {len(response_text)} characters")
                
                # Parse entities from the LLM response
                logger.info("🔍 Parsing entities from LLM response...")
                parsed_entities = self._parse_llm_response_for_entities(response_text)
                logger.info(f"✅ Parsed {len(parsed_entities)} entities from LLM response")
                
                # Update chat state with parsed entities
                chat_state.extracted_entities = [
                    ExtractedEntity(**entity) for entity in parsed_entities
                ]
            
            # Save session
            self.session_manager.save_session(session_id, chat_state)
            
            # Generate formatted chat output
            chat_output = self._generate_chat_output(chat_state.extracted_entities, response_text)
            
            processing_time = time.time() - start_time
            
            return AgentResponse(
                response=response_text,
                chat_output=chat_output,
                extracted_entities=chat_state.extracted_entities,
                chat_state=chat_state,
                confidence_score=0.9,  # Default confidence
                processing_time=processing_time,
                metadata={"session_id": session_id}
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return AgentResponse(
                response=f"Error processing request: {str(e)}",
                chat_output=f"❌ **Error:** {str(e)}",
                extracted_entities=[],
                chat_state=ChatState(session_id=request.session_id or str(uuid.uuid4())),
                confidence_score=0.0,
                processing_time=processing_time,
                metadata={"error": str(e)}
            )
    
    def _get_or_create_session(self, session_id: str) -> ChatState:
        """Get existing session or create new one"""
        existing_session = self.session_manager.get_session(session_id)
        if existing_session:
            return existing_session
        
        new_session = ChatState(
            session_id=session_id,
            messages=[],
            selected_segments=[],
            selected_assets=[],
            selected_bc3_fields=[],
            selected_asset_columns=[],
            extracted_entities=[],
            metadata={}
        )
        self.session_manager.save_session(session_id, new_session)
        return new_session
    
    def get_session(self, session_id: str) -> Optional[ChatState]:
        """Get session by ID"""
        return self.session_manager.get_session(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session by ID"""
        return self.session_manager.delete_session(session_id)
