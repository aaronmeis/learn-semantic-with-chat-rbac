"""
Running Agent - Executes chatbot queries and generates responses
"""

from typing import Dict, Any, List, Optional
import logging

from .base import BaseAgent
from ..rbac.framework import Permission
from ..semantic_store import SemanticStore
from ..llm_client import LLMClient


class RunningAgent(BaseAgent):
    """Agent responsible for executing chatbot queries"""
    
    def __init__(self, agent_id: str, rbac, user_id: str, 
                 semantic_store: SemanticStore, llm_client: LLMClient):
        """
        Initialize Running Agent
        
        Args:
            agent_id: Unique agent identifier
            rbac: RBAC framework instance
            user_id: User ID for permission checking
            semantic_store: Semantic data store instance
            llm_client: LLM client instance
        """
        super().__init__(agent_id, "RunningAgent", rbac, user_id)
        self.semantic_store = semantic_store
        self.llm_client = llm_client
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{agent_id}")
    
    def execute(self, query: str, context_limit: int = 5, **kwargs) -> Dict[str, Any]:
        """
        Execute a chatbot query
        
        Args:
            query: User query string
            context_limit: Number of context documents to retrieve
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with response and metadata
        """
        # Check permissions
        self.require_permission(Permission.CHATBOT_EXECUTE)
        self.require_permission(Permission.DATA_READ)
        
        try:
            self.log_request({"query": query, "context_limit": context_limit})
            
            # Retrieve relevant context from semantic store
            context_docs = self.semantic_store.search(query, limit=context_limit)
            
            # Build context string
            context_text = self._build_context(context_docs)
            
            # Generate response using LLM
            response = self.llm_client.generate(
                query=query,
                context=context_text,
                **kwargs
            )
            
            # Prepare result
            result = {
                "response": response["text"],
                "query": query,
                "context_docs": len(context_docs),
                "metadata": {
                    "model": response.get("model"),
                    "tokens_used": response.get("tokens_used"),
                    "timestamp": response.get("timestamp")
                },
                "agent_id": self.agent_id
            }
            
            self.logger.info(f"Successfully processed query: {query[:50]}...")
            return result
            
        except PermissionError:
            raise
        except Exception as e:
            self.log_error(e, {"query": query})
            raise
    
    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents"""
        if not docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            content = doc.get("content", doc.get("text", ""))
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "Unknown")
            
            context_parts.append(f"[Document {i} - Source: {source}]\n{content}\n")
        
        return "\n".join(context_parts)
    
    def stream_response(self, query: str, context_limit: int = 5, **kwargs):
        """
        Stream response tokens (for real-time responses)
        
        Yields:
            Response tokens as they are generated
        """
        self.require_permission(Permission.CHATBOT_EXECUTE)
        self.require_permission(Permission.DATA_READ)
        
        context_docs = self.semantic_store.search(query, limit=context_limit)
        context_text = self._build_context(context_docs)
        
        for token in self.llm_client.stream(query=query, context=context_text, **kwargs):
            yield token
