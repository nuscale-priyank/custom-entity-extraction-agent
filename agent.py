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
    ExtractedEntity, EntityType, ChatMessage, AgentRequest, AgentResponse, 
    ChatState, GenericDocument, GenericDataField
)
from session_managers import SessionManager, InMemorySessionManager


class AgentState(TypedDict):
    """State schema for LangGraph - following LangGraph best practices"""
    messages: Annotated[List[Any], "Chat messages"]
    session_id: Annotated[str, "Session identifier"]
    selected_segments: Annotated[List[Dict], "Selected credit domain segments"]
    selected_assets: Annotated[List[Dict], "Selected data assets"]
    selected_bc3_fields: Annotated[List[Dict], "Selected BC3 fields with context"]
    selected_asset_columns: Annotated[List[Dict], "Selected asset columns with context"]
    extracted_entities: Annotated[List[Dict], "Extracted entities"]
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
    
    def _initialize_llm(self) -> ChatVertexAI:
        """Initialize Vertex AI LLM"""
        return ChatVertexAI(
            model_name="gemini-2.5-flash-lite",
            project=self.project_id,
            location=self.location,
            temperature=0.1,
            max_output_tokens=2048
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the Credit Domain agent"""
        return """You are PBS Buddy – a specialized friendly chatbot designed to help users create and extract custom entities from Credit Domain (BC3) data and data assets.

IMPORTANT: You MUST extract NEW, MEANINGFUL entities based on the provided context. Do not just echo what's already there.

CRITICAL: The context is ALREADY provided below. Do not ask for more context.

⚠️ WARNING: If you see "Selected BC3 Fields:" and "Selected Asset Columns:" below, the context IS ALREADY PROVIDED. Do not say "Once you provide the context" or similar phrases.

Your primary responsibilities:

1. **MANDATORY NEW Entity Extraction**: 
   - You MUST analyze the selected BC3 fields and asset columns that are ALREADY provided
   - You MUST extract NEW entities that are NOT directly in the context
   - Focus on DERIVED entities, RELATIONSHIPS, and BUSINESS INSIGHTS
   - Each entity should represent a NEW concept derived from the context

2. **Context Analysis**: 
   - Analyze the selected BC3 fields and asset columns provided by the user
   - Understand the relationships between different data elements
   - Identify business-relevant entities based on the selected context

3. **Intelligent Entity Extraction**:
   - Based on the user's message and selected context, determine what entities are relevant
   - Extract entities that make business sense given the combination of BC3 fields and asset columns
   - Consider the relationships between different data elements when extracting entities

4. **Response Structure**: Your response MUST include:
   - "EXTRACTED ENTITIES:" section with numbered list
   - For each entity: type, name, value, confidence, source, business significance
   - Analysis of why these entities are relevant
   - Suggestions for additional context

5. **NEW Entity Examples** (DO NOT extract these exact examples - create your own based on context):
   - **Derived Business Metrics**: "Credit Utilization Ratio" (debt/limit), "Risk Score" (credit_score + debt analysis)
   - **Relationship Entities**: "Account-Credit Correlation" (how account type affects credit score)
   - **Operational Insights**: "Account Health Status" (based on multiple factors), "Risk Category" (high/medium/low)
   - **Business Rules**: "Credit Limit Recommendations" (based on score + debt), "Account Monitoring Triggers"
   - **Predictive Entities**: "Default Risk Probability", "Credit Limit Increase Eligibility"

6. **Quality Requirements**:
   - Minimum 2 entities per response
   - Confidence scores 0.7-1.0 for clear context
   - Business-focused explanations
   - No generic responses like "Let me know if you have questions"

Remember: You are an entity extraction agent. Extract NEW entities based on the context provided. Do not give generic responses.

⚠️ CRITICAL: DO NOT extract entities that are already in the context. Instead, create NEW entities that represent:
- Business insights derived from the context
- Relationships between different context elements
- Operational rules and business logic
- Predictive or analytical entities

FORMAT YOUR RESPONSE LIKE THIS:
EXTRACTED ENTITIES:
1. [NEW Entity Type]: [NEW Entity Name] - [Derived Value] (Confidence: X.X)
   Source: [Combination of BC3 Fields and Asset Columns]
   Business Significance: [Explanation of why this NEW entity is valuable]

2. [NEW Entity Type]: [NEW Entity Name] - [Derived Value] (Confidence: X.X)
   Source: [Combination of BC3 Fields and Asset Columns]
   Business Significance: [Explanation of why this NEW entity is valuable]

ANALYSIS: [Explain how these NEW entities provide value beyond the original context]

The context is provided below - use it to create NEW insights.

CONTEXT FORMAT:
- If you see "Selected BC3 Fields:" followed by field details, that IS your context
- If you see "Selected Asset Columns:" followed by column details, that IS your context
- Extract entities from these fields and columns immediately
- Do not ask for more context - it's already there!"""
    
    def generate_response(self, messages: List[Any], context: str) -> AIMessage:
        """Generate response using the LLM"""
        try:
            # Create prompt template
            system_prompt = self.get_system_prompt()
            logger.info(f"🤖 System prompt length: {len(system_prompt)} characters")
            logger.info(f"🤖 System prompt preview: {system_prompt[:200]}...")
            
            # Log the full context being sent
            logger.info(f"📋 Full context being sent to LLM: {context}")
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                ("system", f"Current Context:\n{context}")
            ])
            
            logger.info(f"📝 Full prompt template created with {len(prompt.messages)} message types")
            
            # Log what's being sent to the LLM
            logger.info(f"📤 Messages being sent to LLM: {[msg.content if hasattr(msg, 'content') else str(msg) for msg in messages]}")
            
            # Generate response with retry logic
            chain = prompt | self.llm
            logger.info("🔄 Invoking LLM chain...")
            
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
                            logger.info("🔄 Retrying...")
                            continue
                        else:
                            logger.error("❌ LLM returned empty response after all retries")
                            return AIMessage(content="I encountered an error: The LLM returned an empty response after multiple attempts. Please try again.")
                    
                    logger.info(f"✅ LLM response received: {len(response.content)} characters")
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
        self.session_manager = session_manager or InMemorySessionManager()
        
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
        workflow.add_node("extract_entities", self._extract_entities)
        workflow.add_node("generate_response", self._generate_response)
        
        # Add edges
        workflow.add_edge("analyze_request", "extract_entities")
        workflow.add_edge("extract_entities", "generate_response")
        workflow.add_edge("generate_response", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_request")
        
        return workflow.compile()
    
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
            
            # Generate response using LLM manager
            logger.info("🔄 Calling LLM with context...")
            response = self.llm_manager.generate_response(state["messages"], context)
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
        
        final_context = "\n".join(context_parts) if context_parts else "No context available"
        logger.info(f"📋 Final context prepared: {len(final_context)} characters")
        return final_context
    
    def _parse_llm_response_for_entities(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse the LLM response to extract structured entities"""
        try:
            logger.info("🔍 Parsing LLM response for entities...")
            entities = []
            
            # Look for the EXTRACTED ENTITIES section
            if "EXTRACTED ENTITIES:" in response_text:
                # Split by entity numbers (1., 2., 3., etc.)
                entity_sections = response_text.split("EXTRACTED ENTITIES:")[1].split("ANALYSIS:")[0]
                
                # Find numbered entities (1., 2., 3., etc.)
                import re
                entity_matches = re.findall(r'(\d+)\.\s*([^:]+):\s*([^-]+)\s*-\s*([^(]+)', entity_sections)
                
                for match in entity_matches:
                    try:
                        entity_num, entity_type, entity_name, entity_value = match
                        
                        # Extract confidence score if present
                        confidence_match = re.search(r'Confidence:\s*([\d.]+)', entity_sections)
                        confidence = float(confidence_match.group(1)) if confidence_match else 0.8
                        
                        # Extract source if present
                        source_match = re.search(r'Source:\s*([^\n]+)', entity_sections)
                        source = source_match.group(1).strip() if source_match else "Unknown"
                        
                        # Extract business significance if present
                        significance_match = re.search(r'Business Significance:\s*([^\n]+)', entity_sections)
                        significance = significance_match.group(1).strip() if significance_match else "Not specified"
                        
                        entity = {
                            "entity_type": self._map_entity_type(entity_type.strip()),
                            "entity_name": entity_name.strip(),
                            "entity_value": entity_value.strip(),
                            "confidence": confidence,
                            "source_field": source,
                            "description": significance,
                            "context_provider": "credit_domain"
                        }
                        
                        entities.append(entity)
                        logger.info(f"✅ Parsed entity: {entity_name.strip()} ({entity_type.strip()})")
                        
                    except Exception as e:
                        logger.error(f"❌ Error parsing individual entity: {e}")
                        continue
                
                logger.info(f"✅ Successfully parsed {len(entities)} entities from LLM response")
            else:
                logger.warning("⚠️ No EXTRACTED ENTITIES section found in LLM response")
                
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
        else:
            return EntityType.METADATA
    
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
            
            processing_time = time.time() - start_time
            
            return AgentResponse(
                response=response_text,
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
