"""
Quality Agent - Monitors and improves system quality
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import sqlite3

from .base import BaseAgent
from ..rbac.framework import Permission


class QualityAgent(BaseAgent):
    """Agent responsible for monitoring and analyzing system quality"""
    
    def __init__(self, agent_id: str, rbac, user_id: str, metrics_db_path: str = "quality_metrics.db"):
        """
        Initialize Quality Agent
        
        Args:
            agent_id: Unique agent identifier
            rbac: RBAC framework instance
            user_id: User ID for permission checking
            metrics_db_path: Path to metrics database
        """
        super().__init__(agent_id, "QualityAgent", rbac, user_id)
        self.metrics_db_path = metrics_db_path
        self._init_metrics_db()
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{agent_id}")
    
    def _init_metrics_db(self):
        """Initialize metrics database"""
        conn = sqlite3.connect(self.metrics_db_path)
        cursor = conn.cursor()
        
        # Interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                response TEXT,
                response_time REAL,
                validation_score REAL,
                user_satisfaction REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                agent_id TEXT
            )
        """)
        
        # Quality metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def execute(self, interaction_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Record and analyze interaction quality
        
        Args:
            interaction_data: Dictionary with interaction data
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with quality analysis results
        """
        # Check permissions
        self.require_permission(Permission.QUALITY_MONITOR)
        self.require_permission(Permission.DATA_WRITE)
        
        try:
            self.log_request(interaction_data)
            
            # Store interaction
            interaction_id = self._store_interaction(interaction_data)
            
            # Calculate quality metrics
            metrics = self._calculate_metrics(interaction_data)
            
            # Store metrics
            self._store_metrics(metrics)
            
            result = {
                "interaction_id": interaction_id,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat(),
                "agent_id": self.agent_id
            }
            
            self.logger.info(f"Quality metrics recorded: {metrics}")
            return result
            
        except PermissionError:
            raise
        except Exception as e:
            self.log_error(e, interaction_data)
            raise
    
    def analyze_quality(self, time_period_hours: int = 24, **kwargs) -> Dict[str, Any]:
        """
        Analyze quality metrics over a time period
        
        Args:
            time_period_hours: Number of hours to analyze
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with quality analysis
        """
        # Check permissions
        self.require_permission(Permission.QUALITY_ANALYZE)
        self.require_permission(Permission.DATA_READ)
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=time_period_hours)
            
            conn = sqlite3.connect(self.metrics_db_path)
            cursor = conn.cursor()
            
            # Get interactions in time period
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_interactions,
                    AVG(response_time) as avg_response_time,
                    AVG(validation_score) as avg_validation_score,
                    AVG(user_satisfaction) as avg_satisfaction
                FROM interactions
                WHERE timestamp >= ?
            """, (cutoff_time.isoformat(),))
            
            row = cursor.fetchone()
            conn.close()
            
            analysis = {
                "time_period_hours": time_period_hours,
                "total_interactions": row[0] or 0,
                "average_response_time": row[1] or 0.0,
                "average_validation_score": row[2] or 0.0,
                "average_satisfaction": row[3] or 0.0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Calculate quality score
            analysis["quality_score"] = self._calculate_quality_score(analysis)
            
            self.logger.info(f"Quality analysis completed: {analysis}")
            return analysis
            
        except PermissionError:
            raise
        except Exception as e:
            self.log_error(e)
            raise
    
    def get_quality_report(self, **kwargs) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        self.require_permission(Permission.QUALITY_ANALYZE)
        self.require_permission(Permission.DATA_READ)
        
        # Analyze different time periods
        reports = {
            "last_hour": self.analyze_quality(1),
            "last_24_hours": self.analyze_quality(24),
            "last_7_days": self.analyze_quality(168),
        }
        
        return {
            "reports": reports,
            "generated_at": datetime.now().isoformat(),
            "agent_id": self.agent_id
        }
    
    def _store_interaction(self, data: Dict[str, Any]) -> int:
        """Store interaction in database"""
        conn = sqlite3.connect(self.metrics_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interactions 
            (query, response, response_time, validation_score, user_satisfaction, agent_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get("query", ""),
            data.get("response", ""),
            data.get("response_time", 0.0),
            data.get("validation_score", 0.0),
            data.get("user_satisfaction"),
            data.get("agent_id", self.agent_id)
        ))
        
        interaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return interaction_id
    
    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics from interaction data"""
        metrics = {}
        
        # Response time metric (lower is better, normalized)
        response_time = data.get("response_time", 0.0)
        metrics["response_time_score"] = max(0.0, 1.0 - (response_time / 10.0))  # Normalize to 0-1
        
        # Validation score (already normalized)
        validation_score = data.get("validation_score", 0.0)
        metrics["validation_score"] = validation_score
        
        # User satisfaction (if provided)
        satisfaction = data.get("user_satisfaction")
        if satisfaction is not None:
            metrics["satisfaction_score"] = satisfaction / 5.0 if satisfaction <= 5 else 1.0
        
        # Overall quality score
        scores = [v for v in metrics.values() if isinstance(v, float)]
        metrics["overall_quality"] = sum(scores) / len(scores) if scores else 0.0
        
        return metrics
    
    def _store_metrics(self, metrics: Dict[str, float]):
        """Store calculated metrics"""
        conn = sqlite3.connect(self.metrics_db_path)
        cursor = conn.cursor()
        
        for metric_name, metric_value in metrics.items():
            cursor.execute("""
                INSERT INTO quality_metrics (metric_name, metric_value)
                VALUES (?, ?)
            """, (metric_name, metric_value))
        
        conn.commit()
        conn.close()
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall quality score from analysis"""
        # Weighted combination of metrics
        weights = {
            "avg_validation_score": 0.4,
            "avg_satisfaction": 0.4,
            "avg_response_time": 0.2  # Inverted - faster is better
        }
        
        score = 0.0
        total_weight = 0.0
        
        if analysis.get("average_validation_score"):
            score += analysis["average_validation_score"] * weights["avg_validation_score"]
            total_weight += weights["avg_validation_score"]
        
        if analysis.get("average_satisfaction"):
            score += (analysis["average_satisfaction"] / 5.0) * weights["avg_satisfaction"]
            total_weight += weights["avg_satisfaction"]
        
        if analysis.get("average_response_time"):
            # Invert response time (faster = better)
            rt_score = max(0.0, 1.0 - (analysis["average_response_time"] / 10.0))
            score += rt_score * weights["avg_response_time"]
            total_weight += weights["avg_response_time"]
        
        return score / total_weight if total_weight > 0 else 0.0
