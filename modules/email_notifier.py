import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List
from datetime import datetime


class EmailNotifier:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        
        self.sender_email = config.get('email', 'sender_email')
        self.sender_password = config.get('email', 'sender_password')
        self.smtp_server = config.get('email', 'smtp_server')
        self.smtp_port = config.getint('email', 'smtp_port')
        self.retry_attempts = config.getint('email', 'retry_attempts')
        self.retry_delay = config.getint('email', 'retry_delay_seconds')
        
        self.sent_emails = set()
    
    def send_alert_email(self, recipients: List[str], subject: str, content: str) -> bool:
        success = True
        
        for recipient in recipients:
            email_key = self._get_email_key(recipient, subject)
            if email_key in self.sent_emails:
                self.logger.log_warning(f'邮件已发送过，跳过: {recipient} - {subject}')
                continue
            
            result = self._send_single_email(recipient, subject, content)
            if result:
                self.sent_emails.add(email_key)
                self.logger.log_email_sent(recipient, subject)
            else:
                success = False
                self.logger.log_email_failed(recipient, '发送失败')
        
        return success
    
    def _send_single_email(self, recipient: str, subject: str, content: str) -> bool:
        for attempt in range(self.retry_attempts):
            try:
                msg = MIMEMultipart('alternative')
                msg['From'] = self.sender_email
                msg['To'] = recipient
                msg['Subject'] = Header(subject, 'utf-8')
                
                text_part = MIMEText(content, 'plain', 'utf-8')
                msg.attach(text_part)
                
                if self.smtp_port == 465:
                    server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)
                else:
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                    server.starttls()
                
                server.set_debuglevel(0)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, [recipient], msg.as_string())
                server.quit()
                
                self.logger.log_info(f'邮件发送成功: {recipient} - {subject}')
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                self.logger.log_error(f'邮件认证失败 (尝试 {attempt + 1}/{self.retry_attempts}): {str(e)}')
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    return False
                    
            except smtplib.SMTPConnectError as e:
                self.logger.log_error(f'邮件服务器连接失败 (尝试 {attempt + 1}/{self.retry_attempts}): {str(e)}')
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    return False
                    
            except smtplib.SMTPException as e:
                self.logger.log_error(f'邮件发送异常 (尝试 {attempt + 1}/{self.retry_attempts}): {str(e)}')
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    return False
                    
            except Exception as e:
                self.logger.log_error(f'邮件发送未知错误 (尝试 {attempt + 1}/{self.retry_attempts}): {str(e)}')
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    return False
        
        return False
    
    def _get_email_key(self, recipient: str, subject: str) -> str:
        timestamp = datetime.now().strftime('%Y%m%d%H')
        return f'{recipient}_{subject}_{timestamp}'
    
    def send_test_email(self, recipient: str) -> bool:
        subject = '金融监控系统测试邮件'
        content = f"""
        金融监控系统测试邮件
        ==================
        
        这是一封测试邮件，用于验证邮件发送功能是否正常。
        
        发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        收件人：{recipient}
        
        如果您收到这封邮件，说明邮件发送功能配置正确！
        
        金融价格监控系统
        """
        
        return self._send_single_email(recipient, subject, content.strip())
    
    def send_summary_report(self, recipients: List[str], gold_data: dict, silver_data: dict, fund_data: dict):
        subject = f'金融监控系统日报 - {datetime.now().strftime("%Y-%m-%d")}'
        
        content = f"""
        金融价格监控系统日报
        ==================
        
        报告时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        【贵金属价格】
        """
        
        if gold_data:
            content += f"""
        黄金({gold_data['name']})
        - 当前价格：{gold_data['current_price']:.2f} 元/克
        - 开盘价：{gold_data['open_price']:.2f} 元/克
        - 最高价：{gold_data['high_price']:.2f} 元/克
        - 最低价：{gold_data['low_price']:.2f} 元/克
        - 涨跌幅：{gold_data['change_percent_str']}
        - 更新时间：{gold_data['update_time']}
            """
        
        if silver_data:
            content += f"""
        白银({silver_data['name']})
        - 当前价格：{silver_data['current_price']:.2f} 元/克
        - 开盘价：{silver_data['open_price']:.2f} 元/克
        - 最高价：{silver_data['high_price']:.2f} 元/克
        - 最低价：{silver_data['low_price']:.2f} 元/克
        - 涨跌幅：{silver_data['change_percent_str']}
        - 更新时间：{silver_data['update_time']}
            """
        
        content += "\n【基金涨跌幅】\n"
        
        for fund_code, data in fund_data.items():
            if 'error' in data:
                content += f"{fund_code}: 获取失败 - {data['error']}\n"
            else:
                direction = '↑' if data['change_percent'] > 0 else '↓' if data['change_percent'] < 0 else '-'
                content += f"{data['name']}({fund_code}): 净值 {data['estimated_value']:.4f}, 涨跌幅 {direction} {abs(data['change_percent']):.2f}%\n"
        
        content += f"\n【系统状态】\n"
        content += f"监控基金数量：{len(fund_data)}\n"
        content += f"邮件接收人数：{len(recipients)}\n"
        content += f"\n金融价格监控系统\n"
        
        self.send_alert_email(recipients, subject, content.strip())
    
    def clear_old_email_records(self, hours: int = 24):
        current_timestamp = datetime.now().strftime('%Y%m%d%H')
        cutoff_timestamp = (datetime.now().replace(hour=datetime.now().hour - hours)).strftime('%Y%m%d%H')
        
        self.sent_emails = {
            email_key for email_key in self.sent_emails
            if email_key.split('_')[-1] > cutoff_timestamp
        }
        
        self.logger.log_info(f'已清除 {hours} 小时前的邮件发送记录')
    
    def get_sent_count(self, hours: int = 24) -> int:
        cutoff_timestamp = (datetime.now().replace(hour=datetime.now().hour - hours)).strftime('%Y%m%d%H')
        
        return sum(
            1 for email_key in self.sent_emails
            if email_key.split('_')[-1] > cutoff_timestamp
        )
