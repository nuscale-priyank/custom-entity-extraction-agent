"""
Configuration management for the Custom Entity Extraction Agent
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuration for the agent"""
    project_id: str
    location: str = "us-central1"
    model_name: str = "gemini-2.5-flash-lite"
    temperature: float = 0.1
    max_output_tokens: int = 2048


@dataclass
class SessionConfig:
    """Configuration for session management"""
    manager_type: str = "memory"  # memory, firestore, redis, mongodb
    cleanup_interval_hours: int = 24
    max_session_age_hours: int = 24
    
    # Firestore settings
    firestore_project_id: str = "trial-247123"
    firestore_database: str = "(default)"  # Firestore database name
    firestore_collection: str = "chat_sessions"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    redis_key_prefix: str = "chat_session:"
    redis_ttl_hours: int = 24
    
    # MongoDB settings
    mongodb_connection_string: str = "mongodb://localhost:27017"
    mongodb_database: str = "chat_agent"
    mongodb_collection: str = "sessions"


@dataclass
class LoggingConfig:
    """Configuration for logging"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None


def load_config_from_env() -> tuple[AgentConfig, SessionConfig, LoggingConfig]:
    """Load configuration from environment variables"""
    
    # Agent configuration
    agent_config = AgentConfig(
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "trial-247123"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        model_name=os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash-lite"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        max_output_tokens=int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "2048"))
    )
    
    # Session configuration - Use memory for development
    session_config = SessionConfig(
        manager_type=os.getenv("SESSION_MANAGER_TYPE", "memory"),
        cleanup_interval_hours=int(os.getenv("SESSION_MANAGER_CLEANUP_INTERVAL_HOURS", "24")),
        max_session_age_hours=int(os.getenv("SESSION_MANAGER_MAX_AGE_HOURS", "24")),
        firestore_project_id=os.getenv("FIRESTORE_PROJECT_ID", "trial-247123"),
        firestore_database=os.getenv("FIRESTORE_DATABASE", "(default)"),
        firestore_collection=os.getenv("FIRESTORE_COLLECTION", "chat_sessions"),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        redis_key_prefix=os.getenv("REDIS_KEY_PREFIX", "chat_session:"),
        redis_ttl_hours=int(os.getenv("REDIS_TTL_HOURS", "24")),
        mongodb_connection_string=os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017"),
        mongodb_database=os.getenv("MONGODB_DATABASE", "chat_agent"),
        mongodb_collection=os.getenv("MONGODB_COLLECTION", "sessions")
    )
    
    # Logging configuration
    logging_config = LoggingConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        file_path=os.getenv("LOG_FILE_PATH")
    )
    
    return agent_config, session_config, logging_config


def get_session_manager_kwargs(session_config: SessionConfig) -> dict:
    """Get keyword arguments for session manager creation"""
    
    if session_config.manager_type == "firestore":
        return {
            "project_id": session_config.firestore_project_id,
            "collection_name": session_config.firestore_collection
        }
    elif session_config.manager_type == "redis":
        return {
            "redis_url": session_config.redis_url,
            "key_prefix": session_config.redis_key_prefix,
            "ttl_hours": session_config.redis_ttl_hours
        }
    elif session_config.manager_type == "mongodb":
        return {
            "connection_string": session_config.mongodb_connection_string,
            "database_name": session_config.mongodb_database,
            "collection_name": session_config.mongodb_collection
        }
    else:
        return {}


# Default configuration
DEFAULT_AGENT_CONFIG = AgentConfig(
    project_id="trial-247123",
    location="us-central1"
)

DEFAULT_SESSION_CONFIG = SessionConfig(
    manager_type="memory"
)

DEFAULT_LOGGING_CONFIG = LoggingConfig(
    level="INFO"
)
