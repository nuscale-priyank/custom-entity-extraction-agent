import os
import time
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_vertexai import ChatVertexAI
from langchain_core.tools import tool

from models import (
    BC3Segment, ExtractedEntity, EntityType, ChatMessage, 
    AgentRequest, AgentResponse, GenericDocument, GenericDataField
)


class CustomEntityExtractionAgent:
    """AI Agent for custom entity extraction from various data structures using LangGraph"""
    
    # Define the state schema for LangGraph
    class AgentState:
        def __init__(self, messages: List[Any] = None, data: Dict[str, Any] = None, 
                     context_provider: str = "generic", extracted_entities: List[Dict[str, Any]] = None,
                     analysis: Dict[str, Any] = None, session_id: str = "", 
                     tools_enabled: bool = True, metadata: Dict[str, Any] = None):
            self.messages = messages or []
            self.data = data or {}
            self.context_provider = context_provider
            self.extracted_entities = extracted_entities or []
            self.analysis = analysis or {}
            self.session_id = session_id
            self.tools_enabled = tools_enabled
            self.metadata = metadata or {}
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        """Initialize the Custom Entity Extraction Agent"""
        print(f"🚀 Initializing CustomEntityExtractionAgent with project: {project_id}")
        self.project_id = project_id
        self.location = location
        self.llm = self._initialize_llm()
        print("🤖 LLM initialized successfully")
        print("🔧 Starting graph construction...")
        self.graph = self._build_graph()
        print("🔧 Graph construction completed")
        
    def _initialize_llm(self) -> ChatVertexAI:
        """Initialize Vertex AI LLM"""
        return ChatVertexAI(
            model_name="gemini-2.5-flash-lite",
            project=self.project_id,
            location=self.location,
            temperature=0.1,
            max_output_tokens=2048
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for custom entity extraction"""
        return """You are an expert AI agent specialized in extracting custom entities from various data structures and JSON documents.

Your primary responsibilities:

1. **Data Structure Analysis**: Analyze different types of data structures including:
   - BC3 (Business Credit Bureau) data with segment_name and data_dictionary
   - Generic JSON documents with nested objects and arrays
   - Structured data with field definitions and metadata
   - Any other JSON-like data structures

2. **Entity Extraction**: Extract meaningful entities from the data including:
   - **Fields**: Individual data fields and their properties
   - **Segments**: Business segment classifications or document sections
   - **Values**: Important data values and their context
   - **Metadata**: Additional contextual information
   - **Objects**: Complex nested objects
   - **Arrays**: List-based data structures

3. **Contextual Understanding**: 
   - Understand the business context of each field
   - Identify relationships between fields and objects
   - Recognize patterns in data structures
   - Provide insights about data quality and completeness
   - Adapt extraction strategy based on data type

4. **Response Format**: Always structure your responses to include:
   - Clear analysis of the data structure
   - List of extracted entities with confidence scores
   - Business insights and recommendations
   - Any data quality issues or missing information

5. **Entity Classification**: When extracting entities, classify them as:
   - FIELD: Individual data fields
   - SEGMENT: Business segment or document section information
   - VALUE: Important data values
   - METADATA: Contextual information
   - OBJECT: Complex nested objects
   - ARRAY: List-based data structures
   - DOCUMENT: Document-level information

For each extracted entity, provide:
- Entity type and name
- Extracted value
- Confidence score (0-1)
- Source field reference
- Description of the entity's significance
- Context provider identification

Always maintain professional, accurate, and helpful communication while analyzing data structures."""

    def _extract_entities_from_data(self, data: Dict[str, Any], context_provider: str = "generic") -> List[Dict[str, Any]]:
        """Extract entities from various data structures"""
        try:
            entities = []
            
            if context_provider == "bc3":
                entities = self._extract_bc3_entities(data)
            else:
                entities = self._extract_generic_entities(data, context_provider)
            
            return entities
            
        except Exception as e:
            return [{
                "entity_type": EntityType.METADATA,
                "entity_name": "error",
                "entity_value": str(e),
                "confidence": 0.0,
                "source_field": "system",
                "description": f"Error extracting entities: {str(e)}",
                "context_provider": context_provider
            }]

    @tool
    def extract_entities_from_data(self, data: Dict[str, Any], context_provider: str = "generic") -> List[Dict[str, Any]]:
        """Extract entities from various data structures"""
        return self._extract_entities_from_data(data, context_provider)

    def _extract_bc3_entities(self, bc3_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities from BC3 data structure"""
        try:
            segment = BC3Segment(**bc3_data)
            
            entities = []
            
            # Extract segment-level entity
            entities.append({
                "entity_type": EntityType.SEGMENT,
                "entity_name": "segment_name",
                "entity_value": segment.segment_name,
                "confidence": 1.0,
                "source_field": "segment_name",
                "description": f"Business segment: {segment.segment_name}",
                "context_provider": "bc3"
            })
            
            # Extract field-level entities
            for field in segment.data_dictionary:
                # Field entity
                entities.append({
                    "entity_type": EntityType.FIELD,
                    "entity_name": field.bc3_field,
                    "entity_value": field.description,
                    "confidence": 0.95,
                    "source_field": field.bc3_field,
                    "description": field.definition or f"Field: {field.description}",
                    "context_provider": "bc3"
                })
                
                # Valid values as separate entities
                if field.valid_values:
                    for value in field.valid_values:
                        entities.append({
                            "entity_type": EntityType.VALUE,
                            "entity_name": f"{field.bc3_field}_value",
                            "entity_value": value,
                            "confidence": 0.9,
                            "source_field": field.bc3_field,
                            "description": f"Valid value for {field.description}: {value}",
                            "context_provider": "bc3"
                        })
                
                # Notes as metadata
                if field.notes:
                    entities.append({
                        "entity_type": EntityType.METADATA,
                        "entity_name": f"{field.bc3_field}_notes",
                        "entity_value": field.notes,
                        "confidence": 0.85,
                        "source_field": field.bc3_field,
                        "description": f"Notes for {field.description}",
                        "context_provider": "bc3"
                    })
            
            return entities
            
        except Exception as e:
            return [{
                "entity_type": EntityType.METADATA,
                "entity_name": "error",
                "entity_value": str(e),
                "confidence": 0.0,
                "source_field": "system",
                "description": f"Error extracting BC3 entities: {str(e)}",
                "context_provider": "bc3"
            }]

    def _extract_generic_entities(self, data: Dict[str, Any], context_provider: str) -> List[Dict[str, Any]]:
        """Extract business-relevant entities from generic data structure"""
        entities = []
        
        def is_business_relevant(key: str, value: Any, path: str) -> bool:
            """Determine if a field is business-relevant"""
            # Skip empty values
            if value == "" or value == [] or value is None:
                return False
            
            # Skip metadata fields
            metadata_fields = {"notes", "valid_values", "definition", "description"}
            if key.lower() in metadata_fields:
                return False
            
            # Skip technical/structural fields
            technical_fields = {"type", "format", "required", "optional", "default"}
            if key.lower() in technical_fields:
                return False
            
            # Include business identifiers, names, codes, amounts, dates
            business_patterns = [
                "name", "id", "code", "amount", "date", "time", "status", 
                "type", "category", "class", "group", "segment", "field",
                "value", "description", "title", "label"
            ]
            
            return any(pattern in key.lower() for pattern in business_patterns)
        
        def extract_business_entities(obj, path="", depth=0):
            """Extract only business-relevant entities"""
            if depth > 3:  # Limit recursion depth
                return
                
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Check if this is a business-relevant field
                    if is_business_relevant(key, value, current_path):
                        if isinstance(value, (str, int, float, bool)):
                            # Only extract non-empty values
                            if value and str(value).strip():
                                entities.append({
                                    "entity_type": EntityType.FIELD,
                                    "entity_name": key,
                                    "entity_value": str(value),
                                    "confidence": 0.95,
                                    "source_field": current_path,
                                    "description": f"Business field: {key} = {value}",
                                    "context_provider": context_provider
                                })
                        elif isinstance(value, list) and value:
                            # Only extract non-empty arrays with business content
                            if len(value) > 0:
                                entities.append({
                                    "entity_type": EntityType.ARRAY,
                                    "entity_name": key,
                                    "entity_value": f"Array with {len(value)} business items",
                                    "confidence": 0.9,
                                    "source_field": current_path,
                                    "description": f"Business array: {key}",
                                    "context_provider": context_provider
                                })
                                
                                # Only process first few items to avoid noise
                                for i, item in enumerate(value[:3]):
                                    if isinstance(item, dict):
                                        extract_business_entities(item, f"{current_path}[{i}]", depth + 1)
                        elif isinstance(value, dict):
                            # Only extract business objects
                            if value:  # Non-empty dict
                                entities.append({
                                    "entity_type": EntityType.OBJECT,
                                    "entity_name": key,
                                    "entity_value": f"Business object: {key}",
                                    "confidence": 0.85,
                                    "source_field": current_path,
                                    "description": f"Business object: {key}",
                                    "context_provider": context_provider
                                })
                                extract_business_entities(value, current_path, depth + 1)
            
            elif isinstance(obj, list):
                # Only process arrays at root level or business-relevant contexts
                if path == "" or "data_dictionary" in path or "segment" in path:
                    for i, item in enumerate(obj[:5]):  # Limit to first 5 items
                        if isinstance(item, dict):
                            extract_business_entities(item, f"{path}[{i}]", depth + 1)
        
        # Start extraction
        extract_business_entities(data)
        
        # If no business entities found, extract at least the main structure
        if not entities and isinstance(data, dict):
            main_keys = [k for k, v in data.items() if v and not isinstance(v, (list, dict)) or (isinstance(v, (list, dict)) and len(v) > 0)]
            for key in main_keys[:3]:  # Limit to top 3
                entities.append({
                    "entity_type": EntityType.FIELD,
                    "entity_name": key,
                    "entity_value": str(data[key])[:100] if isinstance(data[key], str) else str(type(data[key]).__name__),
                    "confidence": 0.8,
                    "source_field": key,
                    "description": f"Main field: {key}",
                    "context_provider": context_provider
                })
        
        return entities

    def _analyze_data_structure(self, data: Dict[str, Any], context_provider: str = "generic") -> Dict[str, Any]:
        """Analyze data structure and provide insights"""
        try:
            if context_provider == "bc3":
                return self._analyze_bc3_structure(data)
            else:
                return self._analyze_generic_structure(data, context_provider)
            
        except Exception as e:
            return {"error": str(e)}

    @tool
    def analyze_data_structure(self, data: Dict[str, Any], context_provider: str = "generic") -> Dict[str, Any]:
        """Analyze data structure and provide insights"""
        return self._analyze_data_structure(data, context_provider)

    def _analyze_bc3_structure(self, bc3_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze BC3 data structure and provide insights"""
        try:
            segment = BC3Segment(**bc3_data)
            
            analysis = {
                "context_provider": "bc3",
                "segment_name": segment.segment_name,
                "total_fields": len(segment.data_dictionary),
                "fields_with_definitions": sum(1 for f in segment.data_dictionary if f.definition),
                "fields_with_notes": sum(1 for f in segment.data_dictionary if f.notes),
                "fields_with_valid_values": sum(1 for f in segment.data_dictionary if f.valid_values),
                "field_types": {},
                "data_quality_score": 0.0
            }
            
            # Analyze field types based on names
            for field in segment.data_dictionary:
                field_name = field.bc3_field.lower()
                if "date" in field_name or "dte" in field_name:
                    analysis["field_types"]["date"] = analysis["field_types"].get("date", 0) + 1
                elif "amount" in field_name or "amt" in field_name:
                    analysis["field_types"]["amount"] = analysis["field_types"].get("amount", 0) + 1
                elif "code" in field_name or "cde" in field_name:
                    analysis["field_types"]["code"] = analysis["field_types"].get("code", 0) + 1
                else:
                    analysis["field_types"]["other"] = analysis["field_types"].get("other", 0) + 1
            
            # Calculate data quality score
            total_score = 0
            if analysis["total_fields"] > 0:
                total_score += (analysis["fields_with_definitions"] / analysis["total_fields"]) * 0.4
                total_score += (analysis["fields_with_notes"] / analysis["total_fields"]) * 0.3
                total_score += (analysis["fields_with_valid_values"] / analysis["total_fields"]) * 0.3
            
            analysis["data_quality_score"] = round(total_score, 2)
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}

    def _analyze_generic_structure(self, data: Dict[str, Any], context_provider: str) -> Dict[str, Any]:
        """Analyze generic data structure and provide insights"""
        def count_elements(obj):
            if isinstance(obj, dict):
                return 1 + sum(count_elements(v) for v in obj.values())
            elif isinstance(obj, list):
                return 1 + sum(count_elements(item) for item in obj)
            else:
                return 1
        
        def get_structure_info(obj, path=""):
            info = {"type": type(obj).__name__, "path": path}
            
            if isinstance(obj, dict):
                info["fields"] = len(obj)
                info["field_names"] = list(obj.keys())
                info["nested_objects"] = sum(1 for v in obj.values() if isinstance(v, (dict, list)))
            elif isinstance(obj, list):
                info["length"] = len(obj)
                info["item_types"] = list(set(type(item).__name__ for item in obj))
            
            return info
        
        analysis = {
            "context_provider": context_provider,
            "total_elements": count_elements(data),
            "structure_info": get_structure_info(data),
            "data_types": self._get_data_types(data),
            "complexity_score": self._calculate_complexity(data)
        }
        
        return analysis

    def _get_data_types(self, obj):
        """Get data types present in the object"""
        types = set()
        
        def collect_types(o):
            types.add(type(o).__name__)
            if isinstance(o, dict):
                for v in o.values():
                    collect_types(v)
            elif isinstance(o, list):
                for item in o:
                    collect_types(item)
        
        collect_types(obj)
        return list(types)

    def _calculate_complexity(self, obj):
        """Calculate complexity score of the data structure"""
        def complexity(o, depth=0):
            if depth > 10:  # Prevent infinite recursion
                return 1
            
            if isinstance(o, dict):
                return 1 + sum(complexity(v, depth + 1) for v in o.values())
            elif isinstance(o, list):
                return 1 + sum(complexity(item, depth + 1) for item in o)
            else:
                return 1
        
        return complexity(obj)

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        print("🔧 Building LangGraph workflow...")
        
        # Create the graph with dictionary state (LangGraph standard approach)
        workflow = StateGraph(dict)
        print("🔧 Created StateGraph with dict schema")
        
        # Add nodes with proper state handling
        workflow.add_node("extract_entities", self._extract_entities_node)
        workflow.add_node("analyze_structure", self._analyze_structure_node)
        workflow.add_node("generate_response", self._generate_response_node)
        print("🔧 Added all nodes to workflow")
        
        # Add edges
        workflow.add_edge("extract_entities", "analyze_structure")
        workflow.add_edge("analyze_structure", "generate_response")
        workflow.add_edge("generate_response", END)
        print("🔧 Added all edges to workflow")
        
        # Set entry point
        workflow.set_entry_point("extract_entities")
        print("🔧 Set entry point to 'extract_entities'")
        
        compiled_graph = workflow.compile()
        print("🔧 Graph compiled successfully")
        return compiled_graph
    
    def _state_to_dict(self, state) -> Dict[str, Any]:
        """Convert state to dictionary format"""
        if isinstance(state, dict):
            return {
                "messages": state["messages"],
                "data": state["data"],
                "context_provider": state["context_provider"],
                "extracted_entities": state["extracted_entities"],
                "analysis": state["analysis"],
                "session_id": state["session_id"],
                "tools_enabled": state["tools_enabled"],
                "metadata": state["metadata"]
            }
        else:
            return {
                "messages": state.messages,
                "data": state.data,
                "context_provider": state.context_provider,
                "extracted_entities": state.extracted_entities,
                "analysis": state.analysis,
                "session_id": state.session_id,
                "tools_enabled": state.tools_enabled,
                "metadata": state.metadata
            }
    
    def _extract_entities_node(self, state) -> Dict[str, Any]:
        """Node for extracting entities from data"""
        print(f"🔍 Extract entities node called with state type: {type(state)}")
        
        # LangGraph passes dict when using dict schema
        data = state["data"]
        context_provider = state["context_provider"]
        print(f"Extract entities node - data type: {type(data)}")
        print(f"Extract entities node - context_provider: {context_provider}")
        
        entities = self._extract_entities_from_data(data, context_provider)
        state["extracted_entities"] = entities
        
        print(f"🔍 Extract entities node returning dict")
        return state
    
    def _analyze_structure_node(self, state) -> Dict[str, Any]:
        """Node for analyzing data structure"""
        print(f"📊 Analyze structure node called with state type: {type(state)}")
        
        # LangGraph passes dict when using dict schema
        analysis = self._analyze_data_structure(state["data"], state["context_provider"])
        state["analysis"] = analysis
        
        print(f"📊 Analyze structure node returning dict")
        return state
    
    def _generate_response_node(self, state) -> Dict[str, Any]:
        """Node for generating final response"""
        print(f"💬 Generate response node called with state type: {type(state)}")
        
        # LangGraph passes dict when using dict schema
        context_provider = state["context_provider"]
        extracted_entities = state["extracted_entities"]
        analysis = state["analysis"]
        messages = state["messages"]
        
        # Prepare context for LLM
        context = f"""
Data Analysis Results:
- Context Provider: {context_provider}
- Extracted Entities: {len(extracted_entities)}
- Analysis: {analysis}

Extracted Entities:
{self._format_entities_for_llm(extracted_entities)}

User Message: {messages[-1].content if messages else 'No message'}
"""
        
        # Generate response using LLM
        messages = [
            SystemMessage(content=self._get_system_prompt()),
            HumanMessage(content=context)
        ]
        
        try:
            response = self.llm.invoke(messages)
            if response is None:
                # Create a fallback response if LLM returns None
                response = AIMessage(content="Analysis completed successfully. Entities have been extracted and analyzed.")
            state["messages"].append(response)
        except Exception as e:
            # Create a fallback response if LLM fails
            response = AIMessage(content=f"Analysis completed with some issues. Error: {str(e)}")
            state["messages"].append(response)
        
        print(f"💬 Generate response node returning dict")
        return state
    
    def _format_entities_for_llm(self, entities: List[Dict[str, Any]]) -> str:
        """Format entities for LLM consumption"""
        formatted = []
        for entity in entities:
            formatted.append(
                f"- {entity['entity_type']}: {entity['entity_name']} = {entity['entity_value']} "
                f"(confidence: {entity['confidence']}, source: {entity['source_field']}, "
                f"context: {entity.get('context_provider', 'unknown')})"
            )
        return "\n".join(formatted)
    
    def process_request(self, request: AgentRequest) -> AgentResponse:
        """Process a user request and return response with extracted entities"""
        start_time = time.time()
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Convert data to dict if it's a Pydantic model
        if hasattr(request.data, 'dict'):
            data_dict = request.data.dict()
        else:
            data_dict = request.data
        
        # Prepare initial state as dictionary (LangGraph expects dict when using dict schema)
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "data": data_dict,
            "context_provider": request.context_provider,
            "extracted_entities": [],
            "analysis": {},
            "session_id": session_id,
            "tools_enabled": request.tools_enabled,
            "metadata": request.metadata
        }
        
        # Debug: Print initial state structure
        print(f"Initial state type: {type(initial_state)}")
        print(f"Initial state data type: {type(initial_state['data'])}")
        print(f"Initial state context_provider: {initial_state['context_provider']}")
        
        # Add chat history
        for msg in request.chat_history:
            if msg.role == "user":
                initial_state["messages"].append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                initial_state["messages"].append(AIMessage(content=msg.content))
        
        # Execute the graph
        try:
            print(f"Starting graph execution with initial state type: {type(initial_state)}")
            final_state = self.graph.invoke(initial_state)
            print(f"Graph execution completed. Final state type: {type(final_state)}")
            if final_state is None:
                raise Exception("Graph execution returned None")
            print(f"Final state is dict: {isinstance(final_state, dict)}")
        except Exception as e:
            print(f"Graph execution failed: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            # Create a fallback final state as dict
            final_state = {
                "messages": [AIMessage(content="Analysis completed with errors")],
                "data": data_dict,
                "context_provider": request.context_provider,
                "extracted_entities": [],
                "analysis": {"error": str(e)},
                "session_id": session_id,
                "tools_enabled": request.tools_enabled,
                "metadata": request.metadata
            }
            # Set error flag for HTTP status code
            has_error = True
        else:
            has_error = False
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Convert extracted entities to proper format with error handling
        extracted_entities = []
        if final_state and 'extracted_entities' in final_state and final_state['extracted_entities']:
            try:
                extracted_entities = [
                    ExtractedEntity(**entity) for entity in final_state['extracted_entities']
                ]
            except Exception as e:
                print(f"Error converting entities: {e}")
                extracted_entities = []
        
        # Get the response content safely
        response_content = "No response generated"
        if final_state and 'messages' in final_state and final_state['messages'] and len(final_state['messages']) > 0:
            last_message = final_state['messages'][-1]
            if hasattr(last_message, 'content') and last_message.content:
                response_content = last_message.content
            elif hasattr(last_message, 'text'):
                response_content = last_message.text
            else:
                response_content = str(last_message)
        
        # Update chat history
        updated_chat_history = request.chat_history + [
            ChatMessage(role="user", content=request.message),
            ChatMessage(role="assistant", content=response_content)
        ]
        
        # Calculate overall confidence
        confidence_score = sum(entity.confidence for entity in extracted_entities) / len(extracted_entities) if extracted_entities else 0.0
        
        response = AgentResponse(
            response=response_content,
            extracted_entities=extracted_entities,
            chat_history=updated_chat_history,
            session_id=session_id,
            confidence_score=confidence_score,
            processing_time=processing_time,
            metadata={
                "analysis": final_state.get('analysis', {}) if isinstance(final_state, dict) else {},
                "tools_enabled": request.tools_enabled,
                "context_provider": request.context_provider,
                "has_error": has_error,
                **request.metadata
            }
        )
        
        # Add error status to response
        if has_error:
            response.metadata["error_status"] = 500
            response.metadata["error_message"] = "Graph execution failed"
        
        return response


# Backward compatibility alias
BC3AIAgent = CustomEntityExtractionAgent
