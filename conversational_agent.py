"""
Conversational Agent for natural entity building through chat
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI

from config import Config
from chat_session_manager import ChatSessionManager
from entity_collection_manager import EntityCollectionManager
from entity_collection_models import CreateEntityRequest
from relationship_detector import RelationshipDetector

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """Agent that can understand user intent and build entities through conversation"""
    
    def __init__(self, project_id: str = None):
        """Initialize the conversational agent"""
        self.project_id = project_id or Config.get_project_id()
        
        # Initialize LLM
        self.llm = ChatVertexAI(
            model_name=Config.get_model_name(),
            project=self.project_id,
            location=Config.LOCATION,
            temperature=Config.get_temperature(),
            max_output_tokens=Config.get_max_output_tokens()
        )
        
        # Initialize managers
        self.chat_manager = ChatSessionManager(self.project_id, database_id=Config.get_database_id())
        self.entity_manager = EntityCollectionManager(self.project_id, database_id=Config.get_database_id())
        self.relationship_detector = RelationshipDetector()
        
        logger.info("Conversational Agent initialized")
    
    def process_message(self, session_id: str, user_message: str, 
                       selected_bc3_fields: List[Dict] = None,
                       selected_asset_columns: List[Dict] = None) -> Dict[str, Any]:
        """Process a user message and return appropriate response"""
        
        try:
            logger.info(f"Processing message for session: {session_id}")
            
            # Get or create session
            session = self.chat_manager.get_session(session_id)
            if not session:
                logger.info(f"Creating new session: {session_id}")
                initial_context = {}
                if selected_bc3_fields:
                    initial_context['selected_bc3_fields'] = selected_bc3_fields
                if selected_asset_columns:
                    initial_context['selected_asset_columns'] = selected_asset_columns
                session = self.chat_manager.create_session(session_id, initial_context)
            
            # Update context if new data provided
            context_updates = {}
            if selected_bc3_fields:
                context_updates['selected_bc3_fields'] = selected_bc3_fields
            if selected_asset_columns:
                context_updates['selected_asset_columns'] = selected_asset_columns
            
            if context_updates:
                self.chat_manager.update_context(session_id, context_updates)
                session = self.chat_manager.get_session(session_id)
            
            # Add user message to session
            self.chat_manager.add_message(session_id, "user", user_message)
            
            # Analyze user intent
            intent = self._analyze_intent(user_message, session)
            logger.info(f"Detected intent: {intent}")
            
            # Process based on intent
            if intent == "extract_entities":
                response = self._handle_entity_extraction(session_id, user_message, session, selected_bc3_fields, selected_asset_columns)
            elif intent == "create_entity":
                response = self._handle_entity_creation(session_id, user_message, session)
            elif intent == "list_entities":
                response = self._handle_list_entities(session_id, session)
            elif intent == "update_entity":
                response = self._handle_entity_update(session_id, user_message, session)
            elif intent == "delete_entity":
                response = self._handle_entity_deletion(session_id, user_message, session)
            elif intent == "manage_relationships":
                response = self._handle_relationship_management(session_id, user_message, session)
            elif intent == "help":
                response = self._handle_help_request()
            else:
                response = self._handle_general_conversation(session_id, user_message, session)
            
            # Add assistant response to session
            self.chat_manager.add_message(session_id, "assistant", response['response'])
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_response = {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "success": False,
                "entities_created": 0,
                "entities": []
            }
            self.chat_manager.add_message(session_id, "assistant", error_response['response'])
            return error_response
    
    def _analyze_intent(self, message: str, session) -> str:
        """Analyze user message to determine intent"""
        
        message_lower = message.lower()
        
        # Intent patterns
        if any(word in message_lower for word in ['extract', 'find', 'identify', 'discover']):
            return "extract_entities"
        elif any(word in message_lower for word in ['create', 'build', 'make', 'add']):
            return "create_entity"
        elif any(word in message_lower for word in ['list', 'show', 'display', 'get']):
            return "list_entities"
        elif any(word in message_lower for word in ['update', 'modify', 'change', 'edit']):
            return "update_entity"
        elif any(word in message_lower for word in ['delete', 'remove', 'drop']):
            return "delete_entity"
        elif any(word in message_lower for word in ['relationship', 'connect', 'link', 'relate']):
            return "manage_relationships"
        elif any(word in message_lower for word in ['help', 'assist', 'support']):
            return "help"
        else:
            return "general_conversation"
    
    def _handle_entity_extraction(self, session_id: str, message: str, session, selected_bc3_fields: List[Dict] = None, selected_asset_columns: List[Dict] = None) -> Dict[str, Any]:
        """Handle entity extraction from BC3 fields and asset columns"""
        
        try:
            # Use the BC3 fields and asset columns passed directly, or fall back to session context
            bc3_fields = selected_bc3_fields or (session.context.get('selected_bc3_fields', []) if session else [])
            asset_columns = selected_asset_columns or (session.context.get('selected_asset_columns', []) if session else [])
            
            if not bc3_fields and not asset_columns:
                return {
                    "response": "I'd be happy to help extract entities! However, I don't see any BC3 fields or asset columns in our conversation. Could you please provide some data to work with?",
                    "success": False,
                    "entities_created": 0,
                    "entities": []
                }
            
            # Use the existing agent to extract entities
            from agent import SimpleAgent
            agent = SimpleAgent()
            
            result = agent.process_request(
                message=message,
                session_id=session_id,
                selected_bc3_fields=bc3_fields,
                selected_asset_columns=asset_columns
            )
            
            # Add created entities to session
            if result['success'] and result['entities_created'] > 0:
                for entity in result['entities']:
                    if 'entity_id' in entity:
                        self.chat_manager.add_created_entity(session_id, entity['entity_id'])
                
                # Enhance response with relationship information
                result = self._enhance_response_with_relationships(result, session_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            return {
                "response": f"I encountered an error while extracting entities: {str(e)}",
                "success": False,
                "entities_created": 0,
                "entities": []
            }
    
    def _handle_entity_creation(self, session_id: str, message: str, session) -> Dict[str, Any]:
        """Handle manual entity creation through conversation"""
        
        try:
            # Use LLM to understand what entity the user wants to create
            prompt = self._get_entity_creation_prompt(message, session)
            
            response = self.llm.invoke(prompt)
            
            # Try to extract entity information from LLM response
            entity_data = self._extract_entity_from_response(response.content)
            
            if entity_data:
                # Create the entity using the entity manager
                request = CreateEntityRequest(
                    session_id=session_id,
                    entities_data=[entity_data]
                )
                
                result = self.entity_manager.create_entities(request)
                
                if result.success:
                    # Add to session
                    for entity in result.created_entities:
                        self.chat_manager.add_created_entity(session_id, entity.entity_id)
                    
                    return {
                        "response": f"Great! I've created the entity '{entity_data.get('entity_name', 'Unknown')}' with {len(entity_data.get('attributes', []))} attributes.",
                        "success": True,
                        "entities_created": result.total_created,
                        "entities": [entity.model_dump(mode='json') for entity in result.created_entities]
                    }
                else:
                    return {
                        "response": f"I had trouble creating the entity: {result.message}",
                        "success": False,
                        "entities_created": 0,
                        "entities": []
                    }
            else:
                return {
                    "response": "I understand you want to create an entity, but I need more details. Could you please specify the entity name, type, and any attributes you'd like to include?",
                    "success": False,
                    "entities_created": 0,
                    "entities": []
                }
                
        except Exception as e:
            logger.error(f"Error in entity creation: {e}")
            return {
                "response": f"I encountered an error while creating the entity: {str(e)}",
                "success": False,
                "entities_created": 0,
                "entities": []
            }
    
    def _handle_list_entities(self, session_id: str, session) -> Dict[str, Any]:
        """Handle listing existing entities"""
        
        try:
            from entity_collection_models import ReadEntityRequest
            
            request = ReadEntityRequest(session_id=session_id)
            result = self.entity_manager.read_entities(request)
            
            if result.success and result.entities:
                # Count entities with relationships
                entities_with_relationships = sum(1 for entity in result.entities if entity.relationships)
                total_relationships = sum(len(entity.relationships) for entity in result.entities)
                
                message = f"📊 **Entity Summary**\n\n"
                message += f"• **Total Entities:** {len(result.entities)}\n"
                message += f"• **Entities with Relationships:** {entities_with_relationships}\n"
                message += f"• **Total Relationships:** {total_relationships}\n\n"
                
                # Detailed entity information
                message += f"📋 **Detailed Entity Information:**\n\n"
                for i, entity in enumerate(result.entities, 1):
                    message += f"**{i}. {entity.entity_name}** ({entity.entity_type.value})\n"
                    message += f"   • **Description:** {entity.description}\n"
                    message += f"   • **Confidence:** {entity.confidence:.2f}\n"
                    message += f"   • **Source Fields:** {entity.source_field}\n\n"
                    
                    # List attributes
                    if entity.attributes:
                        message += f"   **Attributes ({len(entity.attributes)}):**\n"
                        for attr in entity.attributes:
                            # Convert attribute_value to string for display
                            attr_value = str(attr.attribute_value) if attr.attribute_value is not None else "None"
                            message += f"   • {attr.attribute_name} ({attr.attribute_type}): {attr_value}\n"
                        message += "\n"
                    
                    # List relationships
                    if entity.relationships:
                        message += f"   **Relationships ({len(entity.relationships)}):**\n"
                        for target_entity_id, rel_data in entity.relationships.items():
                            target_entity = next((e for e in result.entities if e.entity_id == target_entity_id), None)
                            if target_entity:
                                for rel in rel_data.get('relationships', []):
                                    rel_type = rel["type"].replace("_", " ").title()
                                    message += f"   • → {rel_type} → {target_entity.entity_name} (confidence: {rel.get('confidence', 0):.2f})\n"
                        message += "\n"
                    else:
                        message += f"   **Relationships:** None\n\n"
                
                message += f"💡 **Next Steps:**\n"
                message += f"Please view the detailed entities and relationships in the **Entity Management** section at the top of your screen."
            else:
                message = f"📊 **Entity Summary**\n\n"
                message += f"• **Total Entities:** 0\n"
                message += f"• **Entities with Relationships:** 0\n"
                message += f"• **Total Relationships:** 0\n\n"
                message += f"💡 **No entities found in this session.** Would you like to create some?"
            
            return {
                "response": message,
                "success": True,
                "entities_created": 0,
                "entities": [entity.model_dump(mode='json') for entity in result.entities] if result.entities else []
            }
            
        except Exception as e:
            logger.error(f"Error listing entities: {e}")
            return {
                "response": f"I encountered an error while listing entities: {str(e)}",
                "success": False,
                "entities_created": 0,
                "entities": []
            }
    
    def _handle_entity_update(self, session_id: str, message: str, session) -> Dict[str, Any]:
        """Handle entity updates through conversation"""
        
        return {
            "response": "Entity updates through conversation are not yet implemented. You can use the API endpoints for now.",
            "success": False,
            "entities_created": 0,
            "entities": []
        }
    
    def _handle_entity_deletion(self, session_id: str, message: str, session) -> Dict[str, Any]:
        """Handle entity deletion through conversation"""
        
        try:
            from entity_collection_models import ReadEntityRequest, DeleteEntityRequest
            
            # First, get all entities to help identify which one to delete
            read_request = ReadEntityRequest(session_id=session_id)
            read_result = self.entity_manager.read_entities(read_request)
            
            if not read_result.success or not read_result.entities:
                return {
                    "response": "I don't see any entities in this session to delete. Would you like to create some first?",
                    "success": False,
                    "entities_created": 0,
                    "entities": []
                }
            
            # Use LLM to understand which entity the user wants to delete
            entity_list = []
            for entity in read_result.entities:
                entity_list.append(f"- {entity.entity_name} (ID: {entity.entity_id}) - {entity.description}")
            
            prompt = f"""
