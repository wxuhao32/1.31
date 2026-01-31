import requests
import json
import re
from typing import Dict, List, Optional
from datetime import datetime


class PriceFetcher:
    def __init__(self, config):
        self.gold_api_url = config.get('api', 'gold_api_url', fallback=None)
        self.gold_api_key = config.get('api', 'gold_api_key', fallback=None)
        self.fund_api_url = config.get('api', 'fund_api_url', fallback=None)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.use_sina_api = not self.gold_api_key
        self.sina_gold_url = 'https://hq.sinajs.cn/list=hf_GC'
        self.sina_silver_url = 'https://hq.sinajs.cn/list=hf_SI'
    
    def fetch_gold_silver_prices(self) -> Dict[str, Dict]:
        if self.use_sina_api:
            return self._fetch_from_sina()
        
        try:
            params = {}
            if self.gold_api_key:
                params['appkey'] = self.gold_api_key
            
            response = self.session.get(
                self.gold_api_url,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 0:
                return self._fetch_from_sina()
            
            result = {}
            for item in data.get('result', []):
                typename = item.get('typename', '')
                if '黄金' in typename:
                    result['gold'] = {
                        'name': typename,
                        'price': float(item.get('price', 0)),
                        'open_price': float(item.get('openingprice', 0)),
                        'high_price': float(item.get('maxprice', 0)),
                        'low_price': float(item.get('minprice', 0)),
                        'change_percent': item.get('changepercent', '0%'),
                        'update_time': item.get('updatetime', ''),
                        'type': item.get('type', '')
                    }
                elif '白银' in typename:
                    result['silver'] = {
                        'name': typename,
                        'price': float(item.get('price', 0)),
                        'open_price': float(item.get('openingprice', 0)),
                        'high_price': float(item.get('maxprice', 0)),
                        'low_price': float(item.get('minprice', 0)),
                        'change_percent': item.get('changepercent', '0%'),
                        'update_time': item.get('updatetime', ''),
                        'type': item.get('type', '')
                    }
            
            return result
            
        except requests.exceptions.Timeout:
            print('API 请求超时，将尝试使用新浪财经公共 API...')
            return self._fetch_from_sina()
        except requests.exceptions.ConnectionError:
            print('API 网络连接失败，将尝试使用新浪财经公共 API...')
            return self._fetch_from_sina()
        except json.JSONDecodeError:
            print('API 返回数据格式错误，将尝试使用新浪财经公共 API...')
            return self._fetch_from_sina()
        except Exception as e:
            print(f'获取贵金属价格失败: {str(e)}')
            print(f'将尝试使用新浪财经公共 API...')
            return self._fetch_from_sina()
    
    def _fetch_from_sina(self) -> Dict[str, Dict]:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://finance.sina.com.cn/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
            
            gold_response = self.session.get(self.sina_gold_url, headers=headers, timeout=10)
            gold_response.raise_for_status()
            
            gold_text = gold_response.text
            
            gold_match = re.search(r'var hq_str_hf_GC="([^"]+)"', gold_text)
            
            result = {}
            
            if gold_match:
                gold_data = gold_match.group(1).split(',')
                
                if len(gold_data) >= 14:
                            try:
                                current_price = float(gold_data[0]) if gold_data[0] else 0
                                open_price = float(gold_data[2]) if gold_data[2] else 0
                                high_price = float(gold_data[3]) if gold_data[3] else 0
                                low_price = float(gold_data[4]) if gold_data[4] else 0
                                change_percent = ((current_price - open_price) / open_price * 100) if open_price > 0 else 0
                                
                                result['gold'] = {
                                    'name': gold_data[13] if gold_data[13] else '国际黄金',
                                    'price': current_price,
                                    'open_price': open_price,
                                    'high_price': high_price,
                                    'low_price': low_price,
                                    'change_percent': f'{change_percent:.2f}%',
                                    'update_time': f"{gold_data[12]} {gold_data[6]}" if len(gold_data) >= 13 else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'type': 'sina',
                                    'source': '新浪财经公共API'
                                }
                            except (ValueError, IndexError) as e:
                                pass
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://finance.sina.com.cn/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
            
            silver_response = self.session.get(self.sina_silver_url, headers=headers, timeout=10)
            silver_response.raise_for_status()
            
            silver_text = silver_response.text
            
            silver_match = re.search(r'var hq_str_hf_SI="([^"]+)"', silver_text)
            
            if silver_match:
                silver_data = silver_match.group(1).split(',')
                
                if len(silver_data) >= 14:
                            try:
                                current_price = float(silver_data[0]) if silver_data[0] else 0
                                open_price = float(silver_data[2]) if silver_data[2] else 0
                                high_price = float(silver_data[3]) if silver_data[3] else 0
                                low_price = float(silver_data[4]) if silver_data[4] else 0
                                change_percent = ((current_price - open_price) / open_price * 100) if open_price > 0 else 0
                                
                                result['silver'] = {
                                    'name': silver_data[13] if silver_data[13] else '国际白银',
                                    'price': current_price,
                                    'open_price': open_price,
                                    'high_price': high_price,
                                    'low_price': low_price,
                                    'change_percent': f'{change_percent:.2f}%',
                                    'update_time': f"{silver_data[12]} {silver_data[6]}" if len(silver_data) >= 13 else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'type': 'sina',
                                    'source': '新浪财经公共API'
                                }
                            except (ValueError, IndexError) as e:
                                pass
            
            return result
            
        except Exception as e:
            raise Exception(f'所有 API 均获取失败: {str(e)}')
    
    def fetch_fund_data(self, fund_code: str) -> Optional[Dict]:
        try:
            url = f'{self.fund_api_url}/{fund_code}.js?rt={int(datetime.now().timestamp() * 1000)}'
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            content = response.text
            match = re.search(r'jsonpgz\((.*)\)', content)
            
            if not match:
                raise Exception('无法解析基金数据')
            
            data = json.loads(match.group(1))
            
            result = {
                'code': data.get('fundcode', ''),
                'name': data.get('name', ''),
                'net_value': float(data.get('dwjz', 0)),
                'estimated_value': float(data.get('gsz', 0)),
                'change_percent': float(data.get('gszzl', 0)),
                'update_time': data.get('gztime', '')
            }
            
            return result
            
        except requests.exceptions.Timeout:
            raise Exception(f'请求超时: 基金代码 {fund_code}')
        except requests.exceptions.ConnectionError:
            raise Exception(f'网络连接失败: 基金代码 {fund_code}')
        except json.JSONDecodeError:
            raise Exception(f'基金数据格式错误: 基金代码 {fund_code}')
        except Exception as e:
            raise Exception(f'获取基金数据失败 {fund_code}: {str(e)}')
    
    def fetch_multiple_funds(self, fund_codes: List[str]) -> Dict[str, Dict]:
        results = {}
        
        for fund_code in fund_codes:
            try:
                fund_data = self.fetch_fund_data(fund_code)
                if fund_data:
                    results[fund_code] = fund_data
            except Exception as e:
                results[fund_code] = {
                    'error': str(e),
                    'code': fund_code
                }
        
        return results
    
    def close(self):
        self.session.close()
