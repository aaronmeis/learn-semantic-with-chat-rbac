"""
Agent Orchestrator - Coordinates agent interactions
"""

from typing import Dict, Any, Optional
import logging
import time

from .agents import RunningAgent, ValidationAgent, QualityAgent
from .rbac.framework import RBACFramework
from .monitoring import get_event_tracker


class AgentOrchestrator:
    """Orchestrates multi-agent interactions"""
    
    def __init__(self, rbac: RBACFramework, user_id: str,
                 running_agent: Optional[RunningAgent],
                 validation_agent: Optional[ValidationAgent],
                 quality_agent: QualityAgent):
        """
        Initialize orchestrator
        
        Args:
            rbac: RBAC framework instance
            user_id: User ID for operations
            running_agent: Running agent instance
            validation_agent: Validation agent instance
            quality_agent: Quality agent instance
        """
        self.rbac = rbac
        self.user_id = user_id
        self.running_agent = running_agent
        self.validation_agent = validation_agent
        self.quality_agent = quality_agent
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process_query(self, query: str, validate: bool = True, track_quality: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Process a user query through the agent pipeline
        
        Args:
            query: User query string
            validate: Whether to validate the response
            track_quality: Whether to track quality metrics
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()
        
        try:
            tracker = get_event_tracker()
        except Exception:
            tracker = None
        
        try:
            # Step 1: Generate response using Running Agent
            if self.running_agent is None:
                raise RuntimeError("Running agent not initialized. Semantic store may still be loading.")
            
            self.logger.info(f"Processing query: {query[:50]}...")
            agent_start = time.time()
            try:
                response_result = self.running_agent.execute(query=query, **kwargs)
                response_text = response_result["response"]
                agent_duration = (time.time() - agent_start) * 1000
                if tracker:
                    try:
                        tracker.track_agent_call(
                            agent_id=self.running_agent.agent_id,
                            agent_name=self.running_agent.name,
                            user_id=self.user_id,
                            action="execute",
                            status="success",
                            duration_ms=agent_duration,
                            metadata={"query_length": len(query)}
                        )
                    except Exception:
                        pass
            except Exception as e:
                agent_duration = (time.time() - agent_start) * 1000
                if tracker:
                    tracker.track_agent_call(
                        agent_id=self.running_agent.agent_id,
                        agent_name=self.running_agent.name,
                        user_id=self.user_id,
                        action="execute",
                        status="error",
                        duration_ms=agent_duration,
                        metadata={"error": str(e)}
                    )
                raise
            
            # Step 2: Validate response (if enabled)
            validation_result = None
            if validate and self.validation_agent is not None:
                agent_start = time.time()
                try:
                    validation_result = self.validation_agent.execute(
                        response=response_text,
                        query=query
                    )
                    agent_duration = (time.time() - agent_start) * 1000
                    if tracker:
                        try:
                            tracker.track_agent_call(
                                agent_id=self.validation_agent.agent_id,
                                agent_name=self.validation_agent.name,
                                user_id=self.user_id,
                                action="validate",
                                status="success",
                                duration_ms=agent_duration,
                                metadata={"is_valid": validation_result.get("is_valid", False)}
                            )
                        except Exception:
                            pass
                    
                    # If validation fails, we might want to retry or flag
                    if not validation_result.get("is_valid", True):
                        self.logger.warning(f"Validation failed: {validation_result.get('errors', [])}")
                except Exception as e:
                    agent_duration = (time.time() - agent_start) * 1000
                    if tracker:
                        tracker.track_agent_call(
                            agent_id=self.validation_agent.agent_id,
                            agent_name=self.validation_agent.name,
                            user_id=self.user_id,
                            action="validate",
                            status="error",
                            duration_ms=agent_duration,
                            metadata={"error": str(e)}
                        )
                    raise
            
            # Step 3: Track quality metrics (if enabled)
            quality_result = None
            if track_quality:
                response_time = time.time() - start_time
                quality_data = {
                    "query": query,
                    "response": response_text,
                    "response_time": response_time,
                    "validation_score": validation_result.get("score", 1.0) if validation_result else 1.0,
                    "agent_id": self.running_agent.agent_id
                }
                agent_start = time.time()
                try:
                    quality_result = self.quality_agent.execute(quality_data)
                    agent_duration = (time.time() - agent_start) * 1000
                    if tracker:
                        try:
                            tracker.track_agent_call(
                                agent_id=self.quality_agent.agent_id,
                                agent_name=self.quality_agent.name,
                                user_id=self.user_id,
                                action="track_quality",
                                status="success",
                                duration_ms=agent_duration
                            )
                        except Exception:
                            pass
                except Exception as e:
                    agent_duration = (time.time() - agent_start) * 1000
                    if tracker:
                        tracker.track_agent_call(
                            agent_id=self.quality_agent.agent_id,
                            agent_name=self.quality_agent.name,
                            user_id=self.user_id,
                            action="track_quality",
                            status="error",
                            duration_ms=agent_duration,
                            metadata={"error": str(e)}
                        )
                    raise
            
            # Compile final result
            result = {
                "response": response_text,
                "query": query,
                "metadata": {
                    **response_result.get("metadata", {}),
                    "response_time": time.time() - start_time,
                    "validated": validate,
                    "quality_tracked": track_quality
                },
                "validation": validation_result,
                "quality": quality_result
            }
            
            self.logger.info(f"Query processed successfully in {time.time() - start_time:.2f}s")
            return result
            
        except PermissionError as e:
            self.logger.error(f"Permission denied: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error processing query: {e}", exc_info=True)
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "running_agent": self.running_agent.get_stats(),
            "validation_agent": self.validation_agent.get_stats(),
            "quality_agent": self.quality_agent.get_stats(),
            "user_id": self.user_id
        }
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Get quality report from Quality Agent"""
        return self.quality_agent.get_quality_report()
