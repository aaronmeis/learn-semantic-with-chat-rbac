# Quick Start Guide

Get up and running with the Semantic Data Chatbot in 5 minutes!

## Prerequisites

- Python 3.10+
- Ollama installed and running (default) OR OpenAI API key
- ~100MB disk space for ChromaDB embedding model (downloads automatically)

## Installation

```bash
# 1. Install Ollama (if not already installed)
# Visit https://ollama.ai or use:
# curl https://ollama.ai/install.sh | sh

# 2. Pull a model
ollama pull llama2

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Initialize system
python -m src.setup
```

## Start the System

### Option 1: Executive Dashboard (Recommended)

```bash
# Generate demo data
python3 demo_dashboard.py

# Start dashboard
streamlit run dashboard.py
```

Dashboard opens at `http://localhost:8501`

### Option 2: API Server

```bash
python3 -m src.api
```

The API will be available at `http://localhost:8000`

## Test the API

```bash
# Process a query
curl -X POST "http://localhost:8000/query" \
  -H "X-User-Id: admin" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is semantic search?",
    "validate": true,
    "track_quality": true
  }'

# Check status
curl -X GET "http://localhost:8000/status" \
  -H "X-User-Id: admin"

# Get quality report
curl -X GET "http://localhost:8000/quality" \
  -H "X-User-Id: admin"
```

## Add Sample Data

```python
from src.semantic_store import SemanticStore

store = SemanticStore()

documents = [
    {
        "id": "doc1",
        "content": "Semantic search uses vector embeddings to find similar content.",
        "metadata": {"source": "docs", "topic": "search"}
    },
    {
        "id": "doc2",
        "content": "Vector databases enable efficient similarity search.",
        "metadata": {"source": "docs", "topic": "databases"}
    }
]

store.add_documents(documents)
```

## Default Users

After running `python -m src.setup`, these users are available:

- **admin** (admin role) - Full access
- **operator1** (operator role) - Execute and validate
- **analyst1** (analyst role) - Quality monitoring
- **user1** (user role) - Basic access

## Next Steps

- **Try the Dashboard**: `streamlit run dashboard.py` - See agents and RBAC in action!
- Read [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [example_usage.py](example_usage.py) for code examples
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Check [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) for dashboard features

## Troubleshooting

**Issue**: `Connection refused` or `Ollama not available`
- Solution: Make sure Ollama is running: `ollama serve` (usually runs automatically)
- Check if Ollama is accessible: `curl http://localhost:11434/api/tags`

**Issue**: `Model not found`
- Solution: Pull the model first: `ollama pull llama2` (or your chosen model)

**Issue**: `Permission denied`
- Solution: Use a user with appropriate role (e.g., "admin")

**Issue**: `ChromaDB not available`
- Solution: Install ChromaDB: `pip install chromadb`

**Issue**: Want to use OpenAI instead
- Solution: Set environment variables:
  ```bash
  export LLM_PROVIDER="openai"
  export LLM_MODEL="gpt-4"
  export OPENAI_API_KEY="your-key"
  ```

## Support

For more information, see the full [README.md](README.md).
