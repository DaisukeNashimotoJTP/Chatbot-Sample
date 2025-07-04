#!/usr/bin/env python3
"""
ダミーデータを削除するスクリプト
- チャンネル内のすべてのメッセージを削除
- 必要に応じてチャンネルも削除
"""

import requests
import json

# API設定
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/v1/auth/login"
CHANNELS_URL = f"{BASE_URL}/v1/channels"
MESSAGES_URL = f"{BASE_URL}/v1/messages"

# テストユーザー設定
EMAIL = "admin@chatservice.com"
PASSWORD = "Admin123123"

def login():
    """ログイン処理"""
    print("=== ログイン ===")
    response = requests.post(LOGIN_URL, json={
        "email": EMAIL,
        "password": PASSWORD
    }, headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✓ ログイン成功")
        return token
    else:
        print(f"✗ ログイン失敗: {response.status_code}")
        print(f"レスポンス: {response.text}")
        return None

def get_workspaces(token):
    """ワークスペース一覧取得"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/v1/workspaces", headers=headers)
    
    if response.status_code == 200:
        workspaces = response.json()["workspaces"]
        print(f"✓ ワークスペース取得成功: {len(workspaces)}個のワークスペース")
        return workspaces
    else:
        print(f"✗ ワークスペース取得失敗: {response.status_code}")
        return []

def get_channels(token, workspace_id):
    """チャンネル一覧取得"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"workspace_id": workspace_id}
    response = requests.get(CHANNELS_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        channels = response.json()
        print(f"✓ チャンネル取得成功: {len(channels)}個のチャンネル")
        return channels
    else:
        print(f"✗ チャンネル取得失敗: {response.status_code}")
        print(f"レスポンス: {response.text}")
        return []

def get_messages(token, channel_id):
    """メッセージ一覧取得"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"channel_id": channel_id, "limit": 100}
    response = requests.get(MESSAGES_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        messages = response.json()["messages"]
        return messages
    else:
        print(f"✗ メッセージ取得失敗: {response.status_code}")
        return []

def delete_message(token, message_id):
    """メッセージ削除"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{MESSAGES_URL}/{message_id}", headers=headers)
    
    if response.status_code == 200:
        return True
    else:
        print(f"✗ メッセージ削除失敗: {response.status_code}")
        return False

def main():
    print("==================================================")
    print("ダミーデータクリーンアップスクリプト")
    print("==================================================")
    
    # ログイン
    token = login()
    if not token:
        return
    
    # チャンネル取得
    channels = get_channels(token)
    if not channels:
        return
    
    # 各チャンネルのメッセージを削除
    for channel in channels:
        channel_id = channel["id"]
        channel_name = channel["name"]
        
        print(f"\n=== チャンネル: {channel_name} ===")
        
        # メッセージ取得
        messages = get_messages(token, channel_id)
        print(f"メッセージ数: {len(messages)}")
        
        if len(messages) == 0:
            print("削除するメッセージがありません")
            continue
        
        # 削除確認
        print(f"このチャンネルの{len(messages)}件のメッセージを削除しますか？")
        confirm = input("削除する場合は 'yes' を入力してください: ")
        
        if confirm.lower() != 'yes':
            print("スキップしました")
            continue
        
        # メッセージ削除
        deleted_count = 0
        for message in messages:
            if delete_message(token, message["id"]):
                deleted_count += 1
                print(f"✓ メッセージ削除: {message['content'][:50]}...")
            else:
                print(f"✗ メッセージ削除失敗: {message['id']}")
        
        print(f"✓ {deleted_count}件のメッセージを削除しました")
    
    print("\n==================================================")
    print("クリーンアップ完了")
    print("==================================================")

if __name__ == "__main__":
    main()
