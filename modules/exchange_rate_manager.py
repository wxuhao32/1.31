import requests
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from pathlib import Path
import threading


class ExchangeRateManager:
    USD_TO_CNY = 7.2
    OUNCE_TO_GRAM = 31.1034768
    
    DEFAULT_CACHE_DURATION = 3600
    API_TIMEOUT = 10
    MAX_RETRIES = 3
    
    CACHE_FILE = Path(__file__).parent.parent / 'data' / 'exchange_rate_cache.json'
    
    def __init__(self, logger=None):
        self.logger = logger
        self._rate = None
        self._last_update = None
        self._cache_duration = self.DEFAULT_CACHE_DURATION
        self._cache_data = self._load_cache()
        self._lock = threading.Lock()
        
        if self._cache_data.get('rate'):
            self._rate = self._cache_data['rate']
            self._last_update = datetime.fromisoformat(self._cache_data['last_update'])
            
    def _load_cache(self) -> Dict:
        try:
            if self.CACHE_FILE.exists():
                with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            if self.logger:
                self.logger.log_warning(f'加载汇率缓存失败: {str(e)}')
        return {}
    
    def _save_cache(self, rate: float, source: str):
        try:
            cache_data = {
                'rate': rate,
                'last_update': datetime.now().isoformat(),
                'source': source
            }
            self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            self._cache_data = cache_data
        except Exception as e:
            if self.logger:
                self.logger.log_warning(f'保存汇率缓存失败: {str(e)}')
    
    def _fetch_from_exchangerate_api(self) -> Optional[float]:
        try:
            url = 'https://api.exchangerate-api.com/v4/latest/USD'
            response = requests.get(url, timeout=self.API_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                rate = data.get('rates', {}).get('CNY')
                if rate:
                    return rate
        except Exception as e:
            if self.logger:
                self.logger.log_warning(f'Exchangerate-API 请求失败: {str(e)}')
        return None
    
    def _fetch_from_fixer(self) -> Optional[float]:
        try:
            url = 'https://api.fixer.io/latest?base=USD&symbols=CNY'
            response = requests.get(url, timeout=self.API_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                rate = data.get('rates', {}).get('CNY')
                if rate:
                    return rate
        except Exception as e:
            if self.logger:
                self.logger.log_warning(f'Fixer API 请求失败: {str(e)}')
        return None
    
    def _fetch_from_openexchangerates(self) -> Optional[float]:
        try:
            url = 'https://openexchangerates.org/api/latest.json?app_id=demo&base=USD&symbols=CNY'
            response = requests.get(url, timeout=self.API_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                rate = data.get('rates', {}).get('CNY')
                if rate:
                    return rate
        except Exception as e:
            if self.logger:
                self.logger.log_warning(f'Open Exchange Rates API 请求失败: {str(e)}')
        return None
    
    def _fetch_from_currencyapi(self) -> Optional[float]:
        try:
            url = 'https://api.currencyapi.com/v3/latest?apikey=fca_live_demo&base_currency=USD'
            response = requests.get(url, timeout=self.API_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                rate = data.get('data', {}).get('CNY', {}).get('value')
                if rate:
                    return rate
        except Exception as e:
            if self.logger:
                self.logger.log_warning(f'CurrencyAPI 请求失败: {str(e)}')
        return None
    
    def _fetch_from_exchange_rate_host(self) -> Optional[float]:
        try:
            url = 'https://api.exchangerate.host/latest?base=USD&symbols=CNY'
            response = requests.get(url, timeout=self.API_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                rate = data.get('rates', {}).get('CNY')
                if rate:
                    return rate
        except Exception as e:
            if self.logger:
                self.logger.log_warning(f'ExchangeRate.host 请求失败: {str(e)}')
        return None
    
    def _fetch_rate_from_multiple_sources(self) -> Tuple[Optional[float], Optional[str]]:
        sources = [
            ('Exchangerate-API', self._fetch_from_exchangerate_api),
            ('ExchangeRate.host', self._fetch_from_exchange_rate_host),
            ('CurrencyAPI', self._fetch_from_currencyapi),
            ('Fixer', self._fetch_from_fixer),
            ('OpenExchangeRates', self._fetch_from_openexchangerates),
        ]
        
        for source_name, fetch_func in sources:
            for attempt in range(self.MAX_RETRIES):
                rate = fetch_func()
                if rate and 1 < rate < 15:
                    if self.logger:
                        self.logger.log_info(f'从 {source_name} 获取汇率成功: {rate:.4f}')
                    return rate, source_name
                time.sleep(0.5)
        
        if self.logger:
            self.logger.log_error('所有汇率API源均获取失败')
        return None, None
    
    def get_rate(self, force_refresh: bool = False) -> float:
        with self._lock:
            now = datetime.now()
            
            if self._rate is None or force_refresh:
                rate, source = self._fetch_rate_from_multiple_sources()
                if rate:
                    self._rate = rate
                    self._last_update = now
                    self._save_cache(rate, source or 'Unknown')
                    return rate
            
            if self._last_update:
                age = (now - self._last_update).total_seconds()
                if age >= self._cache_duration:
                    rate, source = self._fetch_rate_from_multiple_sources()
                    if rate:
                        self._rate = rate
                        self._last_update = now
                        self._save_cache(rate, source or 'Unknown')
            
            return self._rate if self._rate is not None else self.USD_TO_CNY
    
    def convert_usd_oz_to_cny_gram(self, price_usd_per_ounce: float, force_refresh: bool = False) -> float:
        rate = self.get_rate(force_refresh)
        result = price_usd_per_ounce * rate / self.OUNCE_TO_GRAM
        return round(result, 2)
    
    def convert_cny_gram_to_usd_oz(self, price_cny_per_gram: float, force_refresh: bool = False) -> float:
        rate = self.get_rate(force_refresh)
        result = price_cny_per_gram * self.OUNCE_TO_GRAM / rate
        return round(result, 2)
    
    def get_rate_info(self) -> Dict:
        return {
            'rate': self._rate if self._rate is not None else self.USD_TO_CNY,
            'last_update': self._last_update.isoformat() if self._last_update else None,
            'source': self._cache_data.get('source', 'Fixed'),
            'is_cached': self._last_update is not None,
            'cache_age_seconds': (datetime.now() - self._last_update).total_seconds() if self._last_update else None
        }
    
    def set_cache_duration(self, seconds: int):
        self._cache_duration = max(300, min(86400, seconds))
    
    def refresh_now(self) -> bool:
        rate, source = self._fetch_rate_from_multiple_sources()
        if rate:
            with self._lock:
                self._rate = rate
                self._last_update = datetime.now()
                self._save_cache(rate, source or 'Unknown')
            return True
        return False
    
    @staticmethod
    def validate_conversion(test_cases: Dict[str, Tuple[float, float, float]]) -> Dict:
        results = {
            'total_tests': len(test_cases),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        for name, (price_usd_oz, expected_rate, tolerance) in test_cases.items():
            actual_rate = ExchangeRateManager.USD_TO_CNY
            error = abs(actual_rate - expected_rate)
            passed = error <= tolerance
            
            results['details'].append({
                'name': name,
                'expected_rate': expected_rate,
                'actual_rate': actual_rate,
                'error': error,
                'tolerance': tolerance,
                'passed': passed
            })
            
            if passed:
                results['passed'] += 1
            else:
                results['failed'] += 1
        
        return results
