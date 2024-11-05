import logging
import time
from typing import Optional
import sys
import os
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.scraper.polymarket_scraper import PolymarketScraper
from src.notifications.discord_notifier import DiscordNotifier
from src.utils.config_loader import ConfigLoader
from src.utils.message_formatter import MessageFormatter

def setup_logging(config: dict) -> None:
    """
    ログ設定のセットアップ
    
    Args:
        config: ログ設定
    """
    log_dir = os.path.dirname(config['file_path'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=config['level'],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config['file_path'], encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def run_monitor(scraper_config: dict, notifier: DiscordNotifier) -> None:
    """
    モニタリングの実行
    
    Args:
        scraper_config: スクレイパーの設定
        notifier: 通知クライアント
    """
    with PolymarketScraper(
        headless=scraper_config['headless'],
        retry_count=scraper_config['retry_count'],
        wait_time=scraper_config['wait_time']
    ) as scraper:
        data = scraper.get_market_data()
        if data:
            notifier.send_market_update(data)
        else:
            notifier.send_error("マーケットデータの取得に失敗しました")

def main():
    """メイン実行関数"""
    try:
        config = ConfigLoader()
        scraper_config = config.get_scraper_config()
        discord_config = config.get_discord_config()
        setup_logging(config.get_logging_config())
        
        notifier = DiscordNotifier(discord_config)
        
        logging.info("モニタリングを開始します")
        
        notifier.send_error("🚀 モニタリングを開始しました")
        
        while True:
            try:
                run_monitor(scraper_config, notifier)
            except Exception as e:
                error_message = f"予期せぬエラーが発生: {e}"
                logging.error(error_message)
                notifier.send_error(error_message)
            
            # 次の実行まで待機
            time.sleep(scraper_config['poll_interval'])

    except Exception as e:
        print(f"致命的なエラーが発生しました: {e}")
        logging.critical(f"致命的なエラーが発生: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()