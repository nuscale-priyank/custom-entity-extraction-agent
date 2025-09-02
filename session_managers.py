"""
Session managers for different storage backends
Supports Firestore and in-memory storage
"""

import json
import pickle
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from models import ChatState

logger = logging.getLogger(__name__)


class SessionManager(ABC):
    """Abstract session manager interface for different storage backends"""
    
    @abstractmethod
    def get_session(self, session_id: str) -> Optional[ChatState]:
        """Get session by ID"""
        pass
    
    @abstractmethod
    def save_session(self, session_id: str, chat_state: ChatState) -> bool:
        """Save session"""
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        pass
    
    @abstractmethod
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up expired sessions, returns number of cleaned sessions"""
        pass


class InMemorySessionManager(SessionManager):
    """In-memory session manager for development/testing"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timestamps: Dict[str, datetime] = {}
    
    def get_session(self, session_id: str) -> Optional[ChatState]:
        if session_id in self.sessions:
            try:
                # Update timestamp on access
                self.session_timestamps[session_id] = datetime.now()
                return ChatState(**self.sessions[session_id])
            except Exception as e:
                logger.error(f"Error deserializing session {session_id}: {e}")
                return None
        return None
    
    def save_session(self, session_id: str, chat_state: ChatState) -> bool:
        try:
            self.sessions[session_id] = chat_state.model_dump()
            self.session_timestamps[session_id] = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self.session_timestamps:
                del self.session_timestamps[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        expired_sessions = [
            sid for sid, timestamp in self.session_timestamps.items()
            if timestamp < cutoff_time
        ]
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        return len(expired_sessions)


class FirestoreSessionManager(SessionManager):
    """Firestore-based session manager for production use"""
    
    def __init__(self, project_id: str, collection_name: str = "chat_sessions"):
        try:
            from google.cloud import firestore
            self.db = firestore.Client(project=project_id)
            self.collection = self.db.collection(collection_name)
            logger.info(f"Firestore session manager initialized for project: {project_id}")
        except ImportError:
            raise ImportError("google-cloud-firestore not installed. Run: pip install google-cloud-firestore")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[ChatState]:
        try:
            from google.cloud import firestore
            doc = self.collection.document(session_id).get()
            
            if doc.exists:
                data = doc.to_dict()
                # Update last accessed timestamp
                self.collection.document(session_id).update({
                    "last_accessed": firestore.SERVER_TIMESTAMP
                })
                
                # Remove Firestore-specific fields
                data.pop("last_accessed", None)
                data.pop("last_updated", None)
                
                return ChatState(**data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting session {session_id} from Firestore: {e}")
            return None
    
    def save_session(self, session_id: str, chat_state: ChatState) -> bool:
        try:
            from google.cloud import firestore
            data = chat_state.model_dump()
            data["last_updated"] = firestore.SERVER_TIMESTAMP
            data["last_accessed"] = firestore.SERVER_TIMESTAMP
            
            self.collection.document(session_id).set(data)
            return True
            
        except Exception as e:
            logger.error(f"Error saving session {session_id} to Firestore: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        try:
            self.collection.document(session_id).delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting session {session_id} from Firestore: {e}")
            return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Query for expired sessions
            expired_docs = self.collection.where(
                "last_accessed", "<", cutoff_time
            ).stream()
            
            deleted_count = 0
            for doc in expired_docs:
                doc.reference.delete()
                deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} expired sessions from Firestore")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0


def create_session_manager(manager_type: str, **kwargs) -> SessionManager:
    """Factory function to create session managers"""
    
    managers = {
        "memory": InMemorySessionManager,
        "firestore": FirestoreSessionManager
    }
    
    if manager_type not in managers:
        raise ValueError(f"Unknown session manager type: {manager_type}. "
                       f"Available types: {list(managers.keys())}")
    
    try:
        return managers[manager_type](**kwargs)
    except Exception as e:
        logger.error(f"Failed to create {manager_type} session manager: {e}")
        # Fallback to in-memory
        logger.info("Falling back to in-memory session manager")
        return InMemorySessionManager()
