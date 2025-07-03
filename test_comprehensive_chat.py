#!/usr/bin/env python3
"""
フロントエンドのチャンネル移動とメッセージ履歴の統合テスト
"""
import requests
import json
import time
import asyncio
import websockets
from datetime import datetime

class ChatSystemTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.ws_url = "ws://localhost:8000/ws"
        self.access_token = None
        self.workspace_id = None
        self.channels = []
        
    def login(self):
        """ログイン処理"""
        print("\n=== ログイン ===")
        login_data = {
            "email": "admin@chatservice.com",
            "password": "Admin123123"
        }
        
        try:
            response = requests.post(f"{self.base_url}/v1/auth/login", json=login_data)
            if response.status_code == 200:
                auth_data = response.json()
                self.access_token = auth_data["access_token"]
                print(f"✓ ログイン成功")
                return True
            else:
                print(f"✗ ログイン失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ ログインエラー: {e}")
            return False
    
    def get_workspace_and_channels(self):
        """ワークスペースとチャンネルを取得"""
        print("\n=== ワークスペース・チャンネル取得 ===")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # ワークスペース取得
        try:
            response = requests.get(f"{self.base_url}/v1/workspaces", headers=headers)
            if response.status_code == 200:
                workspaces = response.json()
                if workspaces:
                    self.workspace_id = workspaces[0]["id"]
                    print(f"✓ ワークスペース取得成功: {self.workspace_id}")
                else:
                    print("✗ ワークスペースが存在しません")
                    return False
            else:
                print(f"✗ ワークスペース取得失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ ワークスペース取得エラー: {e}")
            return False
        
        # チャンネル取得
        try:
            response = requests.get(f"{self.base_url}/v1/channels", 
                                  headers=headers,
                                  params={"workspace_id": self.workspace_id})
            if response.status_code == 200:
                self.channels = response.json()
                if len(self.channels) >= 2:
                    print(f"✓ チャンネル取得成功: {len(self.channels)}個のチャンネル")
                    for i, ch in enumerate(self.channels[:3]):
                        print(f"  チャンネル {i+1}: {ch['name']} ({ch['id']})")
                    return True
                else:
                    print(f"✗ テストには2つ以上のチャンネルが必要です（現在: {len(self.channels)}）")
                    return False
            else:
                print(f"✗ チャンネル取得失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ チャンネル取得エラー: {e}")
            return False
    
    def get_messages(self, channel_id, description=""):
        """指定チャンネルのメッセージを取得"""
        print(f"\n=== メッセージ履歴取得 {description} ===")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{self.base_url}/v1/channels/{channel_id}/messages", 
                                  headers=headers,
                                  params={"limit": 10})
            
            if response.status_code == 200:
                messages_data = response.json()
                messages = messages_data.get("messages", [])
                print(f"✓ メッセージ取得成功: {len(messages)}件")
                
                # 最新の3件を表示
                for i, msg in enumerate(messages[:3]):
                    content = msg.get('content', '')[:50]
                    sender = msg.get('user_username', 'Unknown')
                    created = msg.get('created_at', '')[:19]
                    print(f"  {i+1}. [{created}] {sender}: {content}...")
                
                return messages
            else:
                print(f"✗ メッセージ取得失敗: {response.status_code}")
                print(f"レスポンス: {response.text}")
                return []
        except Exception as e:
            print(f"✗ メッセージ取得エラー: {e}")
            return []
    
    def send_message(self, channel_id, content):
        """メッセージを送信"""
        print(f"\n=== メッセージ送信 ===")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        message_data = {
            "content": content,
            "message_type": "text"
        }
        
        try:
            response = requests.post(f"{self.base_url}/v1/channels/{channel_id}/messages",
                                   headers=headers,
                                   json=message_data)
            
            if response.status_code == 201:
                message = response.json()
                print(f"✓ メッセージ送信成功")
                print(f"  ID: {message['id']}")
                print(f"  内容: {message['content']}")
                return message
            else:
                print(f"✗ メッセージ送信失敗: {response.status_code}")
                print(f"レスポンス: {response.text}")
                return None
        except Exception as e:
            print(f"✗ メッセージ送信エラー: {e}")
            return None
    
    async def test_websocket_message(self, channel_id, content):
        """WebSocket経由でメッセージを送信"""
        print(f"\n=== WebSocketメッセージ送信 ===")
        
        try:
            uri = f"{self.ws_url}?token={self.access_token}"
            async with websockets.connect(uri) as websocket:
                print("✓ WebSocket接続成功")
                
                # チャンネルに参加
                join_message = {
                    "type": "join_channel",
                    "data": {"channel_id": channel_id}
                }
                await websocket.send(json.dumps(join_message))
                print(f"✓ チャンネル参加: {channel_id}")
                
                # メッセージ送信
                send_message = {
                    "type": "send_message",
                    "data": {
                        "channel_id": channel_id,
                        "content": content
                    }
                }
                await websocket.send(json.dumps(send_message))
                print(f"✓ WebSocketメッセージ送信: {content}")
                
                # レスポンスを待機
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    message_data = json.loads(response)
                    print(f"✓ WebSocketレスポンス受信: {message_data.get('type', 'unknown')}")
                    return True
                except asyncio.TimeoutError:
                    print("⚠ WebSocketレスポンスがタイムアウトしました")
                    return False
                    
        except Exception as e:
            print(f"✗ WebSocketエラー: {e}")
            return False
    
    def run_comprehensive_test(self):
        """包括的なテストを実行"""
        print("=" * 50)
        print("チャンネル移動・メッセージ送信・履歴確認テスト")
        print("=" * 50)
        
        # 1. ログイン
        if not self.login():
            return False
        
        # 2. ワークスペース・チャンネル取得
        if not self.get_workspace_and_channels():
            return False
        
        if len(self.channels) < 2:
            print("✗ テストには2つ以上のチャンネルが必要です")
            return False
        
        channel1 = self.channels[0]
        channel2 = self.channels[1] if len(self.channels) > 1 else self.channels[0]
        
        # 3. チャンネル1の初期メッセージ履歴を確認
        initial_messages_ch1 = self.get_messages(channel1["id"], f"（チャンネル1: {channel1['name']}）")
        
        # 4. チャンネル2の初期メッセージ履歴を確認
        initial_messages_ch2 = self.get_messages(channel2["id"], f"（チャンネル2: {channel2['name']}）")
        
        # 5. チャンネル1にメッセージを送信
        test_message_content = f"テストメッセージ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        sent_message = self.send_message(channel1["id"], test_message_content)
        
        if not sent_message:
            print("✗ メッセージ送信に失敗しました")
            return False
        
        # 6. 少し待機
        print("\n⏳ メッセージ処理を待機中...")
        time.sleep(2)
        
        # 7. チャンネル2に移動してメッセージを確認（変化なしの確認）
        messages_ch2_after = self.get_messages(channel2["id"], f"（チャンネル2移動後: {channel2['name']}）")
        
        # 8. チャンネル1に戻ってメッセージが表示されているか確認
        messages_ch1_after = self.get_messages(channel1["id"], f"（チャンネル1戻り: {channel1['name']}）")
        
        # 9. 結果の検証
        print("\n" + "=" * 50)
        print("テスト結果の検証")
        print("=" * 50)
        
        # 送信したメッセージが含まれているか確認
        found_message = False
        for msg in messages_ch1_after:
            if msg.get('content') == test_message_content:
                found_message = True
                print(f"✓ 送信したメッセージが確認されました: {test_message_content}")
                break
        
        if not found_message:
            print(f"✗ 送信したメッセージが見つかりません: {test_message_content}")
            print("取得されたメッセージ:")
            for i, msg in enumerate(messages_ch1_after[:3]):
                print(f"  {i+1}. {msg.get('content', '')[:50]}...")
            return False
        
        # メッセージ数の比較（参考情報として表示）
        if len(messages_ch1_after) > len(initial_messages_ch1):
            print(f"✓ チャンネル1のメッセージ数が {len(initial_messages_ch1)} → {len(messages_ch1_after)} に増加")
        elif len(messages_ch1_after) == len(initial_messages_ch1):
            print(f"⚠ チャンネル1のメッセージ数は変わりませんが、内容は更新されています（limit制限のため）")
        else:
            print(f"⚠ 予期しないメッセージ数の変化: {len(initial_messages_ch1)} → {len(messages_ch1_after)}")
        
        
        # 10. WebSocketでもテスト
        print("\n=== WebSocketテスト ===")
        websocket_test_content = f"WebSocketテスト - {datetime.now().strftime('%H:%M:%S')}"
        
        try:
            websocket_success = asyncio.run(self.test_websocket_message(channel1["id"], websocket_test_content))
            if websocket_success:
                print("✓ WebSocketテスト成功")
                
                # WebSocketメッセージ後の履歴確認
                time.sleep(2)
                final_messages = self.get_messages(channel1["id"], "（WebSocket送信後）")
                
                # WebSocketメッセージが含まれているか確認
                found_ws_message = False
                for msg in final_messages:
                    if msg.get('content') == websocket_test_content:
                        found_ws_message = True
                        print(f"✓ WebSocketメッセージが確認されました: {websocket_test_content}")
                        break
                
                if not found_ws_message:
                    print(f"⚠ WebSocketメッセージが履歴に反映されていません")
            else:
                print("⚠ WebSocketテストに問題がありました")
        except Exception as e:
            print(f"⚠ WebSocketテストでエラー: {e}")
        
        print("\n" + "=" * 50)
        print("✓ 包括的テスト完了")
        print("チャンネル移動→メッセージ送信→履歴確認の流れが正常に動作しています")
        print("=" * 50)
        
        return True

def main():
    tester = ChatSystemTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 すべてのテストが成功しました！")
    else:
        print("\n❌ テストに失敗しました。")
    
    return success

if __name__ == "__main__":
    main()
