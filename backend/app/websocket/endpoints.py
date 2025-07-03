"""
WebSocket endpoints.
"""
from typing import Optional

from fastapi import APIRouter, WebSocket, Query

from app.websocket.handler import websocket_handler

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """WebSocket endpoint for real-time chat functionality."""
    await websocket_handler.handle_connection(websocket, token)
