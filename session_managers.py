"""
Session managers for different storage backends
Supports Firestore, Redis, MongoDB, and in-memory storage
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
            doc_ref = self.collection.document(session_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                # Update last accessed timestamp
                doc_ref.update({"last_accessed": firestore.SERVER_TIMESTAMP})
                return ChatState(**data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting session {session_id} from Firestore: {e}")
            return None
    
    def save_session(self, session_id: str, chat_state: ChatState) -> bool:
        try:
            data = chat_state.dict()
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
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
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


class RedisSessionManager(SessionManager):
    """Redis-based session manager for high-performance production use"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 key_prefix: str = "chat_session:", 
                 ttl_hours: int = 24):
        try:
            import redis
            self.redis_client = redis.from_url(redis_url)
            self.key_prefix = key_prefix
            self.ttl_seconds = ttl_hours * 3600
            logger.info(f"Redis session manager initialized with TTL: {ttl_hours}h")
        except ImportError:
            raise ImportError("redis not installed. Run: pip install redis")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[ChatState]:
        try:
            key = f"{self.key_prefix}{session_id}"
            data = self.redis_client.get(key)
            
            if data:
                # Extend TTL on access
                self.redis_client.expire(key, self.ttl_seconds)
                return ChatState(**json.loads(data))
            return None
            
        except Exception as e:
            logger.error(f"Error getting session {session_id} from Redis: {e}")
            return None
    
    def save_session(self, session_id: str, chat_state: ChatState) -> bool:
        try:
            key = f"{self.key_prefix}{session_id}"
            data = json.dumps(chat_state.dict())
            
            # Set with TTL
            self.redis_client.setex(key, self.ttl_seconds, data)
            return True
            
        except Exception as e:
            logger.error(f"Error saving session {session_id} to Redis: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        try:
            key = f"{self.key_prefix}{session_id}"
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting session {session_id} from Redis: {e}")
            return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        # Redis automatically handles TTL, so no manual cleanup needed
        logger.info("Redis automatically handles TTL expiration")
        return 0


class MongoDBSessionManager(SessionManager):
    """MongoDB-based session manager for production use"""
    
    def __init__(self, connection_string: str, database_name: str = "chat_agent", 
                 collection_name: str = "sessions"):
        try:
            from pymongo import MongoClient
            from pymongo.errors import ConnectionFailure
            
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            
            # Create indexes for performance
            self.collection.create_index("last_accessed", expireAfterSeconds=0)
            self.collection.create_index("session_id", unique=True)
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"MongoDB session manager initialized for database: {database_name}")
            
        except ImportError:
            raise ImportError("pymongo not installed. Run: pip install pymongo")
        except ConnectionFailure:
            raise ConnectionError("Failed to connect to MongoDB")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[ChatState]:
        try:
            doc = self.collection.find_one({"session_id": session_id})
            
            if doc:
                # Update last accessed timestamp
                self.collection.update_one(
                    {"session_id": session_id},
                    {"$set": {"last_accessed": datetime.utcnow()}}
                )
                
                # Remove MongoDB-specific fields
                doc.pop("_id", None)
                doc.pop("last_accessed", None)
                doc.pop("last_updated", None)
                
                return ChatState(**doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting session {session_id} from MongoDB: {e}")
            return None
    
    def save_session(self, session_id: str, chat_state: ChatState) -> bool:
        try:
            data = chat_state.dict()
            data["last_updated"] = datetime.utcnow()
            data["last_accessed"] = datetime.utcnow()
            
            # Upsert session
            self.collection.replace_one(
                {"session_id": session_id},
                data,
                upsert=True
            )
            return True
            
        except Exception as e:
            logger.error(f"Error saving session {session_id} to MongoDB: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        try:
            result = self.collection.delete_one({"session_id": session_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting session {session_id} from MongoDB: {e}")
            return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            result = self.collection.delete_many({
                "last_accessed": {"$lt": cutoff_time}
            })
            
            deleted_count = result.deleted_count
            logger.info(f"Cleaned up {deleted_count} expired sessions from MongoDB")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0


def create_session_manager(manager_type: str, **kwargs) -> SessionManager:
    """Factory function to create session managers"""
    
    managers = {
        "memory": InMemorySessionManager,
        "firestore": FirestoreSessionManager,
        "redis": RedisSessionManager,
        "mongodb": MongoDBSessionManager
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
