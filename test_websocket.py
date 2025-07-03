#!/usr/bin/env python3
"""
WebSocket接続テストスクリプト
"""

import asyncio
import json
import websockets
import requests
from urllib.parse import urlencode

# 設定
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/v1/ws"

async def test_websocket_connection():
    """WebSocket接続をテストする"""
    
    # まず認証を行う
    login_data = {
        "email": "test@example.com", 
        "password": "securePassword123"
    }
    
    # ログイン
    login_data = {
        "email": "test@example.com",
        "password": "securePassword123"
    }
    
    response = requests.post(f"{BASE_URL}/v1/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"ログイン失敗: {response.status_code}")
        print(response.text)
        return
    
    tokens = response.json()
    access_token = tokens["access_token"]
    print(f"認証成功: {access_token[:20]}...")
    
    # WebSocket接続
    ws_url_with_token = f"{WS_URL}?token={access_token}"
    print(f"WebSocket URL: {ws_url_with_token}")
    
    try:
        async with websockets.connect(ws_url_with_token) as websocket:
            print("WebSocket接続成功!")
            
            # チャンネルに参加
            channel_id = "e85c157d-66f6-4c7d-aa2d-e5b66f733e4a"  # development チャンネル
            join_message = {
                "type": "join_channel",
                "data": {
                    "channel_id": channel_id
                }
            }
            
            await websocket.send(json.dumps(join_message))
            print(f"チャンネル {channel_id} に参加要求を送信")
            
            # メッセージ送信
            send_message = {
                "type": "send_message",
                "data": {
                    "channel_id": channel_id,
                    "content": "WebSocketテストメッセージ"
                }
            }
            
            await websocket.send(json.dumps(send_message))
            print("メッセージ送信")
            
            # レスポンスを待機
            try:
                for i in range(3):
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    message = json.loads(response)
                    print(f"受信: {message}")
                    
            except asyncio.TimeoutError:
                print("タイムアウト - レスポンス待機終了")
                
    except Exception as e:
        print(f"WebSocket接続エラー: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
