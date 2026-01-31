import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class FinancialMonitorLogger:
    _instance = None
    
    def __new__(cls, log_dir='logs'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, log_dir='logs'):
        if self._initialized:
            return
            
        self.log_dir = log_dir
        self.alert_history = []
        self._ensure_log_dir()
        self._setup_logger()
        self._initialized = True
    
    def _ensure_log_dir(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _setup_logger(self):
        self.logger = logging.getLogger('FinancialMonitor')
        self.logger.setLevel(logging.INFO)
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        file_handler = RotatingFileHandler(
            os.path.join(self.log_dir, f'monitor_{date_str}.log'),
            maxBytes=100*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
    
    def log_price_update(self, asset_type, asset_name, current_price, change_percent=None):
        if change_percent is not None:
            self.logger.info(f'{asset_type}价格更新 - {asset_name}: 当前价格 {current_price}, 涨跌幅 {change_percent}%')
        else:
            self.logger.info(f'{asset_type}价格更新 - {asset_name}: 当前价格 {current_price}')
    
    def log_alert_triggered(self, alert_type, asset_name, alert_info):
        self.logger.warning(f'预警触发 - {alert_type}: {asset_name} - {alert_info}')
    
    def log_email_sent(self, recipients, subject):
        self.logger.info(f'邮件发送成功 - 收件人: {recipients}, 主题: {subject}')
    
    def log_email_failed(self, recipients, error):
        self.logger.error(f'邮件发送失败 - 收件人: {recipients}, 错误: {error}')
    
    def log_api_error(self, api_name, error):
        self.logger.error(f'API调用失败 - {api_name}: {error}')
    
    def log_config_loaded(self, fund_count, email_count):
        self.logger.info(f'配置加载完成 - 基金数量: {fund_count}, 邮件数量: {email_count}')
    
    def log_system_start(self):
        self.logger.info('='*60)
        self.logger.info('金融价格监控系统启动')
        self.logger.info('='*60)
    
    def log_system_stop(self):
        self.logger.info('='*60)
        self.logger.info('金融价格监控系统停止')
        self.logger.info('='*60)
    
    def log_error(self, error_msg):
        self.logger.error(f'系统错误: {error_msg}')
    
    def log_info(self, info_msg):
        self.logger.info(info_msg)
    
    def log_warning(self, warning_msg):
        self.logger.warning(warning_msg)
    
    def log_debug(self, debug_msg):
        self.logger.debug(debug_msg)
    
    def log_alert_triggered(self, alert_type, asset_name, alert_info):
        alert_record = {
            'type': alert_type,
            'asset_name': asset_name,
            'info': alert_info,
            'timestamp': datetime.now().isoformat()
        }
        self.alert_history.append(alert_record)
        
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        self.logger.warning(f'预警触发 - {alert_type}: {asset_name} - {alert_info}')
    
    def get_alert_history(self, hours=24) -> list:
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            record for record in self.alert_history
            if datetime.fromisoformat(record['timestamp']) > cutoff_time
        ]


logger_instance = FinancialMonitorLogger()