The user wants to delete an entity. They said: "{message}"

Available entities in this session:
{chr(10).join(entity_list)}

Based on their request, identify which entity they want to delete. Return the entity_id of the entity to delete, or "none" if you can't determine which one.

Return only the entity_id or "none", no other text.
            """
            
            response = self.llm.invoke(prompt)
            entity_id_to_delete = response.content.strip().strip('"').strip("'")
            
            if entity_id_to_delete.lower() == "none" or not entity_id_to_delete:
                return {
                    "response": f"I'm not sure which entity you want to delete. Here are the available entities:\n\n{chr(10).join(entity_list)}\n\nPlease specify which entity you'd like to delete by name or ID.",
                    "success": False,
                    "entities_created": 0,
                    "entities": []
                }
            
            # Verify the entity exists
            target_entity = None
            for entity in read_result.entities:
                if entity.entity_id == entity_id_to_delete or entity.entity_name.lower() == entity_id_to_delete.lower():
                    target_entity = entity
                    entity_id_to_delete = entity.entity_id  # Use the actual entity_id
                    break
            
            if not target_entity:
                return {
                    "response": f"I couldn't find an entity matching '{entity_id_to_delete}'. Here are the available entities:\n\n{chr(10).join(entity_list)}",
                    "success": False,
                    "entities_created": 0,
                    "entities": []
                }
            
            # Delete the entity
            delete_request = DeleteEntityRequest(
                session_id=session_id,
                entity_id=entity_id_to_delete
            )
            
            delete_result = self.entity_manager.delete_entities(delete_request)
            
            if delete_result.success:
                # Remove from session tracking
                self.chat_manager.remove_created_entity(session_id, entity_id_to_delete)
                
                return {
                    "response": f"✅ Successfully deleted the entity '{target_entity.entity_name}' (ID: {entity_id_to_delete}).",
                    "success": True,
                    "entities_created": 0,
                    "entities": []
                }
            else:
                return {
                    "response": f"I had trouble deleting the entity: {delete_result.message}",
                    "success": False,
                    "entities_created": 0,
                    "entities": []
                }
                
        except Exception as e:
            logger.error(f"Error in entity deletion: {e}")
            return {
                "response": f"I encountered an error while deleting the entity: {str(e)}",
                "success": False,
                "entities_created": 0,
                "entities": []
            }
    
    def _handle_relationship_management(self, session_id: str, message: str, session) -> Dict[str, Any]:
        """Handle relationship management through conversation"""
        
        try:
            from entity_collection_models import ReadEntityRequest
            
            # Get all entities for the session
            read_request = ReadEntityRequest(session_id=session_id)
            read_result = self.entity_manager.read_entities(read_request)
            
            if not read_result.success or not read_result.entities:
                return {
                    "response": "I don't see any entities in this session to manage relationships for. Would you like to create some first?",
                    "success": False,
                    "entities_created": 0,
                    "entities": []
                }
            
            if len(read_result.entities) < 2:
                return {
                    "response": "I need at least 2 entities to show relationships. You currently have 1 entity. Would you like to create more?",
                    "success": False,
                    "entities_created": 0,
                    "entities": []
                }
            
            # First, try to detect relationships if they haven't been detected yet
            has_relationships = any(entity.relationships for entity in read_result.entities)
            if not has_relationships:
                logger.info("No existing relationships found, triggering relationship detection")
                self.entity_manager.detect_relationships_for_session(session_id)
                
                # Re-read entities to get updated relationships
                read_result = self.entity_manager.read_entities(read_request)
            
            # Detect relationships
            relationships = self.relationship_detector.detect_relationships(read_result.entities)
            
            if relationships:
                # Count relationships found
                total_relationships = sum(len(rel_list) for rel_list in relationships.values())
                
                # Create detailed summary
                chat_output = f"✅ **Relationship Analysis Complete**\n\n"
                chat_output += f"📊 **Summary:**\n"
                chat_output += f"• **Entities Analyzed:** {len(read_result.entities)}\n"
                chat_output += f"• **Relationships Found:** {total_relationships}\n\n"
                
                # List all entities with their details
                chat_output += f"📋 **Entities in Session:**\n\n"
                for i, entity in enumerate(read_result.entities, 1):
                    chat_output += f"**{i}. {entity.entity_name}** ({entity.entity_type.value})\n"
                    chat_output += f"   • **Description:** {entity.description}\n"
                    chat_output += f"   • **Attributes:** {len(entity.attributes)} attributes\n"
                    if entity.attributes:
                        for attr in entity.attributes[:3]:  # Show first 3 attributes
                            attr_value = str(attr.attribute_value) if attr.attribute_value is not None else "None"
                            chat_output += f"     - {attr.attribute_name}: {attr_value}\n"
                        if len(entity.attributes) > 3:
                            chat_output += f"     - ... and {len(entity.attributes) - 3} more\n"
                    chat_output += "\n"
                
                # Add detailed relationships
                chat_output += f"🔗 **Detailed Relationships:**\n\n"
                for entity_id, entity_rels in relationships.items():
                    entity = next((e for e in read_result.entities if e.entity_id == entity_id), None)
                    if entity:
                        chat_output += f"**{entity.entity_name}** relationships:\n"
                        for target_entity_id, rel_list in entity_rels.items():
                            target_entity = next((e for e in read_result.entities if e.entity_id == target_entity_id), None)
                            if target_entity:
                                for rel in rel_list:
                                    rel_type = rel["type"].replace("_", " ").title()
                                    confidence = rel.get('confidence', 0)
                                    description = rel.get('description', '')
                                    chat_output += f"   • → **{rel_type}** → {target_entity.entity_name}\n"
                                    chat_output += f"     Confidence: {confidence:.2f}\n"
                                    if description:
                                        chat_output += f"     Description: {description}\n"
                        chat_output += "\n"
                
                chat_output += f"💡 **Next Steps:**\n"
                chat_output += f"Please view the detailed entities and relationships in the **Entity Management** section at the top of your screen."
                
                return {
                    "response": chat_output,
                    "success": True,
                    "entities_created": 0,
                    "entities": [entity.model_dump(mode='json') for entity in read_result.entities]
                }
            else:
                chat_output = f"📊 **Relationship Analysis Complete**\n\n"
                chat_output += f"• **Entities Analyzed:** {len(read_result.entities)}\n"
                chat_output += f"• **Relationships Found:** 0\n\n"
                chat_output += f"💡 **No clear relationships detected.** This could mean:\n"
                chat_output += f"• The entities are independent\n"
                chat_output += f"• The relationships are not obvious from the current data\n"
                chat_output += f"• You might want to create more related entities\n\n"
                chat_output += f"Please view the entities in the **Entity Management** section at the top of your screen."
                
                return {
                    "response": chat_output,
                    "success": True,
                    "entities_created": 0,
                    "entities": [entity.model_dump(mode='json') for entity in read_result.entities]
                }
                
        except Exception as e:
            logger.error(f"Error in relationship management: {e}")
            return {
                "response": f"I encountered an error while analyzing relationships: {str(e)}",
                "success": False,
                "entities_created": 0,
                "entities": []
            }
    
    def _handle_help_request(self) -> Dict[str, Any]:
        """Handle help requests"""
        
        help_message = """
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
        
        return {
            "response": help_message,
            "success": True,
            "entities_created": 0,
            "entities": []
        }
    
    def _handle_general_conversation(self, session_id: str, message: str, session) -> Dict[str, Any]:
        """Handle general conversation"""
        
        # Use LLM to generate a helpful response
        prompt = f"""
You are a helpful assistant for entity extraction and management. The user said: "{message}"

Context about this session:
- BC3 fields available: {len(session.context.get('selected_bc3_fields', []))}
- Asset columns available: {len(session.context.get('selected_asset_columns', []))}
- Entities created so far: {len(session.entities_created)}

Provide a helpful response that guides them toward entity extraction or creation. Be friendly and suggest what they can do next.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return {
                "response": response.content,
                "success": True,
                "entities_created": 0,
                "entities": []
            }
        except Exception as e:
            logger.error(f"Error in general conversation: {e}")
            return {
                "response": "I'm here to help with entity extraction and management. You can ask me to extract entities from your data, create new entities, or list existing ones. What would you like to do?",
                "success": True,
                "entities_created": 0,
                "entities": []
            }
    
    def _get_entity_creation_prompt(self, message: str, session) -> str:
        """Generate prompt for entity creation"""
        
        context_info = ""
        if session.context.get('selected_bc3_fields'):
            context_info += f"Available BC3 fields: {len(session.context['selected_bc3_fields'])}\n"
        if session.context.get('selected_asset_columns'):
            context_info += f"Available asset columns: {len(session.context['selected_asset_columns'])}\n"
        
        return f"""
