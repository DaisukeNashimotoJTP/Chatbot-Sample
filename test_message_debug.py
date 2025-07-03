#!/usr/bin/env python3
"""
WebSocket debug test script - メッセージ送信のデバッグテスト
"""

import asyncio
import websockets
import json
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_message_flow():
    """メッセージ送信フローのテスト"""
    
    # テスト用のトークンとチャンネル
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTE2MDcxNDksInN1YiI6IjhiZmZjOGI5LTU2YmUtNDYwNS04OGJhLWNiNmJlYmUwNWYzMiJ9.WtYFwz2vCWEnacEmN-RoIHU6m8jBEqw877M3h96V6CE"
    channel_id = "3e198b99-334a-4b33-96ec-c2ef989caeea"
    
    uri = f"ws://localhost:8000/v1/ws?token={token}"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"WebSocket connected")
            
            # チャンネルに参加
            join_message = {
                "type": "join_channel",
                "data": {
                    "channel_id": channel_id
                }
            }
            await websocket.send(json.dumps(join_message))
            logger.info(f"Joined channel: {channel_id}")
            
            # メッセージを受信するためのタスク
            async def receive_messages():
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        logger.info(f"Received message: {data}")
                    except websockets.exceptions.ConnectionClosed:
                        logger.info("WebSocket connection closed")
                        break
                    except Exception as e:
                        logger.error(f"Error receiving message: {e}")
                        
            # 受信タスクを開始
            receive_task = asyncio.create_task(receive_messages())
            
            # 短い待機
            await asyncio.sleep(1)
            
            # メッセージを送信
            send_message = {
                "type": "send_message",
                "data": {
                    "channel_id": channel_id,
                    "content": "デバッグテストメッセージ"
                }
            }
            await websocket.send(json.dumps(send_message))
            logger.info(f"Sent message: {send_message}")
            
            # 受信を待機
            await asyncio.sleep(3)
            
            # 受信タスクをキャンセル
            receive_task.cancel()
            
    except Exception as e:
        logger.error(f"WebSocket test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_message_flow())
