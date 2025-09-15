"""
Simplified Entity Extraction Agent
- Single tool: create_entities
- Direct LLM interaction
- Minimal complexity
"""

import json
import logging
from typing import Dict, List, Any
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate

from config import Config
from tools import create_entities, get_all_tools
from prompts import get_system_prompt, get_context_prompt

logger = logging.getLogger(__name__)


class SimpleAgent:
    """Simplified agent with minimal complexity"""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or Config.get_project_id()
        self.llm = ChatVertexAI(
            model_name=Config.get_model_name(),
            project=self.project_id,
            location=Config.LOCATION,
            temperature=Config.get_temperature(),
            max_output_tokens=Config.get_max_output_tokens()
        )
        self.tools = get_all_tools()
        
        logger.info("Simple Agent initialized")
    
    def process_request(self, message: str, session_id: str, 
                       selected_bc3_fields: List[Dict] = None,
                       selected_asset_columns: List[Dict] = None) -> Dict[str, Any]:
        """Process a single request with minimal complexity"""
        
        try:
            logger.info(f"Processing request for session: {session_id}")
            
            # Prepare context
            context = get_context_prompt(selected_bc3_fields, selected_asset_columns)
            logger.info(f"Context length: {len(context)} characters")
            logger.info(f"Context preview: {context[:300]}...")
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", get_system_prompt()),
                ("human", f"{message}\n\nContext:\n{context}")
            ])
            
            logger.info(f"System prompt length: {len(get_system_prompt())} characters")
            logger.info(f"Full prompt length: {len(message) + len(context) + len(get_system_prompt())} characters")
            
            # Create chain with tools
            chain = prompt | self.llm.bind_tools(self.tools)
            
            # Generate response
            response = chain.invoke({"message": message})
            
            logger.info(f"LLM response: {len(response.content)} characters")
            logger.info(f"LLM response content: {response.content[:500]}...")
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response attributes: {dir(response)}")
            
            # Check for tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info(f"Found {len(response.tool_calls)} tool calls")
                
                # Execute tool calls
                for tool_call in response.tool_calls:
                    if tool_call['name'] == 'create_entities':
                        # Execute the tool
                        tool_result = create_entities.invoke({
                            'session_id': session_id,
                            'entities_data': tool_call['args']['entities_data']
                        })
                        
                        logger.info(f"Tool executed: {tool_result[:200]}...")
                        
                        # Parse result
                        result = json.loads(tool_result)
                        if result['success']:
                            logger.info(f"Successfully created {result['total_created']} entities")
                            # Generate a meaningful response since response.content might be empty
                            entity_names = [entity.get('entity_name', 'Unknown') for entity in result['entities']]
                            response_text = f"✅ Successfully created {result['total_created']} entities: {', '.join(entity_names)}"
                            return {
                                "response": response_text,
                                "success": True,
                                "entities_created": result['total_created'],
                                "entities": result['entities']
                            }
                        else:
                            logger.error(f"Tool failed: {result['message']}")
                            return {
                                "response": f"Error: {result['message']}",
                                "success": False,
                                "entities_created": 0,
                                "entities": []
                            }
            
            # No tool calls made
            logger.warning("No tool calls made by LLM")
            return {
                "response": response.content,
                "success": False,
                "entities_created": 0,
                "entities": []
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "response": f"Error: {str(e)}",
                "success": False,
                "entities_created": 0,
                "entities": []
            }
    