The user wants to create an entity. They said: "{message}"

Context: {context_info}

Based on their request, create a JSON structure for an entity with the following format:
{{
  "entity_name": "Entity Name",
  "entity_type": "business_metric|field|asset|derived_insight",
  "entity_value": "Description of the entity",
  "description": "Detailed description",
  "attributes": [
    {{
      "attribute_name": "Attribute Name",
      "attribute_value": "Attribute Value",
      "attribute_type": "string|numeric|boolean",
      "description": "Attribute description"
    }}
  ]
}}

Return only the JSON, no other text.
        """
    
    def _extract_entity_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract entity data from LLM response"""
        
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                entity_data = json.loads(json_match.group())
                return entity_data
        except Exception as e:
            logger.error(f"Error extracting entity from response: {e}")
        
        return None
    
    def _enhance_response_with_relationships(self, result: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Enhance response with relationship information"""
        try:
            # Get all entities for the session to analyze relationships
            from entity_collection_models import ReadEntityRequest
            read_request = ReadEntityRequest(session_id=session_id)
            read_result = self.entity_manager.read_entities(read_request)
            
            if read_result.success and len(read_result.entities) > 1:
                # Detect relationships
                relationships = self.relationship_detector.detect_relationships(read_result.entities)
                
                if relationships:
                    # Count relationships found
                    total_relationships = sum(len(rel_list) for rel_list in relationships.values())
                    
                    # Create enhanced response
                    original_response = result.get('response', '')
                    
                    enhanced_response = f"{original_response}\n\n"
                    enhanced_response += f"🔗 **Relationship Analysis:**\n"
                    enhanced_response += f"• **Entities Created:** {result.get('entities_created', 0)}\n"
                    enhanced_response += f"• **Total Entities in Session:** {len(read_result.entities)}\n"
                    enhanced_response += f"• **Relationships Detected:** {total_relationships}\n\n"
                    
                    # Add entity details
                    enhanced_response += f"📋 **Created Entities:**\n\n"
                    for i, entity in enumerate(read_result.entities, 1):
                        enhanced_response += f"**{i}. {entity.entity_name}** ({entity.entity_type.value})\n"
                        enhanced_response += f"   • **Description:** {entity.description}\n"
                        enhanced_response += f"   • **Attributes:** {len(entity.attributes)} attributes\n"
                        if entity.attributes:
                            for attr in entity.attributes[:2]:  # Show first 2 attributes
                                attr_value = str(attr.attribute_value) if attr.attribute_value is not None else "None"
                                enhanced_response += f"     - {attr.attribute_name}: {attr_value}\n"
                            if len(entity.attributes) > 2:
                                enhanced_response += f"     - ... and {len(entity.attributes) - 2} more\n"
                        enhanced_response += "\n"
                    
                    # Add relationship details
                    enhanced_response += f"🔗 **Detected Relationships:**\n\n"
                    for entity_id, entity_rels in relationships.items():
                        entity = next((e for e in read_result.entities if e.entity_id == entity_id), None)
                        if entity:
                            for target_entity_id, rel_list in entity_rels.items():
                                target_entity = next((e for e in read_result.entities if e.entity_id == target_entity_id), None)
                                if target_entity:
                                    for rel in rel_list:
                                        rel_type = rel["type"].replace("_", " ").title()
                                        enhanced_response += f"• {entity.entity_name} → **{rel_type}** → {target_entity.entity_name}\n"
                    enhanced_response += "\n"
                    
                    enhanced_response += f"💡 **Next Steps:**\n"
                    enhanced_response += f"Please view the detailed entities and relationships in the **Entity Management** section at the top of your screen."
                    
                    result['response'] = enhanced_response
                    logger.info("Enhanced response with relationship information")
            
            return result
            
        except Exception as e:
            logger.error(f"Error enhancing response with relationships: {e}")
            return result
