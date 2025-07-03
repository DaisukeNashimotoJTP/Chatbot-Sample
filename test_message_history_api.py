#!/usr/bin/env python3
"""
フロントエンドのメッセージ履歴取得APIをテストするスクリプト
"""
import requests
import json
from datetime import datetime

def test_message_history_api():
    base_url = "http://localhost:8000"
    
    print("=== メッセージ履歴取得APIテスト ===")
    
    # 1. ログイン
    print("\n1. ログイン中...")
    login_data = {
        "email": "admin@chatservice.com",
        "password": "Admin123123"
    }
    
    try:
        response = requests.post(f"{base_url}/v1/auth/login", json=login_data)
        if response.status_code == 200:
            auth_data = response.json()
            access_token = auth_data["access_token"]
            print(f"✓ ログイン成功: {access_token[:50]}...")
        else:
            print(f"✗ ログイン失敗: {response.status_code}")
            print(f"レスポンス: {response.text}")
            return
    except Exception as e:
        print(f"✗ ログインエラー: {e}")
        return
    
    # 2. ヘッダーを設定
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 3. ワークスペース取得
    print("\n2. ワークスペース取得中...")
    try:
        response = requests.get(f"{base_url}/v1/workspaces", headers=headers)
        if response.status_code == 200:
            workspaces = response.json()
            if workspaces:
                workspace_id = workspaces[0]["id"]
                print(f"✓ ワークスペース取得成功: {workspace_id}")
            else:
                print("✗ ワークスペースが存在しません")
                return
        else:
            print(f"✗ ワークスペース取得失敗: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ ワークスペース取得エラー: {e}")
        return
    
    # 4. チャンネル取得
    print("\n3. チャンネル取得中...")
    try:
        response = requests.get(f"{base_url}/v1/channels", 
                              headers=headers,
                              params={"workspace_id": workspace_id})
        if response.status_code == 200:
            channels = response.json()
            if channels:
                channel_id = channels[0]["id"]
                channel_name = channels[0]["name"]
                print(f"✓ チャンネル取得成功: {channel_name} ({channel_id})")
            else:
                print("✗ チャンネルが存在しません")
                return
        else:
            print(f"✗ チャンネル取得失敗: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ チャンネル取得エラー: {e}")
        return
    
    # 5. メッセージ履歴取得
    print(f"\n4. メッセージ履歴取得中（チャンネル: {channel_id}）...")
    try:
        response = requests.get(f"{base_url}/v1/channels/{channel_id}/messages", 
                              headers=headers,
                              params={"limit": 10})
        print(f"ステータス: {response.status_code}")
        
        if response.status_code == 200:
            messages_data = response.json()
            print(f"✓ メッセージ履歴取得成功")
            print(f"レスポンス構造: {json.dumps(messages_data, indent=2, default=str)}")
            
            if "messages" in messages_data:
                messages = messages_data["messages"]
                print(f"メッセージ数: {len(messages)}")
                
                for i, msg in enumerate(messages[:3]):  # 最初の3件を表示
                    print(f"メッセージ {i+1}: {msg.get('content', '')[:50]}...")
                    print(f"  送信者: {msg.get('user_username', 'Unknown')}")
                    print(f"  作成日時: {msg.get('created_at', 'Unknown')}")
            else:
                print("✗ messagesキーが見つかりません")
                
        elif response.status_code == 403:
            print("✗ アクセス拒否（403）- 認証またはアクセス権限の問題")
            print(f"レスポンス: {response.text}")
        else:
            print(f"✗ メッセージ履歴取得失敗: {response.status_code}")
            print(f"レスポンス: {response.text}")
    except Exception as e:
        print(f"✗ メッセージ履歴取得エラー: {e}")
        return
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_message_history_api()
