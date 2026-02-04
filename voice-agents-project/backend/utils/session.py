"""Session Management for concurrent voice agent sessions."""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class SessionState(Enum):
    """Possible session states."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDING = "ending"
    ENDED = "ended"
    ERROR = "error"


@dataclass
class SessionData:
    """Data container for a single session."""
    session_id: str
    agent_id: str
    state: SessionState = SessionState.INITIALIZING
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    conversation_history: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evaluation_report: Optional[Dict] = None
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.update_activity()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired due to inactivity."""
        return datetime.utcnow() - self.last_activity > timedelta(minutes=timeout_minutes)


class SessionManager:
    """
    Manages multiple concurrent voice agent sessions.
    
    Thread-safe session management with automatic cleanup.
    """
    
    def __init__(self, max_sessions: int = 1000, cleanup_interval_seconds: int = 300):
        """
        Initialize session manager.
        
        Args:
            max_sessions: Maximum concurrent sessions allowed.
            cleanup_interval_seconds: Interval for cleanup task.
        """
        self._sessions: Dict[str, SessionData] = {}
        self._lock = asyncio.Lock()
        self._max_sessions = max_sessions
        self._cleanup_interval = cleanup_interval_seconds
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start_cleanup_task(self):
        """Start the background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_cleanup_task(self):
        """Stop the background cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup_loop(self):
        """Background loop for cleaning up expired sessions."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in cleanup loop: {e}")
    
    async def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        async with self._lock:
            expired = [
                sid for sid, session in self._sessions.items()
                if session.is_expired() or session.state == SessionState.ENDED
            ]
            for sid in expired:
                del self._sessions[sid]
            
            if expired:
                print(f"Cleaned up {len(expired)} expired sessions")
    
    async def create_session(self, agent_id: str, metadata: Optional[Dict] = None) -> str:
        """
        Create a new session.
        
        Args:
            agent_id: The agent to use for this session.
            metadata: Optional session metadata.
            
        Returns:
            Session ID.
            
        Raises:
            RuntimeError: If max sessions exceeded.
        """
        async with self._lock:
            if len(self._sessions) >= self._max_sessions:
                # Try cleanup before failing
                await self._cleanup_expired_sessions()
                if len(self._sessions) >= self._max_sessions:
                    raise RuntimeError("Maximum concurrent sessions exceeded")
            
            session_id = str(uuid.uuid4())
            self._sessions[session_id] = SessionData(
                session_id=session_id,
                agent_id=agent_id,
                metadata=metadata or {}
            )
            
            return session_id
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session by ID."""
        async with self._lock:
            return self._sessions.get(session_id)
    
    async def update_session_state(self, session_id: str, state: SessionState) -> bool:
        """
        Update session state.
        
        Returns:
            True if session exists and was updated.
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.state = state
                session.update_activity()
                return True
            return False
    
    async def add_message(self, session_id: str, role: str, content: str) -> bool:
        """
        Add message to session history.
        
        Returns:
            True if session exists and message was added.
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.add_message(role, content)
                return True
            return False
    
    async def set_evaluation_report(self, session_id: str, report: Dict) -> bool:
        """
        Set the evaluation report for a session.
        
        Returns:
            True if session exists and report was set.
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.evaluation_report = report
                return True
            return False
    
    async def end_session(self, session_id: str) -> Optional[SessionData]:
        """
        End and remove a session.
        
        Returns:
            The session data before removal, or None if not found.
        """
        async with self._lock:
            session = self._sessions.pop(session_id, None)
            if session:
                session.state = SessionState.ENDED
            return session
    
    async def get_active_session_count(self) -> int:
        """Get count of active sessions."""
        async with self._lock:
            return len([s for s in self._sessions.values() if s.state == SessionState.ACTIVE])
    
    async def get_session_stats(self) -> Dict:
        """Get session statistics."""
        async with self._lock:
            states = {}
            for session in self._sessions.values():
                state_name = session.state.value
                states[state_name] = states.get(state_name, 0) + 1
            
            return {
                "total_sessions": len(self._sessions),
                "by_state": states,
                "max_sessions": self._max_sessions
            }


# Global session manager instance
session_manager = SessionManager()