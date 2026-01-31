from typing import Dict, List
from datetime import datetime, timedelta


class AlertMonitor:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        
        self.gold_threshold = config.getfloat('gold', 'price_threshold_gold')
        self.silver_threshold = config.getfloat('gold', 'price_threshold_silver')
        self.fund_change_threshold = config.getfloat('fund', 'change_percent_threshold')
        self.alert_cooldown_minutes = config.getint('gold', 'alert_cooldown_minutes')
        
        self.alert_history = {}
        self.enable_gold_monitor = config.getboolean('gold', 'enable_monitor')
        self.enable_fund_monitor = config.getboolean('fund', 'enable_monitor')
    
    def check_gold_silver_alerts(self, gold_data: Dict, silver_data: Dict) -> List[Dict]:
        alerts = []
        
        if not self.enable_gold_monitor:
            return alerts
        
        if gold_data:
            gold_alert = self._check_price_alert('gold', '黄金', gold_data['current_price'], self.gold_threshold)
            if gold_alert:
                alerts.append(gold_alert)
        
        if silver_data:
            silver_alert = self._check_price_alert('silver', '白银', silver_data['current_price'], self.silver_threshold)
            if silver_alert:
                alerts.append(silver_alert)
        
        return alerts
    
    def check_fund_alerts(self, fund_data: Dict[str, Dict]) -> List[Dict]:
        alerts = []
        
        if not self.enable_fund_monitor:
            return alerts
        
        for fund_code, data in fund_data.items():
            if 'error' in data:
                continue
            
            change_percent = data['change_percent']
            
            if change_percent >= self.fund_change_threshold or change_percent <= -self.fund_change_threshold:
                alert = self._check_fund_alert(fund_code, data)
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def _check_price_alert(self, asset_type: str, asset_name: str, current_price: float, threshold: float) -> Dict:
        alert_key = f'{asset_type}_price'
        
        if current_price <= threshold:
            if self._is_in_cooldown(alert_key):
                return None
            
            alert = {
                'type': 'price_threshold',
                'asset_type': asset_type,
                'asset_name': asset_name,
                'current_price': current_price,
                'threshold': threshold,
                'alert_time': datetime.now().isoformat(),
                'message': f'{asset_name}价格预警：当前价格 {current_price:.2f} 元/克，已跌破阈值 {threshold:.2f} 元/克'
            }
            
            self._record_alert(alert_key)
            self.logger.log_alert_triggered('价格阈值预警', asset_name, 
                                           f'当前价格 {current_price:.2f}, 阈值 {threshold:.2f}')
            
            return alert
        
        return None
    
    def _check_fund_alert(self, fund_code: str, fund_data: Dict) -> Dict:
        alert_key = f'fund_{fund_code}'
        
        change_percent = fund_data['change_percent']
        
        if self._is_in_cooldown(alert_key):
            return None
        
        direction = '上涨' if change_percent > 0 else '下跌'
        alert = {
            'type': 'fund_change',
            'fund_code': fund_code,
            'fund_name': fund_data['name'],
            'current_value': fund_data['estimated_value'],
            'change_percent': change_percent,
            'threshold': self.fund_change_threshold,
            'alert_time': datetime.now().isoformat(),
            'message': f'基金涨跌幅预警：{fund_data["name"]}({fund_code}) {direction} {abs(change_percent):.2f}%，超过阈值 {self.fund_change_threshold}%'
        }
        
        self._record_alert(alert_key)
        self.logger.log_alert_triggered('基金涨跌幅预警', fund_data['name'],
                                       f'{direction} {abs(change_percent):.2f}%, 当前净值 {fund_data["estimated_value"]:.4f}')
        
        return alert
    
    def _is_in_cooldown(self, alert_key: str) -> bool:
        if alert_key not in self.alert_history:
            return False
        
        last_alert_time = self.alert_history[alert_key]
        cooldown_time = timedelta(minutes=self.alert_cooldown_minutes)
        
        return datetime.now() - last_alert_time < cooldown_time
    
    def _record_alert(self, alert_key: str):
        self.alert_history[alert_key] = datetime.now()
    
    def clear_old_alert_history(self, hours: int = 24):
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        self.alert_history = {
            key: time 
            for key, time in self.alert_history.items()
            if time > cutoff_time
        }
    
    def get_alert_count(self, hours: int = 24) -> int:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return sum(1 for time in self.alert_history.values() if time > cutoff_time)
    
    def format_alert_email_content(self, alert: Dict) -> str:
        if alert['type'] == 'price_threshold':
            content = f"""
            贵金属价格预警通知
            ==================
            
            预警类型：价格跌破阈值
            资产名称：{alert['asset_name']}
            当前价格：{alert['current_price']:.2f} 元/克
            预警阈值：{alert['threshold']:.2f} 元/克
            预警时间：{alert['alert_time']}
            
            请及时关注市场动态，做出相应的投资决策。
            """
        elif alert['type'] == 'fund_change':
            direction = '上涨' if alert['change_percent'] > 0 else '下跌'
            content = f"""
            基金涨跌幅预警通知
            ==================
            
            预警类型：涨跌幅超过阈值
            基金名称：{alert['fund_name']}
            基金代码：{alert['fund_code']}
            当前净值：{alert['current_value']:.4f}
            涨跌幅：{direction} {abs(alert['change_percent']):.2f}%
            预警阈值：{alert['threshold']}%
            预警时间：{alert['alert_time']}
            
            请及时关注基金表现，做出相应的投资决策。
            """
        else:
            content = f"未知预警类型：{alert}"
        
        return content.strip()
    
    def format_alert_email_subject(self, alert: Dict) -> str:
        if alert['type'] == 'price_threshold':
            return f"【金融预警】{alert['asset_name']}价格跌破阈值 {alert['current_price']:.2f}元/克"
        elif alert['type'] == 'fund_change':
            direction = '上涨' if alert['change_percent'] > 0 else '下跌'
            return f"【金融预警】{alert['fund_name']}{direction}{abs(alert['change_percent']):.2f}%"
        else:
            return "【金融预警】未知预警"
