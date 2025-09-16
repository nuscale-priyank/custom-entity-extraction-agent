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
    
    # Default user settings
    DEFAULT_USER_ID: str = "default_user"
    
    # Thread settings
    THREAD_PREFIX: str = "thread"
    
    # Conversation settings
    DEFAULT_CONVERSATION_LIMIT: int = 10
    
    # PostgreSQL settings for LangGraph persistence
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "mysecretpassword"
    POSTGRES_DATABASE: str = "postgres"
    POSTGRES_SCHEMA: str = "public"
    
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
    
    @classmethod
    def get_default_user_id(cls) -> str:
        """Get default user ID from environment or default"""
        return os.getenv("DEFAULT_USER_ID", cls.DEFAULT_USER_ID)
    
    @classmethod
    def get_thread_prefix(cls) -> str:
        """Get thread prefix from environment or default"""
        return os.getenv("THREAD_PREFIX", cls.THREAD_PREFIX)
    
    @classmethod
    def get_default_conversation_limit(cls) -> int:
        """Get default conversation limit from environment or default"""
        return int(os.getenv("DEFAULT_CONVERSATION_LIMIT", cls.DEFAULT_CONVERSATION_LIMIT))
    
    @classmethod
    def get_postgres_host(cls) -> str:
        """Get PostgreSQL host from environment or default"""
        return os.getenv("POSTGRES_HOST", cls.POSTGRES_HOST)
    
    @classmethod
    def get_postgres_port(cls) -> int:
        """Get PostgreSQL port from environment or default"""
        return int(os.getenv("POSTGRES_PORT", cls.POSTGRES_PORT))
    
    @classmethod
    def get_postgres_user(cls) -> str:
        """Get PostgreSQL user from environment or default"""
        return os.getenv("POSTGRES_USER", cls.POSTGRES_USER)
    
    @classmethod
    def get_postgres_password(cls) -> str:
        """Get PostgreSQL password from environment or default"""
        return os.getenv("POSTGRES_PASSWORD", cls.POSTGRES_PASSWORD)
    
    @classmethod
    def get_postgres_database(cls) -> str:
        """Get PostgreSQL database from environment or default"""
        return os.getenv("POSTGRES_DATABASE", cls.POSTGRES_DATABASE)
    
    @classmethod
    def get_postgres_schema(cls) -> str:
        """Get PostgreSQL schema from environment or default"""
        return os.getenv("POSTGRES_SCHEMA", cls.POSTGRES_SCHEMA)
    
    @classmethod
    def get_postgres_connection_string(cls) -> str:
        """Get PostgreSQL connection string"""
        return f"postgresql://{cls.get_postgres_user()}:{cls.get_postgres_password()}@{cls.get_postgres_host()}:{cls.get_postgres_port()}/{cls.get_postgres_database()}"
