/**
 * API Service - 金融监控系统前端API调用封装
 */

const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : '/api';

class APIService {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
        this.timeout = 15000;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.defaultHeaders,
                ...options.headers
            }
        };

        const controller = new AbortController();
        config.signal = controller.signal;

        const timeoutId = setTimeout(() => {
            controller.abort();
        }, this.timeout);

        try {
            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('请求超时，请稍后重试');
            }
            
            throw error;
        }
    }

    // Market APIs
    async getPreciousMetals() {
        return this.request('/market/precious-metals');
    }

    async getFunds() {
        return this.request('/market/funds');
    }

    async getHistory(assetType) {
        return this.request(`/market/history/${assetType}`);
    }

    async getFundHistory(fundCode) {
        return this.request(`/market/fund-history/${fundCode}`);
    }

    async getSingleFund(fundCode) {
        return this.request(`/market/fund/${fundCode}`);
    }

    // Config APIs
    async getFundCodes() {
        return this.request('/config/funds');
    }

    async addFundCode(fundCode) {
        return this.request('/config/funds', {
            method: 'POST',
            body: JSON.stringify({ code: fundCode })
        });
    }

    async deleteFundCode(fundCode) {
        return this.request(`/config/funds/${fundCode}`, {
            method: 'DELETE'
        });
    }

    // Alert Configuration APIs
    async getAlertConfig() {
        return this.request('/alert/config');
    }

    async updateAlertConfig(config) {
        return this.request('/alert/config', {
            method: 'PUT',
            body: JSON.stringify(config)
        });
    }

    async addAlertRecipient(email) {
        return this.request('/alert/recipients', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    }

    async deleteAlertRecipient(email) {
        return this.request(`/alert/recipients/${email}`, {
            method: 'DELETE'
        });
    }

    async sendTestEmail(recipient) {
        return this.request('/alert/test-email', {
            method: 'POST',
            body: JSON.stringify({ recipient })
        });
    }

    async getAlertHistory(hours = 24) {
        return this.request(`/alert/history?hours=${hours}`);
    }

    // Exchange Rate APIs
    async getExchangeRate(forceRefresh = false) {
        const params = forceRefresh ? '?refresh=true' : '';
        return this.request(`/exchange/rate${params}`);
    }

    async refreshExchangeRate() {
        return this.request('/exchange/refresh', {
            method: 'POST'
        });
    }

    async convertCurrency(price, direction = 'usd_oz_to_cny_gram') {
        return this.request(`/exchange/convert?price=${price}&direction=${direction}`);
    }

    async validateExchangeRate() {
        return this.request('/exchange/validate');
    }

    // System APIs
    async healthCheck() {
        return this.request('/health');
    }

    async getInfo() {
        return this.request('/info');
    }

    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
}

// 创建全局API服务实例
const api = new APIService();

// 工具函数
const Utils = {
    formatNumber(num, decimals = 2) {
        if (num === null || num === undefined || isNaN(num)) {
            return '---';
        }
        return Number(num).toFixed(decimals);
    },

    formatCurrency(num, currency = 'CNY') {
        if (num === null || num === undefined || isNaN(num)) {
            return '---';
        }
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(num);
    },

    formatPercent(num, decimals = 2) {
        if (num === null || num === undefined || isNaN(num)) {
            return '---';
        }
        const sign = num >= 0 ? '+' : '';
        return `${sign}${Number(num).toFixed(decimals)}%`;
    },

    formatTime(date) {
        if (!date) return '---';
        const d = new Date(date);
        const now = new Date();
        const diff = now - d;
        
        if (diff < 60000) {
            return '刚刚';
        } else if (diff < 3600000) {
            return `${Math.floor(diff / 60000)}分钟前`;
        } else if (diff < 86400000) {
            return `${Math.floor(diff / 3600000)}小时前`;
        } else {
            return d.toLocaleDateString('zh-CN');
        }
    },

    formatDateTime(date) {
        if (!date) return '---';
        const d = new Date(date);
        return d.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    getChangeClass(change) {
        if (change > 0) return 'positive';
        if (change < 0) return 'negative';
        return 'neutral';
    },

    getChangeIcon(change) {
        if (change > 0) return '▲';
        if (change < 0) return '▼';
        return '●';
    },

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func(...args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },

    localStorageGet(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch {
            return defaultValue;
        }
    },

    localStorageSet(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch {
            return false;
        }
    },

    localStorageRemove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch {
            return false;
        }
    }
};

// 导出
window.APIService = APIService;
window.api = api;
window.Utils = Utils;
