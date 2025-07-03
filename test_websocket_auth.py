#!/usr/bin/env python3
"""
WebSocket認証テストスクリプト
"""
import asyncio
import websockets
import json
import requests
from urllib.parse import urlencode

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

async def test_websocket_auth():
    """WebSocket認証のテスト"""
    
    # まずHTTP APIで認証を行う
    print("1. ユーザー認証...")
    auth_data = {
        "email": "admin@chatservice.com",
        "password": "Admin123123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/auth/login", json=auth_data)
        print(f"Auth response status: {response.status_code}")
        print(f"Auth response: {response.text}")
        
        if response.status_code == 200:
            auth_result = response.json()
            access_token = auth_result.get("access_token")
            user_data = auth_result.get("user")
            print(f"Access token: {access_token[:50]}...")
            print(f"User: {user_data.get('display_name')} ({user_data.get('email')})")
            
            # ワークスペースのチャンネルリストを取得
            print("\n2. チャンネルリスト取得...")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # まずワークスペースを取得
            workspaces_response = requests.get(f"{BASE_URL}/v1/workspaces", headers=headers)
            print(f"Workspaces response: {workspaces_response.status_code}")
            
            if workspaces_response.status_code == 200:
                workspaces = workspaces_response.json()
                if workspaces:
                    workspace_id = workspaces[0]["id"]
                    print(f"Using workspace: {workspace_id}")
                    
                    # チャンネルを取得
                    channels_response = requests.get(f"{BASE_URL}/v1/channels?workspace_id={workspace_id}", headers=headers)
                    print(f"Channels response: {channels_response.status_code}")
                    
                    if channels_response.status_code == 200:
                        channels = channels_response.json()
                        if channels:
                            channel_id = channels[0]["id"]
                            print(f"Using channel: {channel_id}")
                        else:
                            print("チャンネルが見つかりません")
                            channel_id = "ccb41a60-0b86-43b7-89dd-8d70d5e7f410"  # デフォルト
                    else:
                        print("チャンネル取得に失敗")
                        channel_id = "ccb41a60-0b86-43b7-89dd-8d70d5e7f410"  # デフォルト
                else:
                    print("ワークスペースが見つかりません")
                    channel_id = "ccb41a60-0b86-43b7-89dd-8d70d5e7f410"  # デフォルト
            else:
                print("ワークスペース取得に失敗")
                channel_id = "ccb41a60-0b86-43b7-89dd-8d70d5e7f410"  # デフォルト
            
            # WebSocket接続をテスト
            print("\n3. WebSocket接続テスト...")
            
            # トークンをクエリパラメータで送信
            ws_url = f"{WS_URL}/v1/ws?token={access_token}"
            
            try:
                async with websockets.connect(ws_url) as websocket:
                    print("WebSocket接続成功!")
                    
                    # テストメッセージを送信
                    test_message = {
                        "type": "join_channel",
                        "data": {
                            "channel_id": channel_id
                        }
                    }
                    
                    await websocket.send(json.dumps(test_message))
                    print("テストメッセージ送信完了")
                    
                    # 応答を待つ
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        print(f"WebSocket応答: {response}")
                    except asyncio.TimeoutError:
                        print("WebSocket応答のタイムアウト")
                    
            except Exception as ws_error:
                print(f"WebSocket接続エラー: {ws_error}")
                
        else:
            print(f"認証失敗: {response.status_code}")
            
    except Exception as e:
        print(f"認証エラー: {e}")

async def test_websocket_without_token():
    """トークンなしでWebSocket接続をテスト"""
    print("\n4. トークンなしでWebSocket接続テスト...")
    
    try:
        ws_url = f"{WS_URL}/v1/ws"
        async with websockets.connect(ws_url) as websocket:
            print("トークンなしで接続成功（予期しない）")
    except Exception as e:
        print(f"トークンなしで接続失敗（期待通り）: {e}")

async def test_websocket_invalid_token():
    """無効なトークンでWebSocket接続をテスト"""
    print("\n5. 無効なトークンでWebSocket接続テスト...")
    
    try:
        ws_url = f"{WS_URL}/v1/ws?token=invalid_token"
        async with websockets.connect(ws_url) as websocket:
            print("無効なトークンで接続成功（予期しない）")
    except Exception as e:
        print(f"無効なトークンで接続失敗（期待通り）: {e}")

async def main():
    """メイン関数"""
    print("WebSocket認証テストを開始...")
    
    await test_websocket_auth()
    await test_websocket_without_token()
    await test_websocket_invalid_token()
    
    print("\nテスト完了")

if __name__ == "__main__":
    asyncio.run(main())
