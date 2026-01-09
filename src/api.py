"""
API Gateway - FastAPI application for chatbot
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import uvicorn

from .orchestrator import AgentOrchestrator
from .rbac.framework import RBACFramework
from .agents import RunningAgent, ValidationAgent, QualityAgent
from .semantic_store import SemanticStore
from .llm_client import LLMClient


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Semantic Data Chatbot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (should be initialized on startup)
rbac: Optional[RBACFramework] = None
orchestrator: Optional[AgentOrchestrator] = None


# Request/Response models
class QueryRequest(BaseModel):
    query: str
    validate: bool = True
    track_quality: bool = True
    context_limit: int = 5


class QueryResponse(BaseModel):
    response: str
    query: str
    metadata: Dict[str, Any]
    validation: Optional[Dict[str, Any]] = None
    quality: Optional[Dict[str, Any]] = None


class StatusResponse(BaseModel):
    status: str
    agents: Dict[str, Any]


def get_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """Extract user ID from header"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID required in X-User-Id header")
    return x_user_id


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global rbac, orchestrator
    
    logger.info("Initializing services...")
    
    # Initialize RBAC
    rbac = RBACFramework(db_path="rbac.db")
    
    # Create default admin user if not exists
    try:
        rbac.create_user("admin", "admin", "admin@example.com")
        rbac.assign_role("admin", "admin")
    except Exception:
        pass  # User might already exist
    
    # Initialize semantic store
    semantic_store = SemanticStore(collection_name="semantic_data")
    
    # Initialize LLM client (using Ollama by default)
    import os
    from .config import LLM_PROVIDER, LLM_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY
    
    llm_provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER)
    llm_model = os.getenv("LLM_MODEL", LLM_MODEL)
    
    if llm_provider == "ollama":
        ollama_url = os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)
        llm_client = LLMClient(provider="ollama", model=llm_model, base_url=ollama_url)
        logger.info(f"Using Ollama with model: {llm_model} at {ollama_url}")
    else:
        llm_client = LLMClient(provider=llm_provider, model=llm_model, api_key=OPENAI_API_KEY)
        logger.info(f"Using {llm_provider} with model: {llm_model}")
    
    # Initialize agents
    running_agent = RunningAgent(
        agent_id="running_001",
        rbac=rbac,
        user_id="admin",
        semantic_store=semantic_store,
        llm_client=llm_client
    )
    
    validation_agent = ValidationAgent(
        agent_id="validation_001",
        rbac=rbac,
        user_id="admin",
        semantic_store=semantic_store
    )
    
    quality_agent = QualityAgent(
        agent_id="quality_001",
        rbac=rbac,
        user_id="admin",
        metrics_db_path="quality_metrics.db"
    )
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(
        rbac=rbac,
        user_id="admin",
        running_agent=running_agent,
        validation_agent=validation_agent,
        quality_agent=quality_agent
    )
    
    logger.info("Services initialized successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Semantic Data Chatbot API", "version": "1.0.0"}


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, user_id: str = Depends(get_user_id)):
    """
    Process a chatbot query
    
    Args:
        request: Query request
        user_id: User ID from header
        
    Returns:
        Query response
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Update orchestrator user_id for this request
        orchestrator.user_id = user_id
        
        result = orchestrator.process_query(
            query=request.query,
            validate=request.validate,
            track_quality=request.track_quality,
            context_limit=request.context_limit
        )
        
        return QueryResponse(**result)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status", response_model=StatusResponse)
async def get_status(user_id: str = Depends(get_user_id)):
    """Get system status"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        orchestrator.user_id = user_id
        status = orchestrator.get_system_status()
        return StatusResponse(status="operational", agents=status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/quality")
async def get_quality_report(user_id: str = Depends(get_user_id)):
    """Get quality report"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        orchestrator.user_id = user_id
        report = orchestrator.get_quality_report()
        return report
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting quality report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
