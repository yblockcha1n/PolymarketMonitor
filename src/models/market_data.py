from dataclasses import dataclass
from typing import Dict
import time
from datetime import datetime

@dataclass
class MarketData:
    """マーケットデータを格納するデータクラス"""
    probabilities: Dict[str, str]  # 確率データ
    volumes: Dict[str, str]        # 取引量データ
    prices: Dict[str, Dict[str, str]]  # 価格データ
    timestamp: float = time.time()   # タイムスタンプ

    def get_formatted_time(self) -> str:
        """タイムスタンプを読みやすい形式に変換"""
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def get_price_changes(self, previous_data: 'MarketData') -> Dict[str, float]:
        """
        前回のデータと比較して価格変動を計算
        
        Args:
            previous_data: 前回のMarketData
            
        Returns:
            Dict[str, float]: 各候補の価格変動率（%）
        """
        try:
            changes = {}
            for candidate in ['trump', 'harris']:
                current = float(self.probabilities[candidate].rstrip('%'))
                previous = float(previous_data.probabilities[candidate].rstrip('%'))
                changes[candidate] = current - previous
            return changes
        except (ValueError, KeyError):
            return {'trump': 0.0, 'harris': 0.0}

    def to_dict(self) -> Dict:
        """データクラスを辞書形式に変換"""
        return {
            'probabilities': self.probabilities,
            'volumes': self.volumes,
            'prices': self.prices,
            'timestamp': self.timestamp
        }