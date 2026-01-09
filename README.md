# Generic Semantic Data Chatbot - Multi-Agent System

A production-ready semantic data chatbot with a multi-agent architecture featuring RBAC (Role-Based Access Control) for secure operations.

![Overview](./unnamed (5).png)

## Features

- **Multi-Agent Architecture**: Three specialized agents (Running, Validation, Quality)
- **RBAC Framework**: Role-based access control for secure agent operations
- **Semantic Search**: Vector-based semantic search using ChromaDB
- **LLM Integration**: Ollama (default) or OpenAI GPT-4 integration
- **Executive Dashboard**: Real-time visual monitoring of agents and RBAC
- **Quality Monitoring**: Built-in quality metrics and reporting
- **RESTful API**: FastAPI-based API gateway
- **Comprehensive Validation**: Multi-layer response validation
- **Event Tracking**: Complete audit trail of agent calls and RBAC checks

## Architecture

The system consists of:

1. **Running Agent**: Executes queries and generates responses
2. **Validation Agent**: Validates responses before delivery
3. **Quality Agent**: Monitors and analyzes system quality
4. **RBAC Framework**: Manages roles and permissions
5. **Agent Orchestrator**: Coordinates agent interactions
6. **API Gateway**: RESTful API for external access

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed diagrams.

## Installation

### Prerequisites

- Python 3.10+
- Ollama installed and running (default) OR OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd semantic-with-chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install and start Ollama (if not already installed):
```bash
# Install Ollama (see https://ollama.ai)
# Then pull a model:
ollama pull llama2
# Or use another model like: mistral, codellama, etc.
```

4. Set up environment variables (optional):
```bash
cp .env.example .env
# Edit .env if you want to customize settings
# Default uses Ollama at http://localhost:11434
```

5. Initialize the database:
```bash
python -m src.setup
```

## Usage

### Option 1: Executive Dashboard (Recommended for Demos)

The dashboard provides a visual, real-time view of agent execution and RBAC enforcement:

```bash
# Generate demo data (optional)
python3 demo_dashboard.py

# Start dashboard
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501` with:
- Real-time agent activity visualization
- RBAC permission monitoring
- Interactive charts and metrics
- Live query execution

See [README_DASHBOARD.md](README_DASHBOARD.md) for dashboard details.

### Option 2: Starting the API Server

```bash
python -m src.api
# or
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Process Query
```bash
curl -X POST "http://localhost:8000/query" \
  -H "X-User-Id: admin" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is semantic search?",
    "validate": true,
    "track_quality": true
  }'
```

#### Get Status
```bash
curl -X GET "http://localhost:8000/status" \
  -H "X-User-Id: admin"
```

#### Get Quality Report
```bash
curl -X GET "http://localhost:8000/quality" \
  -H "X-User-Id: admin"
```

### Python API Usage

```python
from src.rbac import RBACFramework
from src.agents import RunningAgent, ValidationAgent, QualityAgent
from src.orchestrator import AgentOrchestrator
from src.semantic_store import SemanticStore
from src.llm_client import LLMClient

# Initialize components
rbac = RBACFramework()
semantic_store = SemanticStore()

# Use Ollama (default)
llm_client = LLMClient(provider="ollama", model="llama2")

# Or use OpenAI
# llm_client = LLMClient(provider="openai", model="gpt-4", api_key="your-key")

# Create agents
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
    user_id="admin"
)

# Create orchestrator
orchestrator = AgentOrchestrator(
    rbac=rbac,
    user_id="admin",
    running_agent=running_agent,
    validation_agent=validation_agent,
    quality_agent=quality_agent
)

# Process a query
result = orchestrator.process_query("What is semantic search?")
print(result["response"])
```

## RBAC Roles

The system includes four predefined roles:

- **admin**: Full system access
- **operator**: Can execute and validate operations
- **analyst**: Read-only access for quality monitoring
- **user**: Basic chatbot access

### Managing Users and Roles

```python
from src.rbac import RBACFramework

rbac = RBACFramework()

# Create a user
rbac.create_user("user123", "john_doe", "john@example.com")

# Assign a role
rbac.assign_role("user123", "operator")

# Check permissions
has_permission = rbac.check_permission("user123", Permission.CHATBOT_EXECUTE)
```

## Adding Data to Semantic Store

```python
from src.semantic_store import SemanticStore

store = SemanticStore()

