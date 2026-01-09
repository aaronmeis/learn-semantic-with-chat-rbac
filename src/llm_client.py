"""
LLM Client - Interface for Language Model APIs
"""

from typing import Dict, Any, Optional, Iterator
import logging
import os
import time
import requests
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available. Install with: pip install openai")


class LLMClient:
    """Client for interacting with LLM APIs"""
    
    def __init__(self, provider: str = "ollama", model: str = "llama2", 
                 api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize LLM client
        
        Args:
            provider: LLM provider ("ollama", "openai", or "anthropic")
            model: Model name
            api_key: API key (for OpenAI/Anthropic, not needed for Ollama)
            base_url: Base URL for API (defaults to http://localhost:11434 for Ollama)
        """
        self.provider = provider.lower()
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if self.provider == "ollama":
            self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.api_key = None  # Ollama doesn't require API key
            self.logger.info(f"Using Ollama at {self.base_url} with model {model}")
            
        elif self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI library required. Install with: pip install openai")
            
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key required")
            
            openai.api_key = self.api_key
            self.client = openai
            self.base_url = None
        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported: ollama, openai")
    
    def generate(self, query: str, context: str = "", **kwargs) -> Dict[str, Any]:
        """
        Generate a response
        
        Args:
            query: User query
            context: Context information
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()
        
        # Build prompt
        system_prompt = kwargs.get("system_prompt", "You are a helpful assistant.")
        user_prompt = self._build_prompt(query, context)
        
        try:
            if self.provider == "ollama":
                # Ollama API format
                full_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
                
                payload = {
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "num_predict": kwargs.get("max_tokens", 1000)
                    }
                }
                
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=kwargs.get("timeout", 300)
                )
                response.raise_for_status()
                
                result = response.json()
                response_text = result.get("response", "")
                tokens_used = result.get("eval_count", 0)  # Tokens generated
                
                return {
                    "text": response_text,
                    "model": self.model,
                    "tokens_used": tokens_used,
                    "timestamp": time.time(),
                    "response_time": time.time() - start_time
                }
                
            elif self.provider == "openai":
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", 1000)
                )
                
                response_text = response.choices[0].message.content
                tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
                
                return {
                    "text": response_text,
                    "model": self.model,
                    "tokens_used": tokens_used,
                    "timestamp": time.time(),
                    "response_time": time.time() - start_time
                }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error connecting to Ollama: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise
    
    def stream(self, query: str, context: str = "", **kwargs) -> Iterator[str]:
        """
        Stream response tokens
        
        Args:
            query: User query
            context: Context information
            **kwargs: Additional parameters
            
        Yields:
            Response tokens
        """
        system_prompt = kwargs.get("system_prompt", "You are a helpful assistant.")
        user_prompt = self._build_prompt(query, context)
        
        try:
            if self.provider == "ollama":
                full_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
                
                payload = {
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": True,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "num_predict": kwargs.get("max_tokens", 1000)
                    }
                }
                
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    stream=True,
                    timeout=kwargs.get("timeout", 300)
                )
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                yield chunk["response"]
                        except json.JSONDecodeError:
                            continue
                            
            elif self.provider == "openai":
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", 1000),
                    stream=True
                )
                
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error connecting to Ollama: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error streaming response: {e}")
            raise
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build prompt with context"""
        if context:
            return f"""Context Information:
{context}

User Query: {query}

Please provide a helpful response based on the context information above."""
        else:
            return query
