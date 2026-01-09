"""
Configuration management
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "databases"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "llama2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Semantic Store Configuration
SEMANTIC_STORE_COLLECTION = os.getenv("SEMANTIC_STORE_COLLECTION", "semantic_data")
SEMANTIC_STORE_DIR = os.getenv("SEMANTIC_STORE_DIR", str(DB_DIR / "chroma_db"))

# RBAC Configuration
RBAC_DB_PATH = os.getenv("RBAC_DB_PATH", str(DB_DIR / "rbac.db"))

# Quality Metrics Configuration
QUALITY_DB_PATH = os.getenv("QUALITY_DB_PATH", str(DB_DIR / "quality_metrics.db"))

# Agent Configuration
RUNNING_AGENT_ID = os.getenv("RUNNING_AGENT_ID", "running_001")
VALIDATION_AGENT_ID = os.getenv("VALIDATION_AGENT_ID", "validation_001")
QUALITY_AGENT_ID = os.getenv("QUALITY_AGENT_ID", "quality_001")

# Validation Policies
VALIDATION_POLICIES = {
    "min_length": int(os.getenv("VALIDATION_MIN_LENGTH", "10")),
    "max_length": int(os.getenv("VALIDATION_MAX_LENGTH", "10000")),
    "unsafe_patterns": [],
    "rules": []
}

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "chatbot.log"))