documents = [
    {
        "id": "doc1",
        "content": "Semantic search uses vector embeddings to find similar content.",
        "metadata": {"source": "documentation", "topic": "search"}
    },
    {
        "id": "doc2",
        "content": "Vector databases store embeddings for efficient similarity search.",
        "metadata": {"source": "documentation", "topic": "databases"}
    }
]

store.add_documents(documents)
```

## Configuration

Configuration is managed through environment variables and `config.py`. Key settings:

- `LLM_PROVIDER`: LLM provider to use (default: "ollama")
- `LLM_MODEL`: Model to use (default: "llama2" for Ollama, "gpt-4" for OpenAI)
- `OLLAMA_BASE_URL`: Ollama server URL (default: "http://localhost:11434")
- `OPENAI_API_KEY`: Your OpenAI API key (only needed if using OpenAI)
- `SEMANTIC_STORE_COLLECTION`: Collection name for semantic store
- `RBAC_DB_PATH`: Path to RBAC database
- `QUALITY_DB_PATH`: Path to quality metrics database

### Using Different Models

**Ollama Models:**
```bash
# Pull available models
ollama pull llama2
ollama pull mistral
ollama pull codellama
ollama pull phi

# Use in code
llm_client = LLMClient(provider="ollama", model="mistral")
```

**OpenAI Models:**
```bash
export OPENAI_API_KEY="your-key"
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4"
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Executive Dashboard

The system includes a comprehensive executive dashboard for real-time monitoring:

### Quick Start

```bash
# 1. Generate demo data
python3 demo_dashboard.py

# 2. Start dashboard
streamlit run dashboard.py
```

### Dashboard Features

- **Real-Time Agent Monitoring**: See when agents are called and their execution status
- **RBAC Visualization**: Visual representation of permission checks
- **Performance Metrics**: Success rates, response times, quality scores
- **Interactive Charts**: Explore data with Plotly visualizations
- **User Role Testing**: Switch between users to see RBAC enforcement

### Dashboard Tabs

1. **Overview**: System-wide metrics and KPIs
2. **Agent Activity**: Timeline of agent calls with color coding
3. **RBAC Monitoring**: Permission checks with allow/deny visualization
4. **Analytics**: Advanced performance analysis

See [README_DASHBOARD.md](README_DASHBOARD.md) and [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) for complete dashboard documentation.

## Project Structure

```
semantic-with-chatbot/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── running.py
│   │   ├── validation.py
│   │   └── quality.py
│   ├── rbac/
│   │   ├── __init__.py
│   │   ├── framework.py
│   │   ├── decorators.py
│   │   └── models.py
│   ├── __init__.py
│   ├── api.py
│   ├── orchestrator.py
│   ├── semantic_store.py
│   └── llm_client.py
├── tests/
├── databases/
├── PLAN.md
├── ARCHITECTURE.md
├── requirements.txt
├── config.py
└── README.md
```

## Security Considerations

1. **Authentication**: All API requests require user ID in header
2. **Authorization**: RBAC checks at every agent operation
3. **Audit Logging**: All operations are logged for audit
4. **Input Validation**: All inputs are validated before processing
5. **Error Handling**: Graceful error handling without exposing internals

## Best Practices

This implementation follows these best practices:

1. **Separation of Concerns**: Each agent has a single responsibility
2. **Principle of Least Privilege**: Agents only have necessary permissions
3. **Defense in Depth**: Multiple validation layers
4. **Observability**: Comprehensive logging and monitoring
5. **Error Handling**: Graceful degradation and error recovery
6. **Documentation**: Clear API and code documentation

## License

[Your License Here]

## Contributing

[Contributing Guidelines]

## Troubleshooting

Common issues and solutions:

- **ChromaDB initialization**: First run downloads 79MB embedding model (wait 1-2 minutes)
- **Ollama connection**: Ensure Ollama is running (`ollama serve`)
- **Model not found**: Check available models with `ollama list` and set `LLM_MODEL` environment variable
- **Permission denied**: Use a user with appropriate role (e.g., "admin")
- **Dashboard errors**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions

## Documentation

- [README.md](README.md) - This file (main documentation)
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [README_DASHBOARD.md](README_DASHBOARD.md) - Dashboard quick start
- [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) - Complete dashboard guide
- [OLLAMA_SETUP.md](OLLAMA_SETUP.md) - Ollama setup and configuration
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and diagrams
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Troubleshooting guide
- [PLAN.md](PLAN.md) - Implementation plan

## Support

For issues and questions:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common solutions
- Review dashboard logs: `/tmp/dashboard.log`
- Check system logs for detailed error messages
