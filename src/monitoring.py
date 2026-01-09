"""
Monitoring and Event Tracking for Agent Calls and RBAC
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import deque
import json
import threading
import sqlite3
from pathlib import Path


class EventTracker:
    """Tracks agent calls and RBAC events for visualization"""
    
    def __init__(self, db_path: str = "monitoring.db"):
        """Initialize event tracker"""
        self.db_path = db_path
        self._init_database()
        self.events = deque(maxlen=1000)  # Keep last 1000 events in memory
        self.lock = threading.Lock()
    
    def _init_database(self):
        """Initialize monitoring database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agent call events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                agent_id TEXT,
                agent_name TEXT,
                user_id TEXT,
                action TEXT,
                status TEXT,
                duration_ms REAL,
                metadata TEXT
            )
        """)
        
        # RBAC check events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rbac_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                agent_id TEXT,
                permission TEXT,
                result TEXT,
                context TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def track_agent_call(self, agent_id: str, agent_name: str, user_id: str, 
                         action: str, status: str, duration_ms: float = 0,
                         metadata: Optional[Dict[str, Any]] = None):
        """Track an agent call"""
        event = {
            "type": "agent_call",
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "agent_name": agent_name,
            "user_id": user_id,
            "action": action,
            "status": status,
            "duration_ms": duration_ms,
            "metadata": metadata or {}
        }
        
        with self.lock:
            self.events.append(event)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_calls 
            (agent_id, agent_name, user_id, action, status, duration_ms, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            agent_id, agent_name, user_id, action, status, duration_ms,
            json.dumps(metadata or {})
        ))
        conn.commit()
        conn.close()
    
    def track_rbac_check(self, user_id: str, agent_id: str, permission: str,
                        result: bool, context: Optional[str] = None):
        """Track an RBAC permission check"""
        event = {
            "type": "rbac_check",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "agent_id": agent_id,
            "permission": permission,
            "result": "allowed" if result else "denied",
            "context": context or ""
        }
        
        with self.lock:
            self.events.append(event)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rbac_checks 
            (user_id, agent_id, permission, result, context)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, agent_id, permission, "allowed" if result else "denied", context or ""))
        conn.commit()
        conn.close()
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events"""
        with self.lock:
            return list(self.events)[-limit:]
    
    def get_agent_stats(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get agent statistics for time window"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = datetime.now().timestamp() - (time_window_minutes * 60)
        
        # Agent call stats
        cursor.execute("""
            SELECT 
                agent_name,
                COUNT(*) as total_calls,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count,
                AVG(duration_ms) as avg_duration
            FROM agent_calls
            WHERE timestamp >= datetime(?, 'unixepoch')
            GROUP BY agent_name
        """, (cutoff,))
        
        agent_stats = {}
        for row in cursor.fetchall():
            agent_stats[row[0]] = {
                "total_calls": row[1],
                "success_count": row[2],
                "error_count": row[3],
                "avg_duration_ms": row[4] or 0
            }
        
        # RBAC check stats
        cursor.execute("""
            SELECT 
                permission,
                COUNT(*) as total_checks,
                SUM(CASE WHEN result = 'allowed' THEN 1 ELSE 0 END) as allowed_count,
                SUM(CASE WHEN result = 'denied' THEN 1 ELSE 0 END) as denied_count
            FROM rbac_checks
            WHERE timestamp >= datetime(?, 'unixepoch')
            GROUP BY permission
        """, (cutoff,))
        
        rbac_stats = {}
        for row in cursor.fetchall():
            rbac_stats[row[0]] = {
                "total_checks": row[1],
                "allowed_count": row[2],
                "denied_count": row[3]
            }
        
        conn.close()
        
        return {
            "agents": agent_stats,
            "rbac": rbac_stats,
            "time_window_minutes": time_window_minutes
        }
    
    def get_recent_agent_calls(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent agent calls"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM agent_calls
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_recent_rbac_checks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent RBAC checks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM rbac_checks
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]


# Global event tracker instance
_event_tracker: Optional[EventTracker] = None


def get_event_tracker() -> EventTracker:
    """Get global event tracker instance"""
    global _event_tracker
    if _event_tracker is None:
        _event_tracker = EventTracker()
    return _event_tracker


def set_event_tracker(tracker: EventTracker):
    """Set global event tracker"""
    global _event_tracker
    _event_tracker = tracker
