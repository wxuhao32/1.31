import os
import sys
import json
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from modules.config_manager import ConfigManager
from modules.price_fetcher import PriceFetcher
from modules.data_processor import DataProcessor
from modules.logger import logger_instance
from modules.exchange_rate_manager import ExchangeRateManager
from modules.display import DisplayFormatter


class MarketAPIServer:
    def __init__(self, host=None, port=None):
        self.app = Flask(__name__)
        self.app.config['JSON_AS_ASCII'] = False
        CORS(self.app)
        
        @self.app.after_request
        def add_headers(response):
            if request.path.endswith('.js'):
                response.headers['Content-Type'] = 'application/javascript'
            elif request.path.endswith('.json'):
                response.headers['Content-Type'] = 'application/manifest+json'
            return response
        
        self.host = host or os.getenv('HOST', '0.0.0.0')
        self.port = port or int(os.getenv('PORT', '5000'))
        
        self._setup_directories()
        self._init_components()
        self._setup_routes()
    
    def _setup_directories(self):
        directories = ['logs', 'data', 'config', 'frontend', 'mobile-app']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def _init_components(self):
        config_path = os.path.join('config', 'config.ini')
        fund_list_path = os.path.join('config', 'fund_list.txt')
        email_list_path = os.path.join('config', 'email_list.txt')
        
        self.config_manager = ConfigManager(config_path, fund_list_path, email_list_path, logger_instance)
        self.config = self.config_manager.get_config()
        
        self.price_fetcher = PriceFetcher(self.config)
        self.data_processor = DataProcessor(logger_instance)
        
        history_file = os.path.join('data', 'price_history.json')
        if os.path.exists(history_file):
            self.data_processor.load_history_from_file(history_file)
        
        self.exchange_rate_manager = ExchangeRateManager(logger_instance)
        DisplayFormatter.set_exchange_rate_manager(self.exchange_rate_manager)
        
        self.logger = logger_instance
    
    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return send_from_directory('frontend', 'index.html')
        
        @self.app.route('/<path:filename>')
        def serve_static(filename):
            return send_from_directory('frontend', filename)
        
        @self.app.route('/manifest.json')
        def serve_manifest():
            manifest_path = os.path.join('frontend', 'manifest.json')
            return send_from_directory('frontend', 'manifest.json')
        
        @self.app.route('/sw.js')
        def serve_sw():
            return send_from_directory('frontend', 'sw.js')
        
        # Market Data APIs
        @self.app.route('/api/market/precious-metals')
        def get_precious_metals():
            try:
                raw_data = self.price_fetcher.fetch_gold_silver_prices()
                processed = self.data_processor.process_gold_silver_data(raw_data)
                return jsonify({
                    'success': True,
                    'data': processed,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/market/funds')
        def get_funds():
            try:
                fund_codes = self.config_manager.get_fund_codes()
                if not fund_codes:
                    return jsonify({
                        'success': True,
                        'data': {},
                        'message': '未配置基金代码',
                        'timestamp': datetime.now().isoformat()
                    })
                
                raw_data = self.price_fetcher.fetch_multiple_funds(fund_codes)
                processed = self.data_processor.process_fund_data(raw_data)
                
                return jsonify({
                    'success': True,
                    'data': processed,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/market/history/<asset_type>')
        def get_history(asset_type):
            try:
                history = self.data_processor.price_history
                
                if asset_type == 'gold':
                    data = history.get('gold', [])
                elif asset_type == 'silver':
                    data = history.get('silver', [])
                elif asset_type == 'funds':
                    data = history.get('funds', {})
                else:
                    return jsonify({
                        'success': False,
                        'error': '无效的资源类型'
                    }), 400
                
                return jsonify({
                    'success': True,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/market/fund-history/<fund_code>')
        def get_fund_history(fund_code):
            try:
                history = self.data_processor.price_history
                fund_history = history.get('funds', {}).get(fund_code, [])
                
                return jsonify({
                    'success': True,
                    'data': fund_history,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/market/fund/<fund_code>')
        def get_single_fund(fund_code):
            try:
                raw_data = self.price_fetcher.fetch_multiple_funds([fund_code])
                processed = self.data_processor.process_fund_data(raw_data)
                
                if fund_code in processed:
                    return jsonify({
                        'success': True,
                        'data': processed[fund_code],
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '基金数据获取失败',
                        'timestamp': datetime.now().isoformat()
                    }), 404
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        # Config APIs
        @self.app.route('/api/config/funds')
        def get_fund_codes():
            try:
                fund_codes = self.config_manager.get_fund_codes()
                return jsonify({
                    'success': True,
                    'data': fund_codes,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/config/funds', methods=['POST'])
        def add_fund_code():
            try:
                data = request.get_json()
                fund_code = data.get('code', '').strip()
                
                if not fund_code:
                    return jsonify({
                        'success': False,
                        'error': '基金代码不能为空'
                    }), 400
                
                success = self.config_manager.add_fund_code(fund_code)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'基金代码 {fund_code} 添加成功',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '基金代码添加失败',
                        'timestamp': datetime.now().isoformat()
                    }), 500
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/config/funds/<fund_code>', methods=['DELETE'])
        def delete_fund_code(fund_code):
            try:
                # 暂未实现删除功能，返回成功消息
                return jsonify({
                    'success': True,
                    'message': f'基金代码 {fund_code} 删除功能待实现',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        # Alert Configuration APIs
        @self.app.route('/api/alert/config')
        def get_alert_config():
            try:
                config = {
                    'gold_threshold': self.config.getfloat('gold', 'price_threshold_gold'),
                    'silver_threshold': self.config.getfloat('gold', 'price_threshold_silver'),
                    'fund_threshold': self.config.getfloat('fund', 'change_percent_threshold'),
                    'enable_gold_monitor': self.config.getboolean('gold', 'enable_monitor'),
                    'enable_fund_monitor': self.config.getboolean('fund', 'enable_monitor'),
                    'alert_cooldown': self.config.getint('gold', 'alert_cooldown_minutes'),
                    'recipients': self.config_manager.get_email_list()
                }
                return jsonify({
                    'success': True,
                    'data': config,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/alert/config', methods=['PUT'])
        def update_alert_config():
            try:
                data = request.get_json()
                
                gold_threshold = data.get('gold_threshold')
                silver_threshold = data.get('silver_threshold')
                fund_threshold = data.get('fund_threshold')
                enable_gold_monitor = data.get('enable_gold_monitor')
                enable_fund_monitor = data.get('enable_fund_monitor')
                alert_cooldown = data.get('alert_cooldown')
                
                if gold_threshold is not None:
                    self.config.set('gold', 'price_threshold_gold', str(float(gold_threshold)))
                if silver_threshold is not None:
                    self.config.set('gold', 'price_threshold_silver', str(float(silver_threshold)))
                if fund_threshold is not None:
                    self.config.set('fund', 'change_percent_threshold', str(float(fund_threshold)))
                if enable_gold_monitor is not None:
                    self.config.set('gold', 'enable_monitor', str(bool(enable_gold_monitor)))
                if enable_fund_monitor is not None:
                    self.config.set('fund', 'enable_monitor', str(bool(enable_fund_monitor)))
                if alert_cooldown is not None:
                    self.config.set('gold', 'alert_cooldown_minutes', str(int(alert_cooldown)))
                
                with open(os.path.join('config', 'config.ini'), 'w', encoding='utf-8') as f:
                    self.config.write(f)
                
                return jsonify({
                    'success': True,
                    'message': '预警配置更新成功',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/alert/recipients', methods=['POST'])
        def add_recipient():
            try:
                data = request.get_json()
                email = data.get('email', '').strip()
                
                if not email:
                    return jsonify({
                        'success': False,
                        'error': '邮箱地址不能为空'
                    }), 400
                
                success = self.config_manager.add_email_address(email)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'邮箱 {email} 添加成功',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '邮箱添加失败',
                        'timestamp': datetime.now().isoformat()
                    }), 500
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/alert/recipients/<email>', methods=['DELETE'])
        def delete_recipient(email):
            try:
                success = self.config_manager.remove_email_address(email)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'邮箱 {email} 删除成功',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '邮箱删除失败',
                        'timestamp': datetime.now().isoformat()
                    }), 500
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/alert/test-email', methods=['POST'])
        def send_test_email():
            try:
                from modules.email_notifier import EmailNotifier
                
                data = request.get_json()
                recipient = data.get('recipient', '').strip()
                
                if not recipient:
                    return jsonify({
                        'success': False,
                        'error': '收件人邮箱不能为空'
                    }), 400
                
                email_notifier = EmailNotifier(self.config, self.logger)
                result = email_notifier.send_test_email(recipient)
                
                if result:
                    return jsonify({
                        'success': True,
                        'message': '测试邮件发送成功',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '测试邮件发送失败',
                        'timestamp': datetime.now().isoformat()
                    }), 500
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/alert/history')
        def get_alert_history():
            try:
                hours = request.args.get('hours', 24, type=int)
                history = self.logger.get_alert_history(hours)
                
                return jsonify({
                    'success': True,
                    'data': history,
                    'count': len(history),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        # Exchange Rate APIs
        @self.app.route('/api/exchange/rate')
        def get_exchange_rate():
            try:
                force_refresh = request.args.get('refresh', 'false').lower() == 'true'
                rate = self.exchange_rate_manager.get_rate(force_refresh)
                rate_info = self.exchange_rate_manager.get_rate_info()
                
                return jsonify({
                    'success': True,
                    'data': {
                        'rate': rate,
                        'info': rate_info
                    },
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/exchange/refresh', methods=['POST'])
        def refresh_exchange_rate():
            try:
                success = self.exchange_rate_manager.refresh_now()
                if success:
                    rate_info = self.exchange_rate_manager.get_rate_info()
                    return jsonify({
                        'success': True,
                        'message': '汇率刷新成功',
                        'data': rate_info,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '汇率刷新失败，请检查网络连接',
                        'timestamp': datetime.now().isoformat()
                    }), 500
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/exchange/convert')
        def convert_currency():
            try:
                price = request.args.get('price', type=float)
                direction = request.args.get('direction', 'usd_oz_to_cny_gram')
                
                if price is None:
                    return jsonify({
                        'success': False,
                        'error': '缺少价格参数',
                        'timestamp': datetime.now().isoformat()
                    }), 400
                
                if direction == 'usd_oz_to_cny_gram':
                    result = self.exchange_rate_manager.convert_usd_oz_to_cny_gram(price)
                elif direction == 'cny_gram_to_usd_oz':
                    result = self.exchange_rate_manager.convert_cny_gram_to_usd_oz(price)
                else:
                    return jsonify({
                        'success': False,
                        'error': f'不支持的转换方向: {direction}',
                        'timestamp': datetime.now().isoformat()
                    }), 400
                
                rate_info = self.exchange_rate_manager.get_rate_info()
                
                return jsonify({
                    'success': True,
                    'data': {
                        'input': price,
                        'output': result,
                        'direction': direction,
                        'exchange_rate': rate_info
                    },
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/exchange/validate')
        def validate_exchange_rate():
            try:
                test_cases = {
                    'test_1': (2000.0, 7.2, 1.0),
                    'test_2': (1950.0, 7.3, 1.0),
                    'test_3': (2050.0, 7.1, 1.0),
                    'test_4': (1900.0, 7.25, 1.0),
                    'test_5': (2100.0, 7.15, 1.0)
                }
                
                results = self.exchange_rate_manager.validate_conversion(test_cases)
                
                return jsonify({
                    'success': True,
                    'data': results,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        # System APIs
        @self.app.route('/api/health')
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/info')
        def get_info():
            return jsonify({
                'name': '金融价格监控系统',
                'version': '1.0.0',
                'api_version': 'v1',
                'timestamp': datetime.now().isoformat()
            })
    
    def run(self):
        self.logger.log_info(f'API服务器启动 - http://{self.host}:{self.port}')
        self.logger.log_info('按 Ctrl+C 停止服务器')
        try:
            self.app.run(host=self.host, port=self.port, debug=False, threaded=True)
        except KeyboardInterrupt:
            self.logger.log_info('API服务器已停止')
        finally:
            self.price_fetcher.close()
            self.data_processor.save_history_to_file(os.path.join('data', 'price_history.json'))


def main():
    server = MarketAPIServer(host='0.0.0.0', port=5000)
    server.run()


app = MarketAPIServer().app


if __name__ == '__main__':
    main()
