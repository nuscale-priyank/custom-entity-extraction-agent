"""
Chat Session Manager for handling conversation history and context
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from google.cloud import firestore
from pydantic import BaseModel

from config import Config

logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    """Individual chat message"""
    message_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = {}


class ChatSession(BaseModel):
    """Chat session with conversation history"""
    session_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage]
    context: Dict[str, Any]  # BC3 fields, asset columns, etc.
    entities_created: List[str]  # List of entity IDs created in this session
    status: str = "active"  # "active", "completed", "archived"


class ChatSessionManager:
    """Manages chat sessions and conversation history"""
    
    def __init__(self, project_id: str, collection_name: str = None, database_id: str = None):
        """
        Initialize the Chat Session Manager.
        
        Args:
            project_id: Google Cloud Project ID
            collection_name: Name of the Firestore collection for chat sessions (defaults to config)
            database_id: Firestore database ID (defaults to config)
        """
        self.project_id = project_id
        self.collection_name = collection_name or Config.FIRESTORE_COLLECTION_CHAT_SESSIONS
        self.database_id = database_id or Config.get_database_id()
        self.db = firestore.Client(project=project_id, database=self.database_id)
        self.collection = self.db.collection(self.collection_name)
        
        logger.info(f"ChatSessionManager initialized for project: {project_id}")
        logger.info(f"Using database: {self.database_id}")
        logger.info(f"Using collection: {self.collection_name}")
    
    def create_session(self, session_id: str, initial_context: Dict[str, Any] = None) -> ChatSession:
        """Create a new chat session"""
        try:
            now = datetime.utcnow()
            session = ChatSession(
                session_id=session_id,
                created_at=now,
                updated_at=now,
                messages=[],
                context=initial_context or {},
                entities_created=[],
                status="active"
            )
            
            # Save to Firestore
            doc_ref = self.collection.document(session_id)
            doc_ref.set(session.model_dump(mode='json'))
            
            logger.info(f"Created new chat session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get an existing chat session"""
        try:
            doc_ref = self.collection.document(session_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                
                # Validate that we have the required fields
                required_fields = ['session_id', 'created_at', 'updated_at', 'messages', 'context', 'entities_created']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    logger.error(f"Missing required fields in session data: {missing_fields}")
                    logger.error(f"Available fields: {list(data.keys())}")
                    logger.error(f"Data structure: {data}")
                    return None
                
                # Convert Firestore timestamps back to datetime
                for message in data.get('messages', []):
                    if 'timestamp' in message and hasattr(message['timestamp'], 'to_pydatetime'):
                        message['timestamp'] = message['timestamp'].to_pydatetime()
                if 'created_at' in data and hasattr(data['created_at'], 'to_pydatetime'):
                    data['created_at'] = data['created_at'].to_pydatetime()
                if 'updated_at' in data and hasattr(data['updated_at'], 'to_pydatetime'):
                    data['updated_at'] = data['updated_at'].to_pydatetime()
                
                # Ensure data types are correct
                if not isinstance(data.get('messages'), list):
                    data['messages'] = []
                if not isinstance(data.get('context'), dict):
                    data['context'] = {}
                if not isinstance(data.get('entities_created'), list):
                    data['entities_created'] = []
                
                return ChatSession(**data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting chat session: {e}")
            logger.error(f"Session ID: {session_id}")
            return None
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a message to the chat session"""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found, creating new one")
                session = self.create_session(session_id)
            
            # Create new message
            message = ChatMessage(
                message_id=f"msg_{datetime.utcnow().timestamp()}",
                role=role,
                content=content,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Add to session
            session.messages.append(message)
            session.updated_at = datetime.utcnow()
            
            # Save to Firestore
            doc_ref = self.collection.document(session_id)
            doc_ref.set(session.model_dump(mode='json'))
            
            logger.info(f"Added {role} message to session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to session: {e}")
            return False
    
    def update_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """Update the session context (BC3 fields, asset columns, etc.)"""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found")
                return False
            
            # Update context
            session.context.update(context_updates)
            session.updated_at = datetime.utcnow()
            
            # Save to Firestore
            doc_ref = self.collection.document(session_id)
            doc_ref.set(session.model_dump(mode='json'))
            
            logger.info(f"Updated context for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating session context: {e}")
            return False
    
    def add_created_entity(self, session_id: str, entity_id: str) -> bool:
        """Add an entity ID to the list of created entities"""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found")
                return False
            
            if entity_id not in session.entities_created:
                session.entities_created.append(entity_id)
                session.updated_at = datetime.utcnow()
                
                # Save to Firestore
                doc_ref = self.collection.document(session_id)
                doc_ref.set(session.model_dump(mode='json'))
                
                logger.info(f"Added entity {entity_id} to session {session_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding entity to session: {e}")
            return False
    
    def remove_created_entity(self, session_id: str, entity_id: str) -> bool:
        """Remove an entity ID from the list of created entities"""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found")
                return False
            
            if entity_id in session.entities_created:
                session.entities_created.remove(entity_id)
                session.updated_at = datetime.utcnow()
                
                # Save to Firestore
                doc_ref = self.collection.document(session_id)
                doc_ref.set(session.model_dump(mode='json'))
                
                logger.info(f"Removed entity {entity_id} from session {session_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing entity from session: {e}")
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """Get recent conversation history"""
        try:
            session = self.get_session(session_id)
            if not session:
                return []
            
            # Return last N messages
            return session.messages[-limit:] if session.messages else []
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the session"""
        try:
            session = self.get_session(session_id)
            if not session:
                return {}
            
            return {
                "session_id": session.session_id,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": len(session.messages),
                "entities_created_count": len(session.entities_created),
                "has_bc3_fields": bool(session.context.get('selected_bc3_fields')),
                "has_asset_columns": bool(session.context.get('selected_asset_columns')),
                "status": session.status
            }
            
        except Exception as e:
            logger.error(f"Error getting session summary: {e}")
            return {}
    
    def delete_corrupted_session(self, session_id: str) -> bool:
        """Delete a corrupted session from Firestore"""
        try:
            doc_ref = self.collection.document(session_id)
            doc_ref.delete()
            logger.info(f"Deleted corrupted session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting corrupted session: {e}")
            return False
