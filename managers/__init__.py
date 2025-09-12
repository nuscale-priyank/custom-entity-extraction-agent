"""
Managers package for BC3 AI Agent
Contains all manager classes for handling different aspects of the system
"""

from .entity_collection_manager import EntityCollectionManager
from .chat_session_manager import ChatSessionManager
from .relationship_detector import RelationshipDetector

__all__ = [
    'EntityCollectionManager',
    'ChatSessionManager', 
    'RelationshipDetector'
]
