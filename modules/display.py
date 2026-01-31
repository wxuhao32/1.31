from typing import Dict, List
from datetime import datetime

class DisplayFormatter:
    USD_TO_CNY = 7.2
    OUNCE_TO_GRAM = 31.1034768
    
    _previous_prices = {}
    _previous_fund_values = {}
    _exchange_rate_manager = None
    
    @classmethod
    def set_exchange_rate_manager(cls, manager):
        cls._exchange_rate_manager = manager
    
    @classmethod
    def convert_to_cny_per_gram(cls, price_usd_per_ounce: float) -> float:
        if cls._exchange_rate_manager:
            return cls._exchange_rate_manager.convert_usd_oz_to_cny_gram(price_usd_per_ounce)
        return price_usd_per_ounce * cls.USD_TO_CNY / cls.OUNCE_TO_GRAM
    
    @staticmethod
    def format_price(price: float) -> str:
        return f"{price:.2f}"
    
    @staticmethod
    def format_price_with_change(name: str, current_price: float) -> str:
        if name in DisplayFormatter._previous_prices:
            prev_price = DisplayFormatter._previous_prices[name]
            change = current_price - prev_price
            if change > 0:
                return f"{current_price:.2f} [+{change:.4f}]"
            elif change < 0:
                return f"{current_price:.2f} [{change:.4f}]"
            else:
                return f"{current_price:.2f} [0.0000]"
        DisplayFormatter._previous_prices[name] = current_price
        return f"{current_price:.2f}"
    
    @staticmethod
    def format_fund_with_change(code: str, current_value: float) -> str:
        if code in DisplayFormatter._previous_fund_values:
            prev_value = DisplayFormatter._previous_fund_values[code]
            change = current_value - prev_value
            if change > 0:
                return f"{current_value:.4f} [+{change:.4f}]"
            elif change < 0:
                return f"{current_value:.4f} [{change:.4f}]"
            else:
                return f"{current_value:.4f} [0.0000]"
        DisplayFormatter._previous_fund_values[code] = current_value
        return f"{current_value:.4f}"
    
    @staticmethod
    def format_change(change_percent: str) -> str:
        try:
            value = float(change_percent.replace('%', ''))
            if value > 0:
                return f"▲ +{value:.2f}%"
            elif value < 0:
                return f"▼ {abs(value):.2f}%"
            else:
                return f"● 0.00%"
        except:
            return change_percent
    
    @staticmethod
    def get_trend_indicator(value: float) -> str:
        if value > 0:
            return "🔺"
        elif value < 0:
            return "🔻"
        else:
            return "●"
    
    @staticmethod
    def create_dashed_table(data: Dict) -> str:
        lines = []
        
        lines.append("┌" + "─" * 90 + "┐")
        lines.append("│" + " " * 37 + "金融价格监控" + " " * 36 + "│")
        lines.append("├" + "─" * 90 + "┤")
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines.append(f"│ 更新时间: {current_time}" + " " * (90 - len(f"│ 更新时间: {current_time}") - 1) + "│")
        lines.append("├" + "─" * 90 + "┤")
        
        lines.append("│" + "-" * 90 + "│")
        lines.append("│" + " " * 18 + "贵金属价格 (实时波动)" + " " * 52 + "│")
        lines.append("│" + "-" * 90 + "│")
        
        if 'gold' in data:
            gold = data['gold']
            price = gold.get('current_price', gold.get('price', 0))
            price_cny = DisplayFormatter.convert_to_cny_per_gram(price)
            open_cny = DisplayFormatter.convert_to_cny_per_gram(gold['open_price'])
            high_cny = DisplayFormatter.convert_to_cny_per_gram(gold['high_price'])
            low_cny = DisplayFormatter.convert_to_cny_per_gram(gold['low_price'])
            change_str = DisplayFormatter.format_change(gold.get('change_percent_str', gold.get('change_percent', '0%')))
            price_with_change = DisplayFormatter.format_price_with_change('gold_cny', price_cny)
            
            lines.append("│" + "-" * 90 + "│")
            lines.append(f"│ 🥇 {gold['name']}")
            lines.append(f"│   美元/盎司: {DisplayFormatter.format_price(price)} | 开盘: {DisplayFormatter.format_price(gold['open_price'])} | 最高: {DisplayFormatter.format_price(gold['high_price'])} | 最低: {DisplayFormatter.format_price(gold['low_price'])}")
            lines.append(f"│   人民币/克: {price_with_change} | 开盘: {DisplayFormatter.format_price(open_cny)} | 最高: {DisplayFormatter.format_price(high_cny)} | 最低: {DisplayFormatter.format_price(low_cny)}")
            lines.append(f"│   涨跌幅: {change_str} | 更新: {gold['update_time']} | 来源: {gold.get('source', '未知')}")
        
        if 'silver' in data:
            silver = data['silver']
            price = silver.get('current_price', silver.get('price', 0))
            price_cny = DisplayFormatter.convert_to_cny_per_gram(price)
            open_cny = DisplayFormatter.convert_to_cny_per_gram(silver['open_price'])
            high_cny = DisplayFormatter.convert_to_cny_per_gram(silver['high_price'])
            low_cny = DisplayFormatter.convert_to_cny_per_gram(silver['low_price'])
            change_str = DisplayFormatter.format_change(silver.get('change_percent_str', silver.get('change_percent', '0%')))
            price_with_change = DisplayFormatter.format_price_with_change('silver_cny', price_cny)
            
            lines.append("│" + "-" * 90 + "│")
            lines.append(f"│ 🥈 {silver['name']}")
            lines.append(f"│   美元/盎司: {DisplayFormatter.format_price(price)} | 开盘: {DisplayFormatter.format_price(silver['open_price'])} | 最高: {DisplayFormatter.format_price(silver['high_price'])} | 最低: {DisplayFormatter.format_price(silver['low_price'])}")
            lines.append(f"│   人民币/克: {price_with_change} | 开盘: {DisplayFormatter.format_price(open_cny)} | 最高: {DisplayFormatter.format_price(high_cny)} | 最低: {DisplayFormatter.format_price(low_cny)}")
            lines.append(f"│   涨跌幅: {change_str} | 更新: {silver['update_time']} | 来源: {silver.get('source', '未知')}")
        
        lines.append("│" + "-" * 90 + "│")
        
        if 'funds' in data and data['funds']:
            lines.append("│" + " " * 18 + "基金涨跌幅 (实时波动)" + " " * 52 + "│")
            lines.append("│" + "-" * 90 + "│")
            
            for fund_code, fund_data in data['funds'].items():
                if 'error' not in fund_data:
                    change_str = DisplayFormatter.format_change(f"{fund_data['change_percent']:.2f}%")
                    value_with_change = DisplayFormatter.format_fund_with_change(fund_code, fund_data['estimated_value'])
                    lines.append("│" + "-" * 90 + "│")
                    lines.append(f"│ 📊 基金代码: {fund_data['code']} | 基金名称: {fund_data['name']}")
                    lines.append(f"│   单位净值: {DisplayFormatter.format_price(fund_data['net_value'])} | 估算净值: {value_with_change} | 涨跌幅: {change_str}")
                    lines.append(f"│   更新时间: {fund_data['update_time']}")
        
        lines.append("└" + "─" * 90 + "┘")
        
        return '\n'.join(lines)
    
    @staticmethod
    def clear_screen():
        print('\033[H\033[J', end='', flush=True)
