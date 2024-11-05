import requests
import logging
from typing import Dict, Optional
from datetime import datetime
from models.market_data import MarketData

class DiscordNotifier:
    """Discord Webhookを使用して通知を送信するクラス"""

    def __init__(self, config: Dict[str, str]):
        """
        初期化
        
        Args:
            config: Discord関連の設定辞書
        """
        self.webhook_url = config['webhook_url']
        self.username = config['username']
        self.avatar_url = config.get('avatar_url', '')
        self.embed_color = int(config.get('embed_color', '3447003'))
        self._last_data: Optional[MarketData] = None

    def _create_market_embed(self, data: MarketData) -> Dict:
        """
        マーケットデータのembedを作成
        
        Args:
            data: MarketDataオブジェクト
        """
        # 価格変動の計算
        changes = {}
        if self._last_data:
            changes = data.get_price_changes(self._last_data)

        # Trump のフィールド作成
        trump_value = (
            f"🎯 確率: {data.probabilities['trump']}\n"
            f"📊 取引量: {data.volumes['trump']}\n"
            f"💰 買値(Yes): {data.prices['trump']['buy_yes']}\n"
            f"💰 買値(No): {data.prices['trump']['buy_no']}"
        )
        if changes.get('trump'):
            trump_value += f"\n📈 変動: {changes['trump']:+.1f}%"

        # Harris のフィールド作成
        harris_value = (
            f"🎯 確率: {data.probabilities['harris']}\n"
            f"📊 取引量: {data.volumes['harris']}\n"
            f"💰 買値(Yes): {data.prices['harris']['buy_yes']}\n"
            f"💰 買値(No): {data.prices['harris']['buy_no']}"
        )
        if changes.get('harris'):
            harris_value += f"\n📈 変動: {changes['harris']:+.1f}%"

        return {
            "title": "🗽 米大統領選2024 - 予測市場アップデート",
            "color": self.embed_color,
            "fields": [
                {
                    "name": "🔵 Donald Trump",
                    "value": trump_value,
                    "inline": True
                },
                {
                    "name": "🔴 Kamala Harris",
                    "value": harris_value,
                    "inline": True
                }
            ],
            "footer": {
                "text": f"更新時刻: {data.get_formatted_time()}"
            }
        }

    def send_market_update(self, data: MarketData) -> None:
        """
        マーケットデータの更新を送信
        
        Args:
            data: 送信するMarketDataオブジェクト
        """
        embed = self._create_market_embed(data)
        payload = {
            "username": self.username,
            "avatar_url": self.avatar_url,
            "embeds": [embed]
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logging.info("Discord通知の送信に成功しました")
            self._last_data = data  # 最後に送信したデータを保存
        except Exception as e:
            logging.error(f"Discord通知の送信に失敗: {e}")

    def send_error(self, error_message: str) -> None:
        """
        エラーメッセージを送信
        
        Args:
            error_message: 送信するエラーメッセージ
        """
        embed = {
            "title": "⚠️ エラー発生",
            "description": error_message,
            "color": 0xFF0000,  # 赤色
            "footer": {
                "text": f"発生時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }

        payload = {
            "username": self.username,
            "avatar_url": self.avatar_url,
            "embeds": [embed]
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logging.info("エラー通知の送信に成功しました")
        except Exception as e:
            logging.error(f"エラー通知の送信に失敗: {e}")