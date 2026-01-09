"""
Semantic Data Store - Vector database for embeddings
"""

from typing import List, Dict, Any, Optional
import logging
import json
from pathlib import Path

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Install with: pip install chromadb")


class SemanticStore:
    """Semantic data store using vector embeddings"""
    
    def __init__(self, collection_name: str = "semantic_data", persist_directory: str = "./chroma_db"):
        """
        Initialize semantic store
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist data
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is required. Install with: pip install chromadb")
        
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize ChromaDB client (new API)
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception:
            self.collection = self.client.create_collection(name=collection_name)
            self.logger.info(f"Created new collection: {collection_name}")
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: Optional[List[List[float]]] = None):
        """
        Add documents to the store
        
        Args:
            documents: List of documents with 'content' and 'metadata' keys
            embeddings: Optional pre-computed embeddings
        """
        ids = []
        contents = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            doc_id = doc.get("id", f"doc_{i}")
            content = doc.get("content", doc.get("text", ""))
            metadata = doc.get("metadata", {})
            
            ids.append(doc_id)
            contents.append(content)
            metadatas.append(metadata)
        
        self.collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        self.logger.info(f"Added {len(documents)} documents to collection")
    
    def search(self, query: str, limit: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query string
            limit: Maximum number of results
            filter_metadata: Optional metadata filters
            
        Returns:
            List of similar documents with scores
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0.0
                })
        
        return formatted_results
    
    def delete(self, ids: List[str]):
        """Delete documents by IDs"""
        self.collection.delete(ids=ids)
        self.logger.info(f"Deleted {len(ids)} documents")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": self.persist_directory
        }
