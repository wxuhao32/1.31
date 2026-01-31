from typing import Dict, List
from datetime import datetime
import json


class DataProcessor:
    def __init__(self, logger):
        self.logger = logger
        self.price_history = {
            'gold': [],
            'silver': [],
            'funds': {}
        }
        self.max_history_length = 1000
    
    def process_gold_silver_data(self, raw_data: Dict[str, Dict]) -> Dict[str, Dict]:
        processed = {}
        
        for metal, data in raw_data.items():
            processed[metal] = {
                'name': data['name'],
                'current_price': data['price'],
                'open_price': data['open_price'],
                'high_price': data['high_price'],
                'low_price': data['low_price'],
                'change_percent_str': data['change_percent'],
                'change_percent': self._parse_change_percent(data['change_percent']),
                'update_time': data['update_time'],
                'timestamp': datetime.now().isoformat()
            }
            
            self._update_price_history(metal, processed[metal])
        
        return processed
    
    def process_fund_data(self, raw_data: Dict[str, Dict]) -> Dict[str, Dict]:
        processed = {}
        
        for fund_code, data in raw_data.items():
            if 'error' in data:
                processed[fund_code] = {
                    'error': data['error'],
                    'code': fund_code
                }
                continue
            
            processed[fund_code] = {
                'code': data['code'],
                'name': data['name'],
                'net_value': data['net_value'],
                'estimated_value': data['estimated_value'],
                'change_percent': data['change_percent'],
                'update_time': data['update_time'],
                'timestamp': datetime.now().isoformat()
            }
            
            self._update_fund_history(fund_code, processed[fund_code])
        
        return processed
    
    def _parse_change_percent(self, change_percent_str: str) -> float:
        try:
            return float(change_percent_str.replace('%', ''))
        except (ValueError, AttributeError):
            return 0.0
    
    def _update_price_history(self, metal: str, data: Dict):
        if metal not in self.price_history:
            self.price_history[metal] = []
        
        history_entry = {
            'price': data['current_price'],
            'change_percent': data['change_percent'],
            'timestamp': data['timestamp']
        }
        
        self.price_history[metal].append(history_entry)
        
        if len(self.price_history[metal]) > self.max_history_length:
            self.price_history[metal] = self.price_history[metal][-self.max_history_length:]
    
    def _update_fund_history(self, fund_code: str, data: Dict):
        if fund_code not in self.price_history['funds']:
            self.price_history['funds'][fund_code] = []
        
        history_entry = {
            'estimated_value': data['estimated_value'],
            'change_percent': data['change_percent'],
            'timestamp': data['timestamp']
        }
        
        self.price_history['funds'][fund_code].append(history_entry)
        
        if len(self.price_history['funds'][fund_code]) > self.max_history_length:
            self.price_history['funds'][fund_code] = self.price_history['funds'][fund_code][-self.max_history_length:]
    
    def calculate_price_change(self, metal: str) -> Dict:
        if metal not in self.price_history or len(self.price_history[metal]) < 2:
            return {
                'price_change': 0.0,
                'percent_change': 0.0,
                'previous_price': None
            }
        
        history = self.price_history[metal]
        current = history[-1]
        previous = history[0]
        
        price_change = current['price'] - previous['price']
        if previous['price'] > 0:
            percent_change = (price_change / previous['price']) * 100
        else:
            percent_change = 0.0
        
        return {
            'price_change': price_change,
            'percent_change': percent_change,
            'previous_price': previous['price']
        }
    
    def get_latest_price(self, metal: str) -> float:
        if metal not in self.price_history or not self.price_history[metal]:
            return 0.0
        return self.price_history[metal][-1]['price']
    
    def get_fund_latest_value(self, fund_code: str) -> float:
        if fund_code not in self.price_history['funds'] or not self.price_history['funds'][fund_code]:
            return 0.0
        return self.price_history['funds'][fund_code][-1]['estimated_value']
    
    def get_fund_latest_change(self, fund_code: str) -> float:
        if fund_code not in self.price_history['funds'] or not self.price_history['funds'][fund_code]:
            return 0.0
        return self.price_history['funds'][fund_code][-1]['change_percent']
    
    def save_history_to_file(self, filepath: str):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.price_history, f, ensure_ascii=False, indent=2)
            self.logger.log_info(f'价格历史数据已保存到 {filepath}')
        except Exception as e:
            self.logger.log_error(f'保存历史数据失败: {str(e)}')
    
    def load_history_from_file(self, filepath: str):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.price_history = json.load(f)
            self.logger.log_info(f'价格历史数据已从 {filepath} 加载')
        except FileNotFoundError:
            self.logger.log_info(f'历史数据文件不存在，将创建新的记录')
        except Exception as e:
            self.logger.log_error(f'加载历史数据失败: {str(e)}')
            self.price_history = {
                'gold': [],
                'silver': [],
                'funds': {}
            }
    
    def clear_old_history(self, days: int = 30):
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for metal in ['gold', 'silver']:
            self.price_history[metal] = [
                entry for entry in self.price_history[metal]
                if datetime.fromisoformat(entry['timestamp']).timestamp() > cutoff_time
            ]
        
        for fund_code in list(self.price_history['funds'].keys()):
            self.price_history['funds'][fund_code] = [
                entry for entry in self.price_history['funds'][fund_code]
                if datetime.fromisoformat(entry['timestamp']).timestamp() > cutoff_time
            ]
        
        self.logger.log_info(f'已清除 {days} 天前的历史数据')
