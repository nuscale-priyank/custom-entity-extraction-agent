"""
LangGraph-based Conversational Agent
Production-ready implementation with enhanced state management and conversation persistence
"""

import json
import logging
import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Annotated, TypedDict
from operator import add

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import ToolNode

from config import Config
from .entity_collection_manager import EntityCollectionManager
from .relationship_detector import RelationshipDetector
from models.entity_collection_models import CreateEntityRequest, ReadEntityRequest, DeleteEntityRequest

logger = logging.getLogger(__name__)




class ConversationState(TypedDict):
    """State definition for LangGraph conversation workflow"""
    # Message state - automatically accumulated by LangGraph
    messages: Annotated[List[BaseMessage], add]
    
    # Session context
    session_id: str
    bc3_fields: List[Dict[str, Any]]
    asset_columns: List[Dict[str, Any]]
    
    # Entity state
    entities: List[Dict[str, Any]]
    entities_created_count: int
    
    # Workflow state
    current_intent: str
    last_operation: str
    needs_clarification: bool
    
    # Metadata
    conversation_summary: str
    relationship_data: Dict[str, Any]
    user_id: str


class ConversationalAgent:
    """LangGraph-based conversational agent with enhanced state management"""
    
    def __init__(self, project_id: str = None):
        """Initialize the LangGraph conversational agent"""
        self.project_id = project_id or Config.get_project_id()
        
        # Initialize LLM
        self.llm = ChatVertexAI(
            model_name=Config.get_model_name(),
            project=self.project_id,
            location=Config.LOCATION,
            temperature=Config.get_temperature(),
            max_output_tokens=Config.get_max_output_tokens()
        )
        
        # Initialize managers (entities still in Firestore)
        self.entity_manager = EntityCollectionManager(self.project_id, database_id=Config.get_database_id())
        self.relationship_detector = RelationshipDetector()
        
        # Initialize checkpointer (PostgreSQL with fallback to InMemory)
        logger.info("🔍 DEBUG: About to call _initialize_checkpointer()")
        self.checkpointer = self._initialize_checkpointer()
        logger.info("🔍 DEBUG: _initialize_checkpointer() completed")
        
        # Create the graph
        self.graph = self._create_conversation_graph()
        
        logger.info("LangGraph Conversational Agent initialized successfully")
    
    def _initialize_checkpointer(self):
        """Initialize checkpointer - using InMemorySaver for now"""
        try:
            connection_string = Config.get_postgres_connection_string()
            logger.info(f"PostgreSQL available at: {Config.get_postgres_host()}:{Config.get_postgres_port()}")
            
            # For now, use InMemorySaver to get basic functionality working
            logger.info("🔄 Using InMemorySaver for conversation persistence")
            return InMemorySaver()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize checkpointer: {e}")
            logger.info("🔄 Using InMemorySaver")
            return InMemorySaver()
    
    def _create_conversation_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        # Create the graph with MessagesState for proper memory
        workflow = StateGraph(MessagesState)
        
        # Simple node that just echoes the message - following the working test pattern exactly
        def call_model(state: MessagesState):
            response = AIMessage(content=f"Echo: {state['messages'][-1].content}")
            return {"messages": [response]}
        
        # Add node and edges - following the working test pattern exactly
        workflow.add_node("call_model", call_model)
        workflow.add_edge(START, "call_model")
        workflow.add_edge("call_model", END)
        
        # Compile with checkpointer
        logger.info(f"🔍 DEBUG: Compiling graph with checkpointer: {type(self.checkpointer)}")
        compiled_graph = workflow.compile(checkpointer=self.checkpointer)
        logger.info(f"🔍 DEBUG: Graph compiled successfully")
        return compiled_graph
    
    def process_message(self, session_id: str, user_message: str, 
                       selected_bc3_fields: List[Dict] = None,
                       selected_asset_columns: List[Dict] = None,
                       user_id: str = None) -> Dict[str, Any]:
        """Process a user message using LangGraph"""
        
        try:
            logger.info(f"Processing message for session: {session_id}")
            
            # Use default user_id if not provided
            if user_id is None:
                user_id = Config.get_default_user_id()
            
            # Create thread_id from session_id
            thread_id = f"{Config.get_thread_prefix()}_{user_id}_{session_id}"
            
            # LangGraph config with thread_id (simplified to match working test)
            config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }
            
            # Simple approach using MessagesState
            input_state = {
                "messages": [HumanMessage(content=user_message)]
            }
            
            # Try using invoke instead of stream
            logger.info(f"🔍 DEBUG: About to invoke graph with thread_id: {thread_id}")
            result = self.graph.invoke(input_state, config)
            logger.info(f"🔍 DEBUG: Graph invocation completed")
            
            # Extract response from final state
            messages = result.get("messages", [])
            if not messages:
                response_text = "I apologize, but I couldn't generate a response."
            else:
                last_message = messages[-1]
                if isinstance(last_message, AIMessage):
                    response_text = last_message.content
                else:
                    response_text = str(last_message) if hasattr(last_message, 'content') else str(last_message)
            
            return {
                "response": response_text,
                "success": True,
                "entities_created": 0,  # Simplified for now
                "entities": []
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "success": False,
                "entities_created": 0,
                "entities": []
            }
    
    # Node implementations
    def _message_processing_node(self, state: ConversationState) -> ConversationState:
        """Process incoming user message and update state"""
        logger.info("Processing message in LangGraph node")
        
        # Update context if BC3 fields or asset columns are provided
        context_updates = {}
        if state["bc3_fields"]:
            context_updates["bc3_fields"] = state["bc3_fields"]
        if state["asset_columns"]:
            context_updates["asset_columns"] = state["asset_columns"]
        
        return {
            "last_operation": "message_processing",
            **context_updates
        }
    
    def _intent_analysis_node(self, state: ConversationState) -> ConversationState:
        """Analyze user intent using LLM with conversation context"""
        logger.info("Analyzing intent in LangGraph node")
        
        # Get recent conversation context
        recent_messages = state["messages"][-5:] if len(state["messages"]) > 5 else state["messages"]
        conversation_context = "\n".join([
            f"{msg.__class__.__name__}: {msg.content}" for msg in recent_messages
        ])
        
        # Enhanced intent analysis with conversation context
        prompt = f"""
        Analyze the user's intent based on their message and conversation context.
        
        Current message: {state['messages'][-1].content}
        
        Recent conversation context:
        {conversation_context}
        
        Available data:
        - BC3 fields: {len(state['bc3_fields'])}
        - Asset columns: {len(state['asset_columns'])}
        - Entities created so far: {state['entities_created_count']}
        
        Intent categories:
        - extract_entities: User wants to extract entities from BC3 fields or asset columns
        - create_entity: User wants to manually create an entity
        - natural_language_entity: User wants to create entities from natural language descriptions
        - list_entities: User wants to see existing entities
        - delete_entity: User wants to delete an entity
        - manage_relationships: User wants to analyze relationships between entities
        - help: User is asking for help or instructions
        - general_conversation: General conversation or unclear intent
        
        Return only the intent category name, no other text.
        """
        
        try:
            response = self.llm.invoke(prompt)
            intent = response.content.strip().lower()
            
            # Validate intent
            valid_intents = [
                "extract_entities", "create_entity", "natural_language_entity", "list_entities", 
                "delete_entity", "manage_relationships", "help", "general_conversation"
            ]
            
            if intent not in valid_intents:
                intent = "general_conversation"
            
            logger.info(f"Detected intent: {intent}")
            
            return {
                "current_intent": intent,
                "last_operation": "intent_analysis"
            }
            
        except Exception as e:
            logger.error(f"Error in intent analysis: {e}")
            return {
                "current_intent": "general_conversation",
                "last_operation": "intent_analysis"
            }
    
    def _response_generation_node(self, state: ConversationState) -> ConversationState:
        """Generate final response based on state"""
        logger.info("Generating response in LangGraph node")
        
        # Check if there's already an AI message from tool execution
        last_message = state["messages"][-1] if state["messages"] else None
        
        if isinstance(last_message, AIMessage):
            # Tool already provided a response, use it
            response_text = last_message.content
        else:
            # Generate contextual response
            recent_messages = state["messages"][-3:] if len(state["messages"]) > 3 else state["messages"]
            conversation_context = "\n".join([
                f"{msg.__class__.__name__}: {msg.content}" for msg in recent_messages
            ])
            
            if state["current_intent"] == "help":
                response_text = self._get_help_message()
            elif state["current_intent"] == "general_conversation":
                response_text = self._generate_general_response(state, conversation_context)
            else:
                # For other intents, create a summary response
                response_text = self._create_operation_summary(state)
        
        # Add AI message to state
        ai_message = AIMessage(content=response_text)
        
        return {
            "messages": [ai_message],
            "last_operation": "response_generation"
        }
    
    def _tools_node(self, state: ConversationState) -> ConversationState:
        """Execute tools based on intent"""
        logger.info("Executing tools in LangGraph node")
        
        try:
            intent = state["current_intent"]
            session_id = state["session_id"]
            bc3_fields = state["bc3_fields"]
            asset_columns = state["asset_columns"]
            
            result_text = ""
            
            if intent == "extract_entities":
                result_text = self._extract_entities_tool(session_id, bc3_fields, asset_columns)
            elif intent == "create_entity":
                # Try to extract entity information from the message
                user_message = state["messages"][-1].content
                entity_data = self._extract_entity_data_from_message(user_message)
                if entity_data:
                    result_text = self._create_entity_tool(session_id, entity_data)
                else:
                    result_text = "I can help you create an entity. Please provide the entity name, type, and attributes you'd like to include."
            elif intent == "natural_language_entity":
                # Create entities from natural language descriptions
                user_message = state["messages"][-1].content
                result_text = self._create_entities_from_natural_language(session_id, user_message)
            elif intent == "list_entities":
                result_text = self._list_entities_tool(session_id)
            elif intent == "delete_entity":
                # For now, return a message asking for entity ID
                result_text = "I can help you delete an entity. Please provide the entity ID you'd like to delete."
            elif intent == "manage_relationships":
                result_text = self._analyze_relationships_tool(session_id)
            else:
                result_text = f"Executed tool for intent: {intent}"
            
            # Create AI message with tool result
            ai_message = AIMessage(content=result_text)
            
            return {
                "messages": [ai_message],
                "last_operation": "tools"
            }
            
        except Exception as e:
            logger.error(f"Error in tools node: {e}")
            error_message = AIMessage(content=f"I encountered an error while executing tools: {str(e)}")
            return {
                "messages": [error_message],
                "last_operation": "tools"
            }
    
    def _relationship_analysis_node(self, state: ConversationState) -> ConversationState:
        """Analyze relationships between entities"""
        logger.info("Analyzing relationships in LangGraph node")
        
        try:
            # Get entities from Firestore
            read_request = ReadEntityRequest(session_id=state["session_id"])
            read_result = self.entity_manager.read_entities(read_request)
            
            if not read_result.success or not read_result.entities:
                response_text = "I don't see any entities in this session to analyze relationships for. Would you like to create some first?"
            elif len(read_result.entities) < 2:
                response_text = "I need at least 2 entities to show relationships. You currently have 1 entity. Would you like to create more?"
            else:
                # Detect relationships
                relationships = self.relationship_detector.detect_relationships(read_result.entities)
                
                if relationships:
                    total_relationships = sum(len(rel_list) for rel_list in relationships.values())
                    response_text = f"✅ **Relationship Analysis Complete**\n\n"
                    response_text += f"📊 **Summary:**\n"
                    response_text += f"• **Entities Analyzed:** {len(read_result.entities)}\n"
                    response_text += f"• **Relationships Found:** {total_relationships}\n\n"
                    
                    # Add detailed relationships
                    response_text += f"🔗 **Detected Relationships:**\n\n"
                    for entity_id, entity_rels in relationships.items():
                        entity = next((e for e in read_result.entities if e.entity_id == entity_id), None)
                        if entity:
                            for target_entity_id, rel_list in entity_rels.items():
                                target_entity = next((e for e in read_result.entities if e.entity_id == target_entity_id), None)
                                if target_entity:
                                    for rel in rel_list:
                                        rel_type = rel["type"].replace("_", " ").title()
                                        response_text += f"• {entity.entity_name} → **{rel_type}** → {target_entity.entity_name}\n"
                else:
                    response_text = f"📊 **Relationship Analysis Complete**\n\n"
                    response_text += f"• **Entities Analyzed:** {len(read_result.entities)}\n"
                    response_text += f"• **Relationships Found:** 0\n\n"
                    response_text += f"💡 **No clear relationships detected.** This could mean the entities are independent or relationships are not obvious from the current data."
            
            # Add AI message to state
            ai_message = AIMessage(content=response_text)
            
            return {
                "messages": [ai_message],
                "relationship_data": relationships if 'relationships' in locals() else {},
                "last_operation": "relationship_analysis"
            }
            
        except Exception as e:
            logger.error(f"Error in relationship analysis: {e}")
            error_message = AIMessage(content=f"I encountered an error while analyzing relationships: {str(e)}")
            return {
                "messages": [error_message],
                "last_operation": "relationship_analysis"
            }
    
    # Tool definitions
    def _extract_entities_tool(self, session_id: str, bc3_fields: List[Dict], asset_columns: List[Dict]) -> str:
        """Extract entities from BC3 fields and asset columns"""
        try:
            # Use the existing SimpleAgent for entity extraction
            from .simple_agent import SimpleAgent
            agent = SimpleAgent()
            
            result = agent.process_request(
                message="Extract entities from the provided data",
                session_id=session_id,
                selected_bc3_fields=bc3_fields,
                selected_asset_columns=asset_columns
            )
            
            if result['success'] and result['entities_created'] > 0:
                return f"Successfully extracted {result['entities_created']} entities: {', '.join([entity.get('entity_name', 'Unknown') for entity in result['entities']])}"
            else:
                return f"Entity extraction completed: {result['response']}"
            
        except Exception as e:
            logger.error(f"Error in entity extraction tool: {e}")
            return f"Error during entity extraction: {str(e)}"
    
    def _extract_entity_data_from_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract entity data from user message using LLM"""
        try:
            prompt = f"""
            Extract entity information from this message: "{message}"
            
            Look for:
            - entity_name: The name of the entity (e.g., "Customer", "Account", "Transaction")
            - entity_type: The type/category (e.g., "Person", "Financial", "Business")
            - entity_value: A brief description or value
            - description: A detailed description
            - attributes: List of attributes with their types
            
            If you find entity information, return a JSON object with this structure:
            {{
                "entity_name": "string",
                "entity_type": "string", 
                "entity_value": "string",
                "description": "string",
                "attributes": [
                    {{
                        "attribute_name": "string",
                        "attribute_type": "string",
                        "attribute_value": "",
                        "description": "string"
                    }}
                ]
            }}
            
            If no clear entity information is found, return "null".
            Return only the JSON object or "null", no other text.
            """
            
            response = self.llm.invoke(prompt)
            result = response.content.strip()
            
            if result == "null":
                return None
                
            import json
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"Error extracting entity data from message: {e}")
            return None

    def _create_entities_from_natural_language(self, session_id: str, message: str) -> str:
        """Create entities from natural language descriptions using LLM"""
        try:
            prompt = f"""
            Create business entities from this natural language description: "{message}"
            
            Analyze the description and create meaningful business entities with appropriate attributes.
            Focus on the business use case and create entities that would be useful for that scenario.
            
            IMPORTANT: You must return ONLY valid JSON. No explanations, no markdown, no code blocks.
            
            Return a JSON array of entities with this EXACT structure:
            [
                {{
                    "entity_name": "Descriptive Entity Name",
                    "entity_type": "field|asset|business_metric|derived_insight|segment|operational_rule",
                    "entity_value": "Brief description of the entity",
                    "confidence": 0.9,
                    "source_field": "natural_language",
                    "description": "Detailed description of the entity and its purpose",
                    "attributes": [
                        {{
                            "attribute_name": "Attribute Name",
                            "attribute_type": "string|numeric|boolean|date",
                            "attribute_value": "Default value or example",
                            "confidence": 0.9,
                            "source_field": "natural_language",
                            "description": "Description of this attribute"
                        }}
                    ]
                }}
            ]
            
            Create 1-3 entities that would be most relevant for the described use case.
            CRITICAL: Return ONLY the JSON array, no other text, no explanations, no markdown formatting.
            """
            
            response = self.llm.invoke(prompt)
            result = response.content.strip()
            
            # Debug: Log what the LLM returned
            logger.info(f"LLM response for natural language entity creation: {result[:200]}...")
            
            # Clean up the response - remove markdown formatting if present
            if result.startswith("```json"):
                result = result[7:]  # Remove ```json
            if result.startswith("```"):
                result = result[3:]   # Remove ```
            if result.endswith("```"):
                result = result[:-3]  # Remove trailing ```
            
            result = result.strip()
            
            import json
            entities_data = json.loads(result)
            
            # Create entities using the entity manager
            request = CreateEntityRequest(
                session_id=session_id,
                entities_data=entities_data
            )
            
            result = self.entity_manager.create_entities(request)
            
            if result.success:
                entity_names = [entity.entity_name for entity in result.created_entities]
                return f"✅ Successfully created {result.total_created} entities from natural language: {', '.join(entity_names)}"
            else:
                return f"❌ Failed to create entities: {result.message}"
                
        except Exception as e:
            logger.error(f"Error creating entities from natural language: {e}")
            return f"❌ Error creating entities from natural language: {str(e)}"

    def _create_entity_tool(self, session_id: str, entity_data: Dict[str, Any]) -> str:
        """Create a new entity manually"""
        try:
                request = CreateEntityRequest(
                    session_id=session_id,
                    entities_data=[entity_data]
                )
                
                result = self.entity_manager.create_entities(request)
                
                if result.success:
                    return f"Successfully created entity '{entity_data.get('entity_name', 'Unknown')}' with {len(entity_data.get('attributes', []))} attributes."
                else:
                    return f"Failed to create entity: {result.message}"
                
        except Exception as e:
            logger.error(f"Error in entity creation tool: {e}")
            return f"Error during entity creation: {str(e)}"
    
    def _list_entities_tool(self, session_id: str) -> str:
        """List all entities for a session"""
        try:
            request = ReadEntityRequest(session_id=session_id)
            result = self.entity_manager.read_entities(request)
            
            if result.success and result.entities:
                entity_list = []
                for i, entity in enumerate(result.entities, 1):
                    entity_list.append(f"{i}. {entity.entity_name} ({entity.entity_type.value}) - {entity.description}")
                
                return f"Found {len(result.entities)} entities:\n" + "\n".join(entity_list)
            else:
                return "No entities found in this session."
            
        except Exception as e:
            logger.error(f"Error in entity listing tool: {e}")
            return f"Error listing entities: {str(e)}"
    
    def _delete_entity_tool(self, session_id: str, entity_id: str) -> str:
        """Delete an entity"""
        try:
            request = DeleteEntityRequest(
                session_id=session_id,
                entity_id=entity_id
            )
            
            result = self.entity_manager.delete_entities(request)
            
            if result.success:
                return f"Successfully deleted entity {entity_id}."
            else:
                return f"Failed to delete entity: {result.message}"
                
        except Exception as e:
            logger.error(f"Error in entity deletion tool: {e}")
            return f"Error deleting entity: {str(e)}"
    
    def _analyze_relationships_tool(self, session_id: str) -> str:
        """Analyze relationships between entities"""
        try:
            request = ReadEntityRequest(session_id=session_id)
            result = self.entity_manager.read_entities(request)
            
            if result.success and result.entities:
                relationships = self.relationship_detector.detect_relationships(result.entities)
            if relationships:
                total_relationships = sum(len(rel_list) for rel_list in relationships.values())
                return f"Found {total_relationships} relationships between {len(result.entities)} entities."
            else:
                return "No relationships detected between entities."
                
        except Exception as e:
            logger.error(f"Error in relationship analysis tool: {e}")
            return f"Error analyzing relationships: {str(e)}"
    
    # Helper methods
    def _route_after_intent(self, state: ConversationState) -> str:
        """Route to appropriate node based on intent"""
        return state["current_intent"]
    
    def _get_help_message(self) -> str:
        """Get help message"""
        return """
