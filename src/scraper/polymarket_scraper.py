from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from typing import Optional, Any
import time
import logging
from webdriver_manager.chrome import ChromeDriverManager
from models.market_data import MarketData

class PolymarketScraper:
    """Polymarket.comからデータを取得するスクレイパークラス"""

    def __init__(self, headless: bool = True, retry_count: int = 3, wait_time: int = 2):
        """
        スクレイパーの初期化
        
        Args:
            headless: ヘッドレスモードを使用するかどうか（デフォルト：True）
            retry_count: リトライ回数（デフォルト：3）
            wait_time: リトライ間の待機時間（秒）（デフォルト：2）
        """
        self.retry_count = retry_count
        self.wait_time = wait_time
        self.options = self._setup_chrome_options(headless)

    def _setup_chrome_options(self, headless: bool) -> Options:
        """Chrome用のオプションを設定"""
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        return options

    def setup_driver(self) -> None:
        """ChromeDriverのセットアップ"""
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            logging.info("ChromeDriverのセットアップに成功しました")
        except Exception as e:
            logging.error(f"ChromeDriverのセットアップに失敗: {e}")
            raise

    def __enter__(self):
        """コンテキストマネージャーのエントリー"""
        retry_count = 0
        while retry_count < self.retry_count:
            try:
                self.setup_driver()
                return self
            except Exception as e:
                retry_count += 1
                logging.warning(f"セットアップ試行 {retry_count} 回目が失敗: {e}")
                time.sleep(self.wait_time)
                
                if retry_count == self.retry_count:
                    raise Exception("最大リトライ回数を超えて初期化に失敗しました")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """リソースの解放"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
                logging.info("ChromeDriverを正常に終了しました")
        except Exception as e:
            logging.error(f"ChromeDriverの終了時にエラーが発生: {e}")

    def wait_and_get_element(self, selector: str, timeout: int = 10) -> Optional[Any]:
        """
        要素の待機と取得
        
        Args:
            selector: CSSセレクター
            timeout: タイムアウト時間（秒）
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except TimeoutException:
            logging.warning(f"要素の待機がタイムアウト: {selector}")
            return None

    def get_market_data(self) -> Optional[MarketData]:
        """マーケットデータの取得"""
        try:
            url = "https://polymarket.com/event/presidential-election-winner-2024"
            self.driver.get(url)
            logging.info(f"URLにアクセス: {url}")
            
            # 主要要素の待機
            self.wait_and_get_element("div.c-dhzjXW-ieIsjBe-css")
            time.sleep(2)  # 動的コンテンツの待機
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 各種データの取得
            probability_elements = soup.select("div.c-dhzjXW-ieIsjBe-css p.c-dqzIym-icEtPXM-css")
            volume_elements = soup.select("p.c-dqzIym-ihVLOVM-css")
            price_elements = soup.select("div.c-gBrBnR")
            
            # データの存在確認
            if not all([probability_elements, volume_elements, price_elements]):
                logging.error("必要なデータ要素が見つかりません")
                return None
            
            # MarketDataオブジェクトの作成
            market_data = MarketData(
                probabilities={
                    'trump': probability_elements[0].text if len(probability_elements) > 0 else 'N/A',
                    'harris': probability_elements[1].text if len(probability_elements) > 1 else 'N/A'
                },
                volumes={
                    'trump': volume_elements[0].text if len(volume_elements) > 0 else 'N/A',
                    'harris': volume_elements[1].text if len(volume_elements) > 1 else 'N/A'
                },
                prices={
                    'trump': {
                        'buy_yes': price_elements[0].text if len(price_elements) > 0 else 'N/A',
                        'buy_no': price_elements[1].text if len(price_elements) > 1 else 'N/A'
                    },
                    'harris': {
                        'buy_yes': price_elements[2].text if len(price_elements) > 2 else 'N/A',
                        'buy_no': price_elements[3].text if len(price_elements) > 3 else 'N/A'
                    }
                }
            )
            
            logging.info("マーケットデータの取得に成功しました")
            return market_data
            
        except Exception as e:
            logging.error(f"マーケットデータの取得中にエラーが発生: {e}")
            if hasattr(self, 'driver'):
                logging.error(f"現在のURL: {self.driver.current_url}")
            return None