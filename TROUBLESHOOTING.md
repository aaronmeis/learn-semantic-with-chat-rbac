# Troubleshooting Guide

## Common Errors and Solutions

### Error: "Model not found" or "Ollama connection error"

**Problem:** The system is looking for a model that doesn't exist.

**Solution:**
1. Check available models:
   ```bash
   ollama list
   ```

2. Set the correct model:
   ```bash
   export LLM_MODEL="llama3.2"  # or whatever model you have
   ```

3. Or update `.env` file:
   ```
   LLM_MODEL=llama3.2
   ```

### Error: "Semantic store is still initializing"

**Problem:** ChromaDB is downloading the embedding model (79MB) on first use.

**Solution:**
- Wait 1-2 minutes for ChromaDB to finish downloading
- Refresh the dashboard page
- The download only happens once

### Error: "Running agent not initialized"

**Problem:** Semantic store failed to initialize.

**Solution:**
1. Check if ChromaDB finished downloading
2. Check disk space (needs ~100MB)
3. Restart the dashboard

### Error: "Permission Denied"

**Problem:** User doesn't have required permissions.

**Solution:**
- Select a user with appropriate role (e.g., "admin")
- Check RBAC tab to see user permissions

### Error: "Connection refused" (Ollama)

**Problem:** Ollama server is not running.

**Solution:**
```bash
# Start Ollama
ollama serve

# Or if using Ollama app, make sure it's running
```

### Dashboard Shows Limited Permissions

**Problem:** Only showing permissions that were checked, not all available.

**Solution:**
- Regenerate demo data: `python3 demo_dashboard.py`
- Execute queries to generate more RBAC checks
- Admin should show all 9 permissions

## Quick Fixes

### Reset Everything
```bash
# Stop dashboard
pkill -f "streamlit run dashboard.py"

# Clear databases
rm -f monitoring.db databases/*.db

# Regenerate demo data
python3 demo_dashboard.py

# Restart dashboard
python3 -m streamlit run dashboard.py
```

### Check System Status
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check dashboard
curl http://localhost:8501/_stcore/health

# Check Python dependencies
python3 -c "import streamlit, chromadb, plotly; print('All OK')"
```

## Getting Help

If you see an error:
1. Check the error message in the dashboard (it now shows detailed info)
2. Look at `/tmp/dashboard.log` for full error details
3. Check this troubleshooting guide
4. Verify all prerequisites are installed
