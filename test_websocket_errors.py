#!/usr/bin/env python3
"""
WebSocketエラーハンドリングテストスクリプト
"""

import asyncio
import json
import websockets
import requests

# 設定
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/v1/ws"

async def test_websocket_error_handling():
    """WebSocketエラーハンドリングをテストする"""
    
    print("=== WebSocketエラーハンドリングテスト ===")
    
    # 1. 正常な認証でのWebSocket接続テスト
    print("\n1. 正常な認証でのWebSocket接続テスト")
    login_data = {
        "email": "test@example.com", 
        "password": "securePassword123"
    }
    
    response = requests.post(f"{BASE_URL}/v1/auth/login", json=login_data)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        print(f"✓ 認証成功")
        
        # 正常なWebSocket接続
        ws_url_with_token = f"{WS_URL}?token={access_token}"
        try:
            async with websockets.connect(ws_url_with_token) as websocket:
                print("✓ WebSocket接続成功")
                
                # チャンネル参加テスト
                join_message = {
                    "type": "join_channel",
                    "data": {"channel_id": "e85c157d-66f6-4c7d-aa2d-e5b66f733e4a"}
                }
                await websocket.send(json.dumps(join_message))
                print("✓ チャンネル参加メッセージ送信成功")
                
                # レスポンス受信
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                message = json.loads(response)
                print(f"✓ レスポンス受信: {message['type']}")
                
        except Exception as e:
            print(f"✗ WebSocket接続エラー: {e}")
    else:
        print(f"✗ 認証失敗: {response.status_code}")
        return
    
    # 2. 無効なトークンでのWebSocket接続テスト
    print("\n2. 無効なトークンでのWebSocket接続テスト")
    invalid_ws_url = f"{WS_URL}?token=invalid_token"
    try:
        async with websockets.connect(invalid_ws_url) as websocket:
            print("✗ 無効なトークンで接続成功（予期しない動作）")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"✓ 無効なトークンで接続拒否（期待される動作）: {e.code}")
    except Exception as e:
        print(f"✓ 無効なトークンで接続失敗（期待される動作）: {e}")
    
    # 3. トークンなしでのWebSocket接続テスト
    print("\n3. トークンなしでのWebSocket接続テスト")
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✗ トークンなしで接続成功（予期しない動作）")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"✓ トークンなしで接続拒否（期待される動作）: {e.code}")
    except Exception as e:
        print(f"✓ トークンなしで接続失敗（期待される動作）: {e}")
    
    # 4. 無効なメッセージ形式のテスト
    print("\n4. 無効なメッセージ形式のテスト")
    try:
        async with websockets.connect(ws_url_with_token) as websocket:
            # 無効なJSON送信
            await websocket.send("invalid json")
            print("✓ 無効なJSONメッセージ送信")
            
            # エラーレスポンス受信
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                message = json.loads(response)
                if message.get('type') == 'error':
                    print(f"✓ エラーレスポンス受信: {message['data']['message']}")
                else:
                    print(f"? 予期しないレスポンス: {message}")
            except asyncio.TimeoutError:
                print("? エラーレスポンスなし（サーバーが無効なメッセージを無視）")
                
    except Exception as e:
        print(f"✓ 無効なメッセージでエラー: {e}")
    
    print("\n=== WebSocketエラーハンドリングテスト完了 ===")

if __name__ == "__main__":
    asyncio.run(test_websocket_error_handling())
