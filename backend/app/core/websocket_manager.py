from typing import List, Dict, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.session_users: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
            self.session_users[session_id] = set()
        
        self.active_connections[session_id].append(websocket)
        self.session_users[session_id].add(user_id)
        
        logger.info(f"User {user_id} connected to session {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            try:
                self.active_connections[session_id].remove(websocket)
                self.session_users[session_id].discard(user_id)
                
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
                    del self.session_users[session_id]
                
                logger.info(f"User {user_id} disconnected from session {session_id}")
            except ValueError:
                pass
    
    async def broadcast_transcription(self, session_id: str, data: dict):
        """Broadcast transcription to all connected clients."""
        if session_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json({
                        "type": "transcription",
                        "data": data
                    })
                except Exception as e:
                    logger.error(f"Error broadcasting transcription: {e}")
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.active_connections[session_id].remove(conn)
    
    async def broadcast_translation(self, session_id: str, data: dict):
        """Broadcast translation to all connected clients."""
        if session_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json({
                        "type": "translation",
                        "data": data
                    })
                except Exception as e:
                    logger.error(f"Error broadcasting translation: {e}")
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.active_connections[session_id].remove(conn)
    
    async def broadcast_summary(self, session_id: str, data: dict):
        """Broadcast summary to all connected clients."""
        if session_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json({
                        "type": "summary",
                        "data": data
                    })
                except Exception as e:
                    logger.error(f"Error broadcasting summary: {e}")
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.active_connections[session_id].remove(conn)
    
    async def broadcast_insights(self, session_id: str, data: dict):
        """Broadcast extracted keywords and formulas."""
        if session_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json({
                        "type": "insights",
                        "data": data
                    })
                except Exception as e:
                    logger.error(f"Error broadcasting insights: {e}")
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.active_connections[session_id].remove(conn)
    
    def get_active_users_count(self, session_id: str) -> int:
        """Get count of active users in a session."""
        return len(self.session_users.get(session_id, set()))


manager = ConnectionManager()
