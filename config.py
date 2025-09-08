"""
Configuration settings for the BC3 AI Agent
"""

import os
from typing import Optional

class Config:
    """Configuration class for the agent"""
    
    # Google Cloud settings
    PROJECT_ID: str = "firestore-470903"
    LOCATION: str = "us-central1"
    DATABASE_ID: str = "llmops-demo-track2"
    
    # LLM settings
    MODEL_NAME: str = "gemini-2.5-pro"
    TEMPERATURE: float = 0
    MAX_OUTPUT_TOKENS: int = 64000
    
    # Firestore settings
    FIRESTORE_COLLECTION_CHAT_SESSIONS: str = "chat_sessions"
    FIRESTORE_COLLECTION_CUSTOM_ENTITIES: str = "custom_entities"
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    @classmethod
    def get_project_id(cls) -> str:
        """Get project ID from environment or default"""
        return os.getenv("GOOGLE_CLOUD_PROJECT", cls.PROJECT_ID)
    
    @classmethod
    def get_model_name(cls) -> str:
        """Get model name from environment or default"""
        return os.getenv("LLM_MODEL_NAME", cls.MODEL_NAME)
    
    @classmethod
    def get_temperature(cls) -> float:
        """Get temperature from environment or default"""
        return float(os.getenv("LLM_TEMPERATURE", cls.TEMPERATURE))
    
    @classmethod
    def get_max_output_tokens(cls) -> int:
        """Get max output tokens from environment or default"""
        return int(os.getenv("LLM_MAX_OUTPUT_TOKENS", cls.MAX_OUTPUT_TOKENS))
    
    @classmethod
    def get_database_id(cls) -> str:
        """Get database ID from environment or default"""
        return os.getenv("FIRESTORE_DATABASE_ID", cls.DATABASE_ID)
