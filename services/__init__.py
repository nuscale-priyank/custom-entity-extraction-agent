"""
Services package for BC3 AI Agent
Contains all service classes for handling different aspects of the system
"""

from .simple_agent import SimpleAgent
from .agent import ConversationalAgent
from .entity_collection_manager import EntityCollectionManager
from .chat_session_manager import ChatSessionManager
from .relationship_detector import RelationshipDetector

__all__ = [
    'SimpleAgent',
    'ConversationalAgent',
    'EntityCollectionManager',
    'ChatSessionManager', 
    'RelationshipDetector'
]
