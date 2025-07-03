#!/usr/bin/env python3
"""
WebSocket機能の動作確認テスト
"""
import asyncio
import websockets
import json
import requests

BASE_URL = "http://localhost:8000"

async def test_full_websocket_flow():
    """完全なWebSocketフローのテスト"""
    
    print("🔐 1. ユーザー認証...")
    auth_data = {
        "email": "admin@chatservice.com",
        "password": "Admin123123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/auth/login", json=auth_data)
        
        if response.status_code == 200:
            auth_result = response.json()
            access_token = auth_result.get("access_token")
            user_data = auth_result.get("user")
            print(f"✅ 認証成功: {user_data.get('display_name')}")
            
            # ワークスペースとチャンネル取得
            print("\n📁 2. ワークスペース・チャンネル取得...")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            workspaces_response = requests.get(f"{BASE_URL}/v1/workspaces", headers=headers)
            if workspaces_response.status_code == 200:
                workspaces = workspaces_response.json()
                workspace_id = workspaces[0]["id"]
                print(f"✅ ワークスペース: {workspaces[0]['name']}")
                
                channels_response = requests.get(f"{BASE_URL}/v1/channels?workspace_id={workspace_id}", headers=headers)
                if channels_response.status_code == 200:
                    channels = channels_response.json()
                    channel_id = channels[0]["id"]
                    print(f"✅ チャンネル: {channels[0]['name']}")
                    
                    # WebSocket接続テスト
                    print("\n🔌 3. WebSocket接続テスト...")
                    ws_url = f"ws://localhost:8000/v1/ws?token={access_token}"
                    
                    async with websockets.connect(ws_url) as websocket:
                        print("✅ WebSocket接続成功")
                        
                        # チャンネル参加
                        join_message = {
                            "type": "join_channel",
                            "data": {"channel_id": channel_id}
                        }
                        await websocket.send(json.dumps(join_message))
                        print("📤 チャンネル参加メッセージ送信")
                        
                        # 応答を受信
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                            response_data = json.loads(response)
                            print(f"📥 応答受信: {response_data.get('type')}")
                            
                            # メッセージ送信テスト
                            send_message = {
                                "type": "send_message",
                                "data": {
                                    "channel_id": channel_id,
                                    "content": "WebSocketテストメッセージ ✨"
                                }
                            }
                            await websocket.send(json.dumps(send_message))
                            print("📤 メッセージ送信完了")
                            
                            # メッセージ応答を受信
                            try:
                                message_response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                                message_data = json.loads(message_response)
                                print(f"📥 メッセージ応答: {message_data.get('type')}")
                                
                                print("\n🎉 WebSocketフローテスト完了!")
                                print("✅ 認証 -> ✅ チャンネル参加 -> ✅ メッセージ送信")
                                
                            except asyncio.TimeoutError:
                                print("⚠️ メッセージ応答のタイムアウト")
                                
                        except asyncio.TimeoutError:
                            print("⚠️ チャンネル参加応答のタイムアウト")
                            
                else:
                    print("❌ チャンネル取得失敗")
            else:
                print("❌ ワークスペース取得失敗")
                
        else:
            print(f"❌ 認証失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    asyncio.run(test_full_websocket_flow())
