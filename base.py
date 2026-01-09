"""
Base Agent Class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..rbac.framework import Permission, RBACFramework
from ..monitoring import get_event_tracker


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_id: str, name: str, rbac: RBACFramework, user_id: str):
        """
        Initialize base agent
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name
            rbac: RBAC framework instance
            user_id: User ID for permission checking
        """
        self.agent_id = agent_id
        self.name = name
        self.rbac = rbac
        self.user_id = user_id
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{agent_id}")
        self.created_at = datetime.now()
        self.stats = {
            "requests_processed": 0,
            "errors": 0,
            "last_request": None
        }
    
    def check_permission(self, permission: Permission) -> bool:
        """Check if agent has required permission"""
        result = self.rbac.check_permission(self.user_id, permission)
        # Track RBAC check
        try:
            tracker = get_event_tracker()
            tracker.track_rbac_check(
                user_id=self.user_id,
                agent_id=self.agent_id,
                permission=permission.value,
                result=result,
                context=f"Agent: {self.name}"
            )
        except Exception:
            pass  # Don't fail if monitoring not available
        return result
    
    def require_permission(self, permission: Permission):
        """Require permission or raise exception"""
        if not self.check_permission(permission):
            raise PermissionError(
                f"Agent {self.name} (user {self.user_id}) does not have permission {permission.value}"
            )
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute agent's main function
        
        Returns:
            Dictionary with execution results
        """
        pass
    
    def log_request(self, request_data: Dict[str, Any]):
        """Log a request"""
        self.stats["requests_processed"] += 1
        self.stats["last_request"] = datetime.now()
        self.logger.info(f"Request processed: {request_data}")
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log an error"""
        self.stats["errors"] += 1
        self.logger.error(f"Error in {self.name}: {error}", exc_info=True, extra=context)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            **self.stats,
            "agent_id": self.agent_id,
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }
