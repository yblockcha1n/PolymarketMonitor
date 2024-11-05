import configparser
import os
from typing import Any, Dict
import logging

class ConfigLoader:
    """設定ファイルを読み込むクラス"""

    def __init__(self, config_path: str = 'config/config.ini'):
        """
        初期化
        
        Args:
            config_path: 設定ファイルのパス
        """
        self.config = configparser.ConfigParser()
        self.config_path = config_path
        self._load_config()

    def _load_config(self) -> None:
        """設定ファイルの読み込み"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_path}")
            
        try:
            self.config.read(self.config_path, encoding='utf-8')
            logging.info(f"設定ファイルを読み込みました: {self.config_path}")
        except Exception as e:
            raise Exception(f"設定ファイルの読み込みに失敗: {e}")

    def get_scraper_config(self) -> Dict[str, Any]:
        """
        スクレイパーの設定を取得
        
        Returns:
            Dict[str, Any]: スクレイパーの設定
        """
        return {
            'headless': self.config.getboolean('scraper', 'headless'),
            'retry_count': self.config.getint('scraper', 'retry_count'),
            'wait_time': self.config.getint('scraper', 'wait_time'),
            'poll_interval': self.config.getint('scraper', 'poll_interval')
        }

    def get_discord_config(self) -> Dict[str, str]:
        """
        Discord通知の設定を取得
        
        Returns:
            Dict[str, str]: Discord関連の設定
        """
        return dict(self.config['discord'])

    def get_logging_config(self) -> Dict[str, str]:
        """
        ログの設定を取得
        
        Returns:
            Dict[str, str]: ログ関連の設定
        """
        return dict(self.config['logging'])

    def get_monitoring_config(self) -> Dict[str, float]:
        """
        監視の設定を取得
        
        Returns:
            Dict[str, float]: 監視関連の設定
        """
        return {
            'alert_threshold': self.config.getfloat('monitoring', 'alert_threshold')
        }