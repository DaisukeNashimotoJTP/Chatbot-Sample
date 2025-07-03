#!/usr/bin/env python3
"""
メッセージのグループ化テスト
1分以内の連続メッセージと1分以上の間隔があるメッセージを送信して、
UIでのグループ化動作を確認します。
"""

import requests
import time
from datetime import datetime

# API設定
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
MESSAGES_URL = f"{BASE_URL}/api/v1/messages"

# テストユーザー設定
USERNAME = "admin"
PASSWORD = "admin123"

def login():
    """ログイン処理"""
    print("=== ログイン ===")
    response = requests.post(LOGIN_URL, json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✓ ログイン成功")
        return token
    else:
        print(f"✗ ログイン失敗: {response.status_code}")
        return None

def send_message(token, channel_id, content):
    """メッセージ送信"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(MESSAGES_URL, json={
        "channel_id": channel_id,
        "content": content
    }, headers=headers)
    
    if response.status_code == 200:
        message_id = response.json()["id"]
        print(f"✓ メッセージ送信成功: {content}")
        return message_id
    else:
        print(f"✗ メッセージ送信失敗: {response.status_code}")
        return None

def get_channels(token):
    """チャンネル一覧取得"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/channels", headers=headers)
    
    if response.status_code == 200:
        channels = response.json()["channels"]
        print(f"✓ チャンネル取得成功: {len(channels)}個のチャンネル")
        return channels
    else:
        print(f"✗ チャンネル取得失敗: {response.status_code}")
        return []

def main():
    print("==================================================")
    print("メッセージグループ化テスト")
    print("==================================================")
    
    # ログイン
    token = login()
    if not token:
        return
    
    # チャンネル取得
    channels = get_channels(token)
    if not channels:
        return
    
    # 最初のチャンネルを使用
    channel_id = channels[0]["id"]
    print(f"テストチャンネル: {channels[0]['name']} ({channel_id})")
    print()
    
    # 1分以内の連続メッセージ（同じBoxに表示されるべき）
    print("=== 1分以内の連続メッセージ送信 ===")
    current_time = datetime.now()
    
    send_message(token, channel_id, f"メッセージ1 - {current_time.strftime('%H:%M:%S')}")
    time.sleep(5)  # 5秒間隔
    
    send_message(token, channel_id, f"メッセージ2 - {(datetime.now()).strftime('%H:%M:%S')}")
    time.sleep(5)  # 5秒間隔
    
    send_message(token, channel_id, f"メッセージ3 - {(datetime.now()).strftime('%H:%M:%S')}")
    print("✓ 1分以内の連続メッセージ送信完了")
    print()
    
    # 1分以上の間隔をあけて次のメッセージ（新しいBoxに表示されるべき）
    print("=== 1分以上の間隔をあけたメッセージ送信 ===")
    print("⏳ 65秒間待機中...")
    time.sleep(65)  # 65秒間隔
    
    send_message(token, channel_id, f"メッセージ4 - {(datetime.now()).strftime('%H:%M:%S')} (新しいBox)")
    print("✓ 1分以上の間隔をあけたメッセージ送信完了")
    print()
    
    # 再び1分以内の連続メッセージ
    print("=== 再び1分以内の連続メッセージ送信 ===")
    time.sleep(5)  # 5秒間隔
    
    send_message(token, channel_id, f"メッセージ5 - {(datetime.now()).strftime('%H:%M:%S')}")
    time.sleep(5)  # 5秒間隔
    
    send_message(token, channel_id, f"メッセージ6 - {(datetime.now()).strftime('%H:%M:%S')}")
    print("✓ 再び1分以内の連続メッセージ送信完了")
    print()
    
    print("==================================================")
    print("メッセージグループ化テスト完了")
    print("==================================================")
    print("フロントエンドでメッセージの表示を確認してください：")
    print("- メッセージ1-3は同じBoxに表示されるはず")
    print("- メッセージ4は新しいBoxに表示されるはず")
    print("- メッセージ5-6は同じBoxに表示されるはず")
    print("==================================================")

if __name__ == "__main__":
    main()
