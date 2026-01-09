"""
Example usage of the Semantic Data Chatbot
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rbac import RBACFramework
from src.rbac.framework import Permission
from src.agents import RunningAgent, ValidationAgent, QualityAgent
from src.orchestrator import AgentOrchestrator
from src.semantic_store import SemanticStore
from src.llm_client import LLMClient


def example_basic_usage():
    """Basic usage example"""
    print("=== Basic Usage Example ===\n")
    
    # Initialize RBAC
    print("1. Initializing RBAC framework...")
    rbac = RBACFramework(db_path="databases/rbac.db")
    
    # Create a user and assign role
    user_id = "example_user"
    try:
        rbac.create_user(user_id, "example_user", "user@example.com")
        rbac.assign_role(user_id, "operator")
        print(f"   Created user: {user_id} with operator role")
    except Exception as e:
        print(f"   User might already exist: {e}")
    
    # Check permissions
    print("\n2. Checking permissions...")
    has_execute = rbac.check_permission(user_id, Permission.CHATBOT_EXECUTE)
    has_validate = rbac.check_permission(user_id, Permission.VALIDATION_EXECUTE)
    print(f"   Can execute: {has_execute}")
    print(f"   Can validate: {has_validate}")
    
    # Initialize semantic store
    print("\n3. Initializing semantic store...")
    try:
        store = SemanticStore(collection_name="semantic_data", persist_directory="databases/chroma_db")
        
        # Add sample documents
        documents = [
            {
                "id": "doc1",
                "content": "Semantic search uses vector embeddings to find similar content based on meaning rather than keywords.",
                "metadata": {"source": "documentation", "topic": "search"}
            },
            {
                "id": "doc2",
                "content": "Vector databases store embeddings in a way that enables efficient similarity search using distance metrics.",
                "metadata": {"source": "documentation", "topic": "databases"}
            },
            {
                "id": "doc3",
                "content": "RBAC (Role-Based Access Control) is a security model that restricts access based on user roles.",
                "metadata": {"source": "documentation", "topic": "security"}
            }
        ]
        store.add_documents(documents)
        print(f"   Added {len(documents)} documents to semantic store")
    except Exception as e:
        print(f"   Error initializing semantic store: {e}")
        return
    
    # Initialize LLM client (using Ollama by default)
    print("\n4. Initializing LLM client...")
    llm_provider = os.getenv("LLM_PROVIDER", "ollama")
    llm_model = os.getenv("LLM_MODEL", "llama2")
    
    try:
        if llm_provider == "ollama":
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            llm_client = LLMClient(provider="ollama", model=llm_model, base_url=ollama_url)
            print(f"   LLM client initialized (Ollama: {llm_model} at {ollama_url})")
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("   Warning: OPENAI_API_KEY not set. LLM operations will fail.")
                print("   Set it with: export OPENAI_API_KEY='your-key'")
                return
            llm_client = LLMClient(provider=llm_provider, model=llm_model, api_key=api_key)
            print(f"   LLM client initialized ({llm_provider}: {llm_model})")
    except Exception as e:
        print(f"   Error initializing LLM client: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return
    
    # Create agents
    print("\n5. Creating agents...")
    running_agent = RunningAgent(
        agent_id="running_001",
        rbac=rbac,
        user_id=user_id,
        semantic_store=store,
        llm_client=llm_client
    )
    print("   Running agent created")
    
    validation_agent = ValidationAgent(
        agent_id="validation_001",
        rbac=rbac,
        user_id=user_id,
        semantic_store=store
    )
    print("   Validation agent created")
    
    quality_agent = QualityAgent(
        agent_id="quality_001",
        rbac=rbac,
        user_id=user_id
    )
    print("   Quality agent created")
    
    # Create orchestrator
    print("\n6. Creating orchestrator...")
    orchestrator = AgentOrchestrator(
        rbac=rbac,
        user_id=user_id,
        running_agent=running_agent,
        validation_agent=validation_agent,
        quality_agent=quality_agent
    )
    print("   Orchestrator created")
    
    # Process a query
    print("\n7. Processing query...")
    query = "What is semantic search?"
    print(f"   Query: {query}")
    
    try:
        result = orchestrator.process_query(
            query=query,
            validate=True,
            track_quality=True
        )
        
        print(f"\n   Response: {result['response']}")
        print(f"\n   Validation Score: {result.get('validation', {}).get('score', 'N/A')}")
        print(f"   Response Time: {result['metadata'].get('response_time', 'N/A'):.2f}s")
        
    except Exception as e:
        print(f"   Error processing query: {e}")
    
    # Get quality report
    print("\n8. Getting quality report...")
    try:
        report = orchestrator.get_quality_report()
        print(f"   Quality report generated")
        print(f"   Last 24 hours interactions: {report.get('reports', {}).get('last_24_hours', {}).get('total_interactions', 0)}")
    except Exception as e:
        print(f"   Error getting quality report: {e}")


def example_rbac_usage():
    """RBAC usage example"""
    print("\n=== RBAC Usage Example ===\n")
    
    rbac = RBACFramework(db_path="databases/rbac.db")
    
    # Create users with different roles
    users = [
        ("admin_user", "admin"),
        ("operator_user", "operator"),
        ("analyst_user", "analyst"),
        ("regular_user", "user"),
    ]
    
    print("Creating users with different roles...")
    for user_id, role in users:
        try:
            rbac.create_user(user_id, user_id, f"{user_id}@example.com")
            rbac.assign_role(user_id, role)
            print(f"   Created {user_id} with role: {role}")
        except Exception:
            pass
    
    # Check permissions for each user
    print("\nChecking permissions for each user...")
    permissions_to_check = [
        Permission.CHATBOT_EXECUTE,
        Permission.VALIDATION_EXECUTE,
        Permission.QUALITY_MONITOR,
        Permission.DATA_WRITE,
    ]
    
    for user_id, _ in users:
        print(f"\n{user_id}:")
        user_permissions = rbac.get_user_permissions(user_id)
        for perm in permissions_to_check:
            has_perm = perm in user_permissions or Permission.ADMIN_ALL in user_permissions
            print(f"   {perm.value}: {has_perm}")


if __name__ == "__main__":
    print("Semantic Data Chatbot - Example Usage\n")
    print("=" * 50)
    
    # Run examples
    example_rbac_usage()
    example_basic_usage()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