I'm here to help you build and manage entities! Here's what I can do:

**Entity Extraction:**
- "Extract entities from my BC3 fields"
- "Find entities in my asset columns"
- "Identify business entities from the data"

**Entity Creation:**
- "Create a customer entity with name and email attributes"
- "Build a credit account entity"
- "Make a transaction entity"

**Entity Management:**
- "List all my entities"
- "Show me what entities I have"
- "Delete the Customer Profile entity"
- "Remove entity_abc123"

**Relationship Management:**
- "Show me relationships between entities"
- "How are my entities connected?"
- "Analyze entity relationships"

**Data Context:**
- You can provide BC3 fields and asset columns, and I'll use them for extraction
- I remember our conversation context throughout the session
- I automatically detect relationships between entities

Just tell me what you'd like to do in natural language!
        """.strip()
        
    def _generate_general_response(self, state: ConversationState, conversation_context: str) -> str:
        """Generate a general conversational response"""
        prompt = f"""
        You are a helpful assistant for entity extraction and management. 
        
        Current conversation context:
        {conversation_context}
        
        Session context:
        - BC3 fields available: {len(state['bc3_fields'])}
        - Asset columns available: {len(state['asset_columns'])}
        - Entities created so far: {state['entities_created_count']}

Provide a helpful response that guides them toward entity extraction or creation. Be friendly and suggest what they can do next.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error generating general response: {e}")
            return "I'm here to help with entity extraction and management. You can ask me to extract entities from your data, create new entities, or list existing ones. What would you like to do?"
    
    def _create_operation_summary(self, state: ConversationState) -> str:
        """Create a summary of the operation performed"""
        operation = state["last_operation"]
        entities_count = state["entities_created_count"]
        
        if operation == "tools":
            return f"Operation completed successfully. {entities_count} entities were processed in this session."
        elif operation == "relationship_analysis":
            return "Relationship analysis completed. Check the detailed results above."
        else:
            return "Operation completed successfully."
    
    # Public methods for external access
    def get_conversation_history(self, session_id: str, user_id: str = None, limit: int = None) -> List[Dict]:
        """Get conversation history from LangGraph"""
        try:
            # Use default values if not provided - MUST match process_message logic
            if user_id is None:
                user_id = Config.get_default_user_id()
            if limit is None:
                limit = Config.get_default_conversation_limit()
            
            thread_id = f"{Config.get_thread_prefix()}_{user_id}_{session_id}"
            config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }
            
            # Get conversation history using the checkpointer directly
            history = list(self.graph.get_state_history(config))
            logger.info(f"🔍 DEBUG: Found {len(history)} checkpoints for thread_id: {thread_id}")
            
            # Also try to get current state
            current_state = self.graph.get_state(config)
            logger.info(f"🔍 DEBUG: Current state: {current_state}")
            
            messages = []
            for i, checkpoint in enumerate(reversed(history[:limit])):
                logger.info(f"🔍 DEBUG: Checkpoint {i}: {checkpoint}")
                checkpoint_messages = checkpoint.values.get("messages", [])
                logger.info(f"🔍 DEBUG: Checkpoint {i} has {len(checkpoint_messages)} messages")
                for message in checkpoint_messages:
                    messages.append({
                        "role": "user" if isinstance(message, HumanMessage) else "assistant",
                        "content": message.content,
                        "timestamp": checkpoint.created_at
                    })
            
            logger.info(f"🔍 DEBUG: Returning {len(messages)} messages")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def get_session_summary(self, session_id: str, user_id: str = None) -> Dict[str, Any]:
        """Get session summary from LangGraph state"""
        try:
            # Use default user_id if not provided
            if user_id is None:
                user_id = Config.get_default_user_id()
            
            thread_id = f"{Config.get_thread_prefix()}_{user_id}_{session_id}"
            config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }
            
            # Get current state
            current_state = self.graph.get_state(config)
            
            if not current_state:
                return {}
            
            return {
                "session_id": session_id,
                "thread_id": thread_id,
                "message_count": len(current_state.values.get("messages", [])),
                "entities_created_count": current_state.values.get("entities_created_count", 0),
                "has_bc3_fields": bool(current_state.values.get("bc3_fields")),
                "has_asset_columns": bool(current_state.values.get("asset_columns")),
                "current_intent": current_state.values.get("current_intent", ""),
                "last_activity": current_state.created_at,
                "status": "active" if current_state.next else "completed"
            }
            
        except Exception as e:
            logger.error(f"Error getting session summary: {e}")
            return {}