import configparser
import os
import time
from typing import List, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ConfigManager:
    def __init__(self, config_path: str, fund_list_path: str, email_list_path: str, logger):
        self.config_path = config_path
        self.fund_list_path = fund_list_path
        self.email_list_path = email_list_path
        self.logger = logger
        
        self.config = configparser.ConfigParser()
        self.fund_codes = set()
        self.email_addresses = set()
        
        self.observer = None
        self.file_change_callbacks = []
        
        self._load_all_configs()
    
    def _load_all_configs(self):
        self._load_config_file()
        self._load_fund_list()
        self._load_email_list()
    
    def _load_config_file(self):
        try:
            self.config.read(self.config_path, encoding='utf-8')
            self.logger.log_info(f'配置文件加载成功: {self.config_path}')
        except Exception as e:
            self.logger.log_error(f'配置文件加载失败: {str(e)}')
            raise
    
    def _load_fund_list(self):
        try:
            if not os.path.exists(self.fund_list_path):
                self.logger.log_warning(f'基金列表文件不存在，将创建: {self.fund_list_path}')
                with open(self.fund_list_path, 'w', encoding='utf-8') as f:
                    f.write('# 基金代码列表\n# 每行一个基金代码，以#开头的行为注释\n')
                self.fund_codes = set()
                return
            
            new_fund_codes = set()
            
            with open(self.fund_list_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        fund_code = line.strip()
                        if fund_code:
                            new_fund_codes.add(fund_code)
            
            added_funds = new_fund_codes - self.fund_codes
            removed_funds = self.fund_codes - new_fund_codes
            
            if added_funds or removed_funds:
                self.fund_codes = new_fund_codes
                if added_funds:
                    self.logger.log_info(f'新增基金代码: {added_funds}')
                if removed_funds:
                    self.logger.log_info(f'移除基金代码: {removed_funds}')
                self._notify_file_change('fund_list')
            else:
                self.fund_codes = new_fund_codes
            
            self.logger.log_info(f'当前监控基金数量: {len(self.fund_codes)}')
            
        except Exception as e:
            self.logger.log_error(f'加载基金列表失败: {str(e)}')
    
    def _load_email_list(self):
        try:
            if not os.path.exists(self.email_list_path):
                self.logger.log_warning(f'邮件列表文件不存在，将创建: {self.email_list_path}')
                with open(self.email_list_path, 'w', encoding='utf-8') as f:
                    f.write('# 邮件地址列表\n# 每行一个邮箱地址，以#开头的行为注释\n')
                self.email_addresses = set()
                return
            
            new_email_addresses = set()
            
            with open(self.email_list_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        email = line.strip()
                        if '@' in email:
                            new_email_addresses.add(email)
            
            added_emails = new_email_addresses - self.email_addresses
            removed_emails = self.email_addresses - new_email_addresses
            
            if added_emails or removed_emails:
                self.email_addresses = new_email_addresses
                if added_emails:
                    self.logger.log_info(f'新增邮件地址: {added_emails}')
                if removed_emails:
                    self.logger.log_info(f'移除邮件地址: {removed_emails}')
                self._notify_file_change('email_list')
            else:
                self.email_addresses = new_email_addresses
            
            self.logger.log_info(f'当前邮件接收人数: {len(self.email_addresses)}')
            
        except Exception as e:
            self.logger.log_error(f'加载邮件列表失败: {str(e)}')
    
    def reload_all_configs(self):
        self._load_all_configs()
        self.logger.log_config_loaded(len(self.fund_codes), len(self.email_addresses))
    
    def reload_fund_list(self):
        self._load_fund_list()
    
    def reload_email_list(self):
        self._load_email_list()
    
    def get_fund_codes(self) -> List[str]:
        return list(self.fund_codes)
    
    def get_email_addresses(self) -> List[str]:
        return list(self.email_addresses)
    
    def get_config(self):
        return self.config
    
    def add_fund_code(self, fund_code: str):
        fund_code = fund_code.strip()
        if not fund_code:
            return False
        
        if fund_code in self.fund_codes:
            self.logger.log_warning(f'基金代码已存在: {fund_code}')
            return False
        
        try:
            with open(self.fund_list_path, 'a', encoding='utf-8') as f:
                f.write(f'{fund_code}\n')
            self.fund_codes.add(fund_code)
            self.logger.log_info(f'添加基金代码成功: {fund_code}')
            return True
        except Exception as e:
            self.logger.log_error(f'添加基金代码失败: {str(e)}')
            return False
    
    def add_email_address(self, email: str):
        email = email.strip()
        if not email or '@' not in email:
            return False
        
        if email in self.email_addresses:
            self.logger.log_warning(f'邮件地址已存在: {email}')
            return False
        
        try:
            with open(self.email_list_path, 'a', encoding='utf-8') as f:
                f.write(f'{email}\n')
            self.email_addresses.add(email)
            self.logger.log_info(f'添加邮件地址成功: {email}')
            return True
        except Exception as e:
            self.logger.log_error(f'添加邮件地址失败: {str(e)}')
            return False
    
    def remove_email_address(self, email: str):
        email = email.strip()
        if email not in self.email_addresses:
            self.logger.log_warning(f'邮件地址不存在: {email}')
            return False
        
        try:
            lines = []
            with open(self.email_list_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and line != email:
                        lines.append(line)
                    elif line.startswith('#'):
                        lines.append(line)
            
            with open(self.email_list_path, 'w', encoding='utf-8') as f:
                f.write('# 邮件地址列表\n# 每行一个邮箱地址，以#开头的行为注释\n')
                for line in lines:
                    f.write(f'{line}\n')
            
            self.email_addresses.remove(email)
            self.logger.log_info(f'删除邮件地址成功: {email}')
            return True
        except Exception as e:
            self.logger.log_error(f'删除邮件地址失败: {str(e)}')
            return False
    
    def get_email_list(self) -> List[str]:
        return self.get_email_addresses()
    
    def start_file_watcher(self):
        if self.observer:
            return
        
        try:
            handler = ConfigFileChangeHandler(self)
            self.observer = Observer()
            self.observer.schedule(handler, path=os.path.dirname(self.fund_list_path), recursive=False)
            self.observer.start()
            self.logger.log_info('文件监控服务已启动')
        except Exception as e:
            self.logger.log_error(f'启动文件监控服务失败: {str(e)}')
    
    def stop_file_watcher(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.logger.log_info('文件监控服务已停止')
    
    def _notify_file_change(self, file_type: str):
        for callback in self.file_change_callbacks:
            try:
                callback(file_type)
            except Exception as e:
                self.logger.log_error(f'文件变更回调执行失败: {str(e)}')
    
    def register_file_change_callback(self, callback):
        if callback not in self.file_change_callbacks:
            self.file_change_callbacks.append(callback)
    
    def unregister_file_change_callback(self, callback):
        if callback in self.file_change_callbacks:
            self.file_change_callbacks.remove(callback)


class ConfigFileChangeHandler(FileSystemEventHandler):
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.last_modified = {}
        self.debounce_delay = 1
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        if file_path not in [self.config_manager.fund_list_path, self.config_manager.email_list_path]:
            return
        
        current_time = time.time()
        
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < self.debounce_delay:
                return
        
        self.last_modified[file_path] = current_time
        
        if file_path == self.config_manager.fund_list_path:
            self.config_manager._load_fund_list()
        elif file_path == self.config_manager.email_list_path:
            self.config_manager._load_email_list()
