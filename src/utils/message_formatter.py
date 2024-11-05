from typing import Dict
from models.market_data import MarketData

class MessageFormatter:
    """通知メッセージのフォーマットを行うクラス"""

    @staticmethod
    def format_market_data(data: MarketData) -> str:
        """
        マーケットデータを文字列にフォーマット
        
        Args:
            data: MarketDataオブジェクト
            
        Returns:
            str: フォーマットされた文字列
        """
        return (
            f"📊 予測市場の状況 ({data.get_formatted_time()})\n\n"
            f"🔵 Donald Trump:\n"
            f"確率: {data.probabilities['trump']}\n"
            f"取引量: {data.volumes['trump']}\n"
            f"買値(Yes): {data.prices['trump']['buy_yes']}\n"
            f"買値(No): {data.prices['trump']['buy_no']}\n\n"
            f"🔴 Kamala Harris:\n"
            f"確率: {data.probabilities['harris']}\n"
            f"取引量: {data.volumes['harris']}\n"
            f"買値(Yes): {data.prices['harris']['buy_yes']}\n"
            f"買値(No): {data.prices['harris']['buy_no']}"
        )

    @staticmethod
    def format_error(error_message: str) -> str:
        """
        エラーメッセージをフォーマット
        
        Args:
            error_message: エラーメッセージ
            
        Returns:
            str: フォーマットされたエラーメッセージ
        """
        return f"⚠️ エラーが発生しました\n{error_message}"

    @staticmethod
    def format_price_changes(changes: Dict[str, float], threshold: float) -> str:
        """
        価格変動メッセージをフォーマット
        
        Args:
            changes: 価格変動データ
            threshold: アラートの閾値
            
        Returns:
            str: フォーマットされた価格変動メッセージ
        """
        messages = []
        for candidate, change in changes.items():
            if abs(change) >= threshold:
                direction = "上昇" if change > 0 else "下落"
                messages.append(
                    f"📈 {candidate.title()}の確率が{abs(change):.1f}%{direction}しました"
                )
        
        return "\n".join(messages) if messages else ""