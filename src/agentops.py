"""
AgentOps - Monitoring for AI Agents
Core SDK for tracking agent behavior in production
"""

import time
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps
import asyncio


@dataclass
class AgentEvent:
    """Represents a single agent action/monitoring event"""
    timestamp: str
    action_type: str
    latency_ms: float
    token_usage: Dict[str, int]
    model: str
    success: bool
    error_message: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AgentMonitor:
    """Main monitoring class for tracking agent behavior"""
    
    def __init__(self, api_key: Optional[str] = None, project_name: str = "default"):
        self.api_key = api_key
        self.project_name = project_name
        self.session_id = self._generate_session_id()
        self.events: list = []
        self.baseline_stats: Dict[str, Any] = {}
        self.drift_threshold = 0.2  # 20% change triggers alert
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def record_event(self, event: AgentEvent):
        """Record a monitoring event"""
        event.session_id = self.session_id
        self.events.append(event)
        
        # Check for drift if we have baseline
        if self.baseline_stats:
            self._check_drift(event)
    
    def _check_drift(self, event: AgentEvent):
        """Check if agent behavior has drifted from baseline"""
        baseline_latency = self.baseline_stats.get('avg_latency', 0)
        if baseline_latency > 0:
            latency_change = abs(event.latency_ms - baseline_latency) / baseline_latency
            if latency_change > self.drift_threshold:
                print(f"⚠️  DRIFT ALERT: Latency changed by {latency_change:.1%}")
                print(f"   Baseline: {baseline_latency:.0f}ms | Current: {event.latency_ms:.0f}ms")
    
    def record_action(self, action_type: str = "agent_action"):
        """Decorator to automatically monitor agent actions"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error_msg = None
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error_msg = str(e)
                    raise
                finally:
                    latency = (time.time() - start_time) * 1000
                    
                    # Extract token usage if available in result
                    token_usage = {"prompt": 0, "completion": 0, "total": 0}
                    
                    event = AgentEvent(
                        timestamp=datetime.now().isoformat(),
                        action_type=action_type,
                        latency_ms=latency,
                        token_usage=token_usage,
                        model="unknown",  # Override in specific implementations
                        success=success,
                        error_message=error_msg,
                        metadata={"args": str(args), "kwargs": str(kwargs)}
                    )
                    
                    self.record_event(event)
                    
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        if not self.events:
            return {"message": "No events recorded yet"}
        
        total_events = len(self.events)
        success_count = sum(1 for e in self.events if e.success)
        avg_latency = sum(e.latency_ms for e in self.events) / total_events
        
        return {
            "total_events": total_events,
            "success_rate": success_count / total_events,
            "avg_latency_ms": avg_latency,
            "session_id": self.session_id,
            "project": self.project_name
        }
    
    def establish_baseline(self, duration_seconds: int = 300):
        """Establish baseline behavior for drift detection"""
        print(f"📊 Establishing baseline for {duration_seconds}s...")
        time.sleep(duration_seconds)  # In real impl, this would monitor continuously
        
        if self.events:
            self.baseline_stats = {
                'avg_latency': sum(e.latency_ms for e in self.events) / len(self.events),
                'avg_tokens': 0,  # Calculate from events
                'event_count': len(self.events)
            }
            print(f"✅ Baseline established: {self.baseline_stats}")
    
    def export_events(self, filepath: str):
        """Export events to JSON for analysis"""
        with open(filepath, 'w') as f:
            json.dump([e.to_dict() for e in self.events], f, indent=2)
        print(f"📁 Events exported to {filepath}")


# Global instance for easy access
_monitor: Optional[AgentMonitor] = None


def init(api_key: Optional[str] = None, project_name: str = "default") -> AgentMonitor:
    """Initialize AgentOps monitoring"""
    global _monitor
    _monitor = AgentMonitor(api_key=api_key, project_name=project_name)
    print(f"🔍 AgentOps initialized | Project: {project_name} | Session: {_monitor.session_id}")
    return _monitor


def record_action(action_type: str = "agent_action"):
    """Decorator to record agent actions"""
    if _monitor is None:
        raise RuntimeError("AgentOps not initialized. Call agentops.init() first.")
    return _monitor.record_action(action_type)


def get_stats() -> Dict[str, Any]:
    """Get current monitoring stats"""
    if _monitor is None:
        return {"error": "AgentOps not initialized"}
    return _monitor.get_stats()


def export_events(filepath: str):
    """Export events to file"""
    if _monitor is None:
        raise RuntimeError("AgentOps not initialized")
    _monitor.export_events(filepath)
