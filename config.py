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
    manager_type: str = "memory"  # memory, firestore
    
    # Firestore settings
    firestore_project_id: str = "firestore-470903"
    firestore_database: str = "(default)"  # Firestore database name
    firestore_collection: str = "chat_sessions"


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
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "firestore-470903"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        model_name=os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash-lite"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        max_output_tokens=int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "2048"))
    )
    
    # Session configuration - Use memory for development
    session_config = SessionConfig(
        manager_type=os.getenv("SESSION_MANAGER_TYPE", "memory"),
        firestore_project_id=os.getenv("FIRESTORE_PROJECT_ID", "firestore-470903"),
        firestore_database=os.getenv("FIRESTORE_DATABASE", "(default)"),
        firestore_collection=os.getenv("FIRESTORE_COLLECTION", "chat_sessions")
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
    else:
        return {}


# Default configuration
DEFAULT_AGENT_CONFIG = AgentConfig(
    project_id="firestore-470903",
    location="us-central1"
)

DEFAULT_SESSION_CONFIG = SessionConfig(
    manager_type="memory"
)

DEFAULT_LOGGING_CONFIG = LoggingConfig(
    level="INFO"
)
