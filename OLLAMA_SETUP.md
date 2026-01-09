# Ollama Setup Guide

This guide explains how to set up and use Ollama with the Semantic Data Chatbot.

## What is Ollama?

Ollama is a tool that allows you to run large language models locally on your machine. It's free, open-source, and doesn't require API keys.

## Installation

### macOS
```bash
brew install ollama
# Or download from https://ollama.ai/download
```

### Linux
```bash
curl https://ollama.ai/install.sh | sh
```

### Windows
Download the installer from https://ollama.ai/download

## Starting Ollama

Ollama typically runs automatically after installation. To start it manually:

```bash
ollama serve
```

The server will run on `http://localhost:11434` by default.

## Pulling Models

Before using a model, you need to pull it:

```bash
# Popular models
ollama pull llama2          # Meta's Llama 2 (7B parameters)
ollama pull mistral         # Mistral AI model
ollama pull codellama       # Code-focused Llama
ollama pull phi             # Microsoft's Phi model (smaller, faster)
ollama pull llama2:13b      # Larger Llama 2 (13B parameters)
ollama pull llama2:70b      # Largest Llama 2 (70B parameters, requires more RAM)
```

### Recommended Models

- **For general use**: `llama2` or `mistral`
- **For code**: `codellama`
- **For low-resource systems**: `phi` or `llama2:7b`
- **For best quality**: `llama2:13b` or `llama2:70b`

## Testing Ollama

Test that Ollama is working:

```bash
curl http://localhost:11434/api/tags
```

You should see a list of available models.

Test a model:

```bash
ollama run llama2 "What is semantic search?"
```

## Configuration

The chatbot is configured to use Ollama by default. You can customize settings:

### Environment Variables

```bash
# Use Ollama (default)
export LLM_PROVIDER="ollama"
export LLM_MODEL="llama2"
export OLLAMA_BASE_URL="http://localhost:11434"

# Or use a different model
export LLM_MODEL="mistral"
```

### In Code

```python
from src.llm_client import LLMClient

# Use default Ollama settings
llm_client = LLMClient(provider="ollama", model="llama2")

# Use custom Ollama URL
llm_client = LLMClient(
    provider="ollama", 
    model="mistral",
    base_url="http://localhost:11434"
)
```

## Switching Between Ollama and OpenAI

### Using Ollama (Default)
```bash
export LLM_PROVIDER="ollama"
export LLM_MODEL="llama2"
```

### Using OpenAI
```bash
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4"
export OPENAI_API_KEY="your-api-key"
```

## Performance Tips

1. **Model Size**: Smaller models (phi, llama2:7b) are faster but less capable
2. **RAM**: Ensure you have enough RAM for the model:
   - 7B models: ~8GB RAM
   - 13B models: ~16GB RAM
   - 70B models: ~64GB RAM
3. **GPU**: Ollama can use GPU if available (CUDA/Metal)
4. **Batch Processing**: Process multiple queries together for better throughput

## Troubleshooting

### Ollama not starting
```bash
# Check if port is already in use
lsof -i :11434

# Kill existing process if needed
killall ollama

# Restart
ollama serve
```

### Model not found
```bash
# List available models
ollama list

# Pull the model
ollama pull llama2
```

### Connection refused
- Make sure Ollama is running: `ollama serve`
- Check firewall settings
- Verify URL: `curl http://localhost:11434/api/tags`

### Out of memory
- Use a smaller model (phi, llama2:7b)
- Close other applications
- Reduce batch size

## Model Comparison

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| phi | 2.7B | Very Fast | Good | Quick responses, low resources |
| llama2:7b | 7B | Fast | Very Good | General purpose, balanced |
| mistral | 7B | Fast | Excellent | Best quality for size |
| llama2:13b | 13B | Medium | Excellent | Higher quality needs |
| codellama | 7B-34B | Medium | Excellent | Code generation |

## Advanced Usage

### Custom Ollama Server

If running Ollama on a different machine:

```bash
export OLLAMA_BASE_URL="http://your-server:11434"
```

### Multiple Models

You can switch models at runtime:

```python
# Use different models for different tasks
code_client = LLMClient(provider="ollama", model="codellama")
general_client = LLMClient(provider="ollama", model="llama2")
```

## Resources

- Ollama Website: https://ollama.ai
- Ollama GitHub: https://github.com/ollama/ollama
- Model Library: https://ollama.ai/library
- Documentation: https://github.com/ollama/ollama/blob/main/docs/api.md
