/**
 * Main Application - 金融监控系统前端主逻辑
 */

class FinancialMonitorApp {
    constructor() {
        this.state = {
            preciousMetals: null,
            funds: {},
            fundList: [],
            isLoading: false,
            isConnected: true,
            lastUpdate: null,
            currentPage: 1,
            itemsPerPage: 10,
            searchQuery: '',
            autoRefresh: true,
            refreshInterval: 3,
            darkMode: true,
            refreshTimer: null
        };

        this.elements = {};
        this.init();
    }

    async init() {
        this.cacheElements();
        this.bindEvents();
        this.loadSettings();
        await this.loadInitialData();
        this.startAutoRefresh();
        this.setupServiceWorker();
    }

    cacheElements() {
        this.elements = {
            connectionStatus: document.getElementById('connectionStatus'),
            connectionText: document.getElementById('connectionText'),
            lastUpdate: document.getElementById('lastUpdate'),
            exchangeRateItem: document.getElementById('exchangeRateItem'),
            exchangeRateText: document.getElementById('exchangeRateText'),
            goldName: document.getElementById('goldName'),
            goldPriceUSD: document.getElementById('goldPriceUSD'),
            goldPriceCNY: document.getElementById('goldPriceCNY'),
            goldOpen: document.getElementById('goldOpen'),
            goldHigh: document.getElementById('goldHigh'),
            goldLow: document.getElementById('goldLow'),
            goldChange: document.getElementById('goldChange'),
            goldUpdateTime: document.getElementById('goldUpdateTime'),
            silverName: document.getElementById('silverName'),
            silverPriceUSD: document.getElementById('silverPriceUSD'),
            silverPriceCNY: document.getElementById('silverPriceCNY'),
            silverOpen: document.getElementById('silverOpen'),
            silverHigh: document.getElementById('silverHigh'),
            silverLow: document.getElementById('silverLow'),
            silverChange: document.getElementById('silverChange'),
            silverUpdateTime: document.getElementById('silverUpdateTime'),
            fundList: document.getElementById('fundList'),
            fundLoading: document.getElementById('fundLoading'),
            fundPagination: document.getElementById('fundPagination'),
            prevPage: document.getElementById('prevPage'),
            nextPage: document.getElementById('nextPage'),
            paginationInfo: document.getElementById('paginationInfo'),
            fundSearch: document.getElementById('fundSearch'),
            refreshBtn: document.getElementById('refreshBtn'),
            menuBtn: document.getElementById('menuBtn'),
            sidebar: document.getElementById('sidebar'),
            sidebarOverlay: document.getElementById('sidebarOverlay'),
            closeSidebar: document.getElementById('closeSidebar'),
            sidebarAlertLink: document.getElementById('sidebarAlertLink'),
            settingsPanel: document.getElementById('settingsPanel'),
            closeSettings: document.getElementById('closeSettings'),
            autoRefresh: document.getElementById('autoRefresh'),
            refreshInterval: document.getElementById('refreshInterval'),
            darkMode: document.getElementById('darkMode'),
            newFundCode: document.getElementById('newFundCode'),
            addFundBtn: document.getElementById('addFundBtn'),
            toastContainer: document.getElementById('toastContainer'),
            loadingOverlay: document.getElementById('loadingOverlay'),
            alertPanel: document.getElementById('alertPanel'),
            alertOverlay: document.getElementById('alertOverlay'),
            closeAlert: document.getElementById('closeAlert'),
            enableGoldAlert: document.getElementById('enableGoldAlert'),
            enableSilverAlert: document.getElementById('enableSilverAlert'),
            enableFundAlert: document.getElementById('enableFundAlert'),
            goldThreshold: document.getElementById('goldThreshold'),
            silverThreshold: document.getElementById('silverThreshold'),
            fundThreshold: document.getElementById('fundThreshold'),
            alertCooldown: document.getElementById('alertCooldown'),
            saveAlertConfig: document.getElementById('saveAlertConfig'),
            newEmail: document.getElementById('newEmail'),
            addEmailBtn: document.getElementById('addEmailBtn'),
            emailList: document.getElementById('emailList'),
            testEmailBtn: document.getElementById('testEmailBtn'),
            alertHistory: document.getElementById('alertHistory'),
            historyFilter: document.getElementById('historyFilter')
        };

        this.alertConfig = null;
        this.alertRecipients = [];
        this.alertHistoryData = [];
        this.exchangeRate = 7.2;
        this.exchangeRateInfo = null;
    }

    bindEvents() {
        // Refresh button
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.addEventListener('click', () => this.manualRefresh());
        }

        // Menu button
        if (this.elements.menuBtn) {
            this.elements.menuBtn.addEventListener('click', () => this.openSidebar());
        }

        // Sidebar
        if (this.elements.sidebarOverlay) {
            this.elements.sidebarOverlay.addEventListener('click', () => this.closeSidebar());
        }
        if (this.elements.closeSidebar) {
            this.elements.closeSidebar.addEventListener('click', () => this.closeSidebar());
        }
        if (this.elements.sidebarAlertLink) {
            this.elements.sidebarAlertLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeSidebar();
                this.openAlertPanel();
            });
        }

        // Settings
        if (this.elements.closeSettings) {
            this.elements.closeSettings.addEventListener('click', () => this.closeSettings());
        }

        // Settings toggles
        if (this.elements.autoRefresh) {
            this.elements.autoRefresh.addEventListener('change', (e) => {
                this.state.autoRefresh = e.target.checked;
                this.saveSettings();
                if (this.state.autoRefresh) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }

        if (this.elements.refreshInterval) {
            this.elements.refreshInterval.addEventListener('change', (e) => {
                this.state.refreshInterval = parseInt(e.target.value);
                this.saveSettings();
                if (this.state.autoRefresh) {
                    this.startAutoRefresh();
                }
            });
        }

        if (this.elements.darkMode) {
            this.elements.darkMode.addEventListener('change', (e) => {
                this.state.darkMode = e.target.checked;
                this.applyTheme();
                this.saveSettings();
            });
        }

        // Fund search
        if (this.elements.fundSearch) {
            this.elements.fundSearch.addEventListener('input', Utils.debounce((e) => {
                this.state.searchQuery = e.target.value.trim();
                this.state.currentPage = 1;
                this.renderFundList();
            }, 300));
        }

        // Pagination
        if (this.elements.prevPage) {
            this.elements.prevPage.addEventListener('click', () => {
                if (this.state.currentPage > 1) {
                    this.state.currentPage--;
                    this.renderFundList();
                }
            });
        }

        if (this.elements.nextPage) {
            this.elements.nextPage.addEventListener('click', () => {
                const totalPages = this.getTotalPages();
                if (this.state.currentPage < totalPages) {
                    this.state.currentPage++;
                    this.renderFundList();
                }
            });
        }

        // Add fund
        if (this.elements.addFundBtn) {
            this.elements.addFundBtn.addEventListener('click', () => this.addFund());
        }
        if (this.elements.newFundCode) {
            this.elements.newFundCode.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.addFund();
                }
            });
        }

        // Bottom navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                e.currentTarget.classList.add('active');
                
                if (tab === 'alert') {
                    this.openAlertPanel();
                } else {
                    this.closeAlertPanel();
                }
            });
        });

        // Alert panel
        if (this.elements.closeAlert) {
            this.elements.closeAlert.addEventListener('click', () => this.closeAlertPanel());
        }
        if (this.elements.alertOverlay) {
            this.elements.alertOverlay.addEventListener('click', () => this.closeAlertPanel());
        }

        // Alert config save
        if (this.elements.saveAlertConfig) {
            this.elements.saveAlertConfig.addEventListener('click', () => this.saveAlertConfiguration());
        }

        // Email management
        if (this.elements.addEmailBtn) {
            this.elements.addEmailBtn.addEventListener('click', () => this.addEmailRecipient());
        }
        if (this.elements.newEmail) {
            this.elements.newEmail.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.addEmailRecipient();
            });
        }

        // Test email
        if (this.elements.testEmailBtn) {
            this.elements.testEmailBtn.addEventListener('click', () => this.sendTestEmail());
        }

        // Alert history filter
        if (this.elements.historyFilter) {
            this.elements.historyFilter.addEventListener('change', (e) => {
                this.loadAlertHistory(parseInt(e.target.value));
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeSidebar();
                this.closeSettings();
                this.closeAlertPanel();
            }
            if (e.key === 'r' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                this.manualRefresh();
            }
        });

        // Handle online/offline
        window.addEventListener('online', () => this.onOnline());
        window.addEventListener('offline', () => this.onOffline());
    }

    async loadInitialData() {
        this.showLoading(true);
        try {
            await Promise.all([
                this.loadPreciousMetals(),
                this.loadFunds(),
                this.loadExchangeRate()
            ]);
            this.state.lastUpdate = new Date();
            this.updateLastUpdateTime();
        } catch (error) {
            console.error('Initial data load failed:', error);
            this.showToast('加载数据失败，请刷新页面重试', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadPreciousMetals() {
        try {
            const response = await api.getPreciousMetals();
            if (response.success) {
                this.state.preciousMetals = response.data;
                this.renderPreciousMetals();
                this.updateConnectionStatus(true);
            } else {
                throw new Error(response.error || '获取贵金属数据失败');
            }
        } catch (error) {
            console.error('Load precious metals failed:', error);
            this.updateConnectionStatus(false, '数据获取失败');
        }
    }

    async loadFunds() {
        try {
            const response = await api.getFunds();
            const localFundCodes = Utils.localStorageGet('fund_codes', []);
            
            if (response.success) {
                    this.state.funds = response.data || {};
                    
                    if (localFundCodes.length > 0) {
                        const existingCodes = Object.keys(this.state.funds);
                        const codesToFetch = [];
                        
                        localFundCodes.forEach(code => {
                            if (!existingCodes.includes(code)) {
                                this.state.funds[code] = {
                                    code: code,
                                    name: '获取中...',
                                    estimated_value: '---',
                                    net_value: '---',
                                    change_percent: 0,
                                    update_time: ''
                                };
                                codesToFetch.push(code);
                            }
                        });
                        
                        if (codesToFetch.length > 0) {
                            for (const code of codesToFetch) {
                                try {
                                    const fundResponse = await api.getSingleFund(code);
                                    if (fundResponse.success && fundResponse.data) {
                                        this.state.funds[code] = fundResponse.data;
                                    }
                                } catch (e) {
                                    console.error(`Failed to fetch fund ${code}:`, e);
                                    this.state.funds[code].name = '获取失败';
                                }
                            }
                        }
                    }
                    
                    this.renderFundList();
                    this.updateConnectionStatus(true);
                } else {
                    console.warn('获取基金数据失败:', response.error);
                }
            } catch (error) {
                console.error('Load funds failed:', error);
            }
    }

    async loadExchangeRate() {
        try {
            const response = await api.getExchangeRate();
            if (response.success) {
                this.exchangeRate = response.data.rate;
                this.exchangeRateInfo = response.data.info;
                console.log('Exchange rate loaded:', this.exchangeRate, this.exchangeRateInfo);
                this.updateExchangeRateDisplay();
            }
        } catch (error) {
            console.error('Load exchange rate failed:', error);
            this.exchangeRate = 7.2;
            this.exchangeRateInfo = { source: 'Fixed' };
            this.updateExchangeRateDisplay();
        }
    }

    async manualRefresh() {
        const btn = this.elements.refreshBtn;
        if (btn) {
            btn.classList.add('refreshing');
        }

        try {
            await Promise.all([
                this.loadPreciousMetals(),
                this.loadFunds(),
                this.loadExchangeRate()
            ]);
            this.state.lastUpdate = new Date();
            this.updateLastUpdateTime();
            this.showToast('数据已刷新', 'success');
        } catch (error) {
            console.error('Manual refresh failed:', error);
            this.showToast('刷新失败，请稍后重试', 'error');
        } finally {
            if (btn) {
                setTimeout(() => btn.classList.remove('refreshing'), 500);
            }
        }
    }

    renderPreciousMetals() {
        const data = this.state.preciousMetals;
        
        if (!data) return;

        const OUNCE_TO_GRAM = 31.1034768;
        const USD_TO_CNY = this.exchangeRate || 7.2;

        // Gold
        if (data.gold) {
            const gold = data.gold;
            const priceCNY = gold.current_price * USD_TO_CNY / OUNCE_TO_GRAM;
            const openCNY = gold.open_price * USD_TO_CNY / OUNCE_TO_GRAM;
            const highCNY = gold.high_price * USD_TO_CNY / OUNCE_TO_GRAM;
            const lowCNY = gold.low_price * USD_TO_CNY / OUNCE_TO_GRAM;
            const changePercent = gold.change_percent || 0;

            if (this.elements.goldName) this.elements.goldName.textContent = gold.name || '纽约黄金';
            if (this.elements.goldPriceUSD) {
                this.elements.goldPriceUSD.textContent = Utils.formatNumber(gold.current_price);
                this.animateValue(this.elements.goldPriceUSD);
            }
            if (this.elements.goldPriceCNY) {
                this.elements.goldPriceCNY.textContent = Utils.formatNumber(priceCNY);
                this.animateValue(this.elements.goldPriceCNY);
            }
            if (this.elements.goldOpen) this.elements.goldOpen.textContent = Utils.formatNumber(gold.current_price);
            if (this.elements.goldHigh) this.elements.goldHigh.textContent = Utils.formatNumber(gold.low_price);
            if (this.elements.goldLow) this.elements.goldLow.textContent = Utils.formatNumber(gold.high_price);
            
            if (this.elements.goldChange) {
                const changeClass = Utils.getChangeClass(changePercent);
                const changeIcon = Utils.getChangeIcon(changePercent);
                this.elements.goldChange.innerHTML = `
                    <span class="change-value ${changeClass}">${changeIcon} ${Utils.formatPercent(changePercent)}</span>
                `;
            }
            if (this.elements.goldUpdateTime) this.elements.goldUpdateTime.textContent = gold.update_time || '---';
        }

        // Silver
        if (data.silver) {
            const silver = data.silver;
            const priceCNY = silver.current_price * USD_TO_CNY / OUNCE_TO_GRAM;
            const openCNY = silver.open_price * USD_TO_CNY / OUNCE_TO_GRAM;
            const highCNY = silver.high_price * USD_TO_CNY / OUNCE_TO_GRAM;
            const lowCNY = silver.low_price * USD_TO_CNY / OUNCE_TO_GRAM;
            const changePercent = silver.change_percent || 0;

            if (this.elements.silverName) this.elements.silverName.textContent = silver.name || '纽约白银';
            if (this.elements.silverPriceUSD) {
                this.elements.silverPriceUSD.textContent = Utils.formatNumber(silver.current_price);
                this.animateValue(this.elements.silverPriceUSD);
            }
            if (this.elements.silverPriceCNY) {
                this.elements.silverPriceCNY.textContent = Utils.formatNumber(priceCNY);
                this.animateValue(this.elements.silverPriceCNY);
            }
            if (this.elements.silverOpen) this.elements.silverOpen.textContent = Utils.formatNumber(silver.current_price);
            if (this.elements.silverHigh) this.elements.silverHigh.textContent = Utils.formatNumber(silver.low_price);
            if (this.elements.silverLow) this.elements.silverLow.textContent = Utils.formatNumber(silver.high_price);
            
            if (this.elements.silverChange) {
                const changeClass = Utils.getChangeClass(changePercent);
                const changeIcon = Utils.getChangeIcon(changePercent);
                this.elements.silverChange.innerHTML = `
                    <span class="change-value ${changeClass}">${changeIcon} ${Utils.formatPercent(changePercent)}</span>
                `;
            }
            if (this.elements.silverUpdateTime) this.elements.silverUpdateTime.textContent = silver.update_time || '---';
        }
    }

    renderFundList() {
        const container = this.elements.fundList;
        if (!container) return;

        const funds = this.state.funds;
        const fundCodes = Object.keys(funds);
        
        // Filter funds
        let filteredFunds = fundCodes;
        if (this.state.searchQuery) {
            const query = this.state.searchQuery.toLowerCase();
            filteredFunds = fundCodes.filter(code => {
                const fund = funds[code];
                const codeMatch = code.toLowerCase().includes(query);
                const nameMatch = fund.name && fund.name.toLowerCase().includes(query);
                return codeMatch || nameMatch;
            });
        }

        // Empty state
        if (filteredFunds.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <div class="empty-state-title">暂无基金数据</div>
                    <div class="empty-state-description">
                        ${this.state.searchQuery ? '未找到匹配的基金' : '请在设置中添加基金代码'}
                    </div>
                </div>
            `;
            if (this.elements.fundPagination) {
                this.elements.fundPagination.style.display = 'none';
            }
            return;
        }

        // Pagination
        const totalPages = Math.ceil(filteredFunds.length / this.state.itemsPerPage);
        const startIndex = (this.state.currentPage - 1) * this.state.itemsPerPage;
        const endIndex = startIndex + this.state.itemsPerPage;
        const pageFunds = filteredFunds.slice(startIndex, endIndex);

        // Render funds
        let html = '';
        pageFunds.forEach((code, index) => {
            const fund = funds[code];
            if (fund.error) {
                html += `
                    <div class="fund-item error" style="opacity: 0.6;">
                        <div class="fund-code">
                            <span class="fund-code-value">${code}</span>
                            <span class="fund-code-label">代码</span>
                        </div>
                        <div class="fund-info">
                            <div class="fund-name">获取失败</div>
                            <div class="fund-stats">${fund.error}</div>
                        </div>
                        <div class="fund-value">
                            <span class="fund-current-value">---</span>
                            <span class="fund-change neutral">---</span>
                        </div>
                    </div>
                `;
            } else {
                const changeClass = Utils.getChangeClass(fund.change_percent);
                const changeIcon = Utils.getChangeIcon(fund.change_percent);
                html += `
                    <div class="fund-item" style="animation-delay: ${index * 0.05}s">
                        <div class="fund-code">
                            <span class="fund-code-value">${fund.code || code}</span>
                            <span class="fund-code-label">代码</span>
                        </div>
                        <div class="fund-info">
                            <div class="fund-name">${fund.name || '未知基金'}</div>
                            <div class="fund-stats">
                                <span>净值: ${Utils.formatNumber(fund.net_value)}</span>
                                <span>${fund.update_time || ''}</span>
                            </div>
                        </div>
                        <div class="fund-value">
                            <span class="fund-current-value">${Utils.formatNumber(fund.estimated_value)}</span>
                            <span class="fund-change ${changeClass}">${changeIcon} ${Utils.formatPercent(fund.change_percent)}</span>
                        </div>
                    </div>
                `;
            }
        });

        container.innerHTML = html;

        // Update pagination
        if (this.elements.fundPagination && filteredFunds.length > this.state.itemsPerPage) {
            this.elements.fundPagination.style.display = 'flex';
            if (this.elements.paginationInfo) {
                this.elements.paginationInfo.textContent = `${this.state.currentPage} / ${totalPages}`;
            }
            if (this.elements.prevPage) {
                this.elements.prevPage.disabled = this.state.currentPage === 1;
            }
            if (this.elements.nextPage) {
                this.elements.nextPage.disabled = this.state.currentPage === totalPages;
            }
        }
    }

    getTotalPages() {
        const funds = this.state.funds;
        const fundCodes = Object.keys(funds);
        
        let filteredFunds = fundCodes;
        if (this.state.searchQuery) {
            const query = this.state.searchQuery.toLowerCase();
            filteredFunds = fundCodes.filter(code => {
                const fund = funds[code];
                const codeMatch = code.toLowerCase().includes(query);
                const nameMatch = fund.name && fund.name.toLowerCase().includes(query);
                return codeMatch || nameMatch;
            });
        }
        
        return Math.ceil(filteredFunds.length / this.state.itemsPerPage);
    }

    async addFund() {
        const input = this.elements.newFundCode;
        const code = input ? input.value.trim() : '';
        
        if (!code) {
            this.showToast('请输入基金代码', 'warning');
            return;
        }

        // Validate code format (6 digits)
        if (!/^\d{6}$/.test(code)) {
            this.showToast('基金代码格式错误，请输入6位数字', 'warning');
            return;
        }

        const localFundCodes = Utils.localStorageGet('fund_codes', []);
        if (localFundCodes.includes(code)) {
            this.showToast('该基金代码已存在', 'warning');
            return;
        }

        try {
            const response = await api.addFundCode(code);
            if (response.success) {
                localFundCodes.push(code);
                Utils.localStorageSet('fund_codes', localFundCodes);
                this.showToast(response.message || '基金添加成功', 'success');
                if (input) input.value = '';
                await this.loadFunds();
            } else {
                throw new Error(response.error || '添加失败');
            }
        } catch (error) {
            this.showToast(error.message || '添加基金失败', 'error');
        }
    }

    // Auto refresh
    startAutoRefresh() {
        this.stopAutoRefresh();
        if (this.state.autoRefresh) {
            this.state.refreshTimer = setInterval(() => {
                this.loadPreciousMetals();
                this.loadFunds();
                this.loadExchangeRate();
                this.state.lastUpdate = new Date();
                this.updateLastUpdateTime();
            }, this.state.refreshInterval * 1000);
        }
    }

    stopAutoRefresh() {
        if (this.state.refreshTimer) {
            clearInterval(this.state.refreshTimer);
            this.state.refreshTimer = null;
        }
    }

    // Connection status
    updateConnectionStatus(online, reason = null) {
        this.state.isConnected = online;
        const dot = this.elements.connectionStatus;
        const text = this.elements.connectionText;
        
        if (dot) {
            dot.className = `status-dot ${online ? 'online' : 'offline'}`;
        }
        if (text) {
            if (online) {
                text.textContent = reason || '已连接';
            } else {
                text.textContent = reason || '已断开';
            }
        }
    }

    onOnline() {
        this.updateConnectionStatus(true);
        this.showToast('网络已连接', 'success');
        this.manualRefresh();
    }

    onOffline() {
        this.updateConnectionStatus(false);
        this.showToast('网络已断开', 'error');
    }

    // UI Updates
    updateLastUpdateTime() {
        const el = this.elements.lastUpdate;
        if (el && this.state.lastUpdate) {
            el.textContent = `更新: ${Utils.formatTime(this.state.lastUpdate)}`;
        }
    }

    updateExchangeRateDisplay() {
        const item = this.elements.exchangeRateItem;
        const text = this.elements.exchangeRateText;
        
        if (this.exchangeRateInfo && this.exchangeRateInfo.source !== 'Fixed') {
            if (item) {
                item.style.display = 'flex';
            }
            if (text) {
                text.textContent = `USD/CNY: ${this.exchangeRate.toFixed(4)}`;
            }
        } else {
            if (item) {
                item.style.display = 'none';
            }
        }
    }

    animateValue(element) {
        if (!element) return;
        element.classList.add('updating');
        setTimeout(() => element.classList.remove('updating'), 500);
    }

    showLoading(show) {
        const overlay = this.elements.loadingOverlay;
        if (overlay) {
            if (show) {
                overlay.classList.add('active');
            } else {
                overlay.classList.remove('active');
            }
        }
    }

    showToast(message, type = 'info') {
        const container = this.elements.toastContainer;
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Sidebar & Settings
    openSidebar() {
        const sidebar = this.elements.sidebar;
        const overlay = this.elements.sidebarOverlay;
        if (sidebar) sidebar.classList.add('active');
        if (overlay) overlay.classList.add('active');
    }

    closeSidebar() {
        const sidebar = this.elements.sidebar;
        const overlay = this.elements.sidebarOverlay;
        if (sidebar) sidebar.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
    }

    closeSettings() {
        const panel = this.elements.settingsPanel;
        if (panel) panel.classList.remove('active');
    }

    // Theme
    applyTheme() {
        document.body.classList.toggle('dark-mode', this.state.darkMode);
    }

    // Settings persistence
    loadSettings() {
        const settings = Utils.localStorageGet('app_settings');
        if (settings) {
            this.state.autoRefresh = settings.autoRefresh !== false;
            this.state.refreshInterval = settings.refreshInterval || 3;
            this.state.darkMode = settings.darkMode !== false;
        }

        // Apply settings to UI
        if (this.elements.autoRefresh) {
            this.elements.autoRefresh.checked = this.state.autoRefresh;
        }
        if (this.elements.refreshInterval) {
            this.elements.refreshInterval.value = this.state.refreshInterval;
        }
        if (this.elements.darkMode) {
            this.elements.darkMode.checked = this.state.darkMode;
        }

        this.applyTheme();
    }

    saveSettings() {
        Utils.localStorageSet('app_settings', {
            autoRefresh: this.state.autoRefresh,
            refreshInterval: this.state.refreshInterval,
            darkMode: this.state.darkMode
        });
    }

    // Alert Panel Methods
    async openAlertPanel() {
        const panel = this.elements.alertPanel;
        const overlay = this.elements.alertOverlay;
        if (panel) {
            panel.classList.add('open');
            if (overlay) overlay.classList.add('active');
            await this.loadAlertConfiguration();
            await this.loadAlertHistory(24);
        }
    }

    closeAlertPanel() {
        const panel = this.elements.alertPanel;
        const overlay = this.elements.alertOverlay;
        if (panel) panel.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
    }

    async loadAlertConfiguration() {
        try {
            const response = await api.getAlertConfig();
            if (response.success) {
                this.alertConfig = response.data;
                const localRecipients = Utils.localStorageGet('alert_recipients', []);
                this.alertRecipients = localRecipients.length > 0 ? localRecipients : (response.data.recipients || []);
                this.populateAlertForm();
                this.renderEmailList();
            } else {
                this.showToast('加载预警配置失败', 'error');
            }
        } catch (error) {
            console.error('Load alert config failed:', error);
            this.showToast('加载预警配置失败', 'error');
        }
    }

    populateAlertForm() {
        const config = this.alertConfig;
        if (!config) return;

        if (this.elements.enableGoldAlert) this.elements.enableGoldAlert.checked = config.enable_gold_monitor;
        if (this.elements.enableSilverAlert) this.elements.enableSilverAlert.checked = config.enable_gold_monitor;
        if (this.elements.enableFundAlert) this.elements.enableFundAlert.checked = config.enable_fund_monitor;
        if (this.elements.goldThreshold) this.elements.goldThreshold.value = config.gold_threshold;
        if (this.elements.silverThreshold) this.elements.silverThreshold.value = config.silver_threshold;
        if (this.elements.fundThreshold) this.elements.fundThreshold.value = config.fund_threshold;
        if (this.elements.alertCooldown) this.elements.alertCooldown.value = config.alert_cooldown;
    }

    async saveAlertConfiguration() {
        const btn = this.elements.saveAlertConfig;
        if (btn) {
            btn.disabled = true;
            btn.textContent = '保存中...';
        }

        try {
            const config = {
                enable_gold_monitor: this.elements.enableGoldAlert?.checked,
                enable_silver_monitor: this.elements.enableSilverAlert?.checked,
                enable_fund_monitor: this.elements.enableFundAlert?.checked,
                gold_threshold: parseFloat(this.elements.goldThreshold?.value),
                silver_threshold: parseFloat(this.elements.silverThreshold?.value),
                fund_threshold: parseFloat(this.elements.fundThreshold?.value),
                alert_cooldown: parseInt(this.elements.alertCooldown?.value)
            };

            const response = await api.updateAlertConfig(config);
            if (response.success) {
                this.alertConfig = { ...this.alertConfig, ...config };
                this.showToast('预警配置保存成功', 'success');
            } else {
                throw new Error(response.error || '保存失败');
            }
        } catch (error) {
            console.error('Save alert config failed:', error);
            this.showToast('保存预警配置失败', 'error');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.textContent = '保存配置';
            }
        }
    }

    renderEmailList() {
        const container = this.elements.emailList;
        if (!container) return;

        if (this.alertRecipients.length === 0) {
            container.innerHTML = '<div class="email-list-empty">暂无邮箱地址</div>';
            return;
        }

        let html = '';
        this.alertRecipients.forEach((email, index) => {
            html += `
                <div class="email-item">
                    <div class="email-item-info">
                        <span class="email-item-icon">📧</span>
                        <span class="email-item-address">${email}</span>
                    </div>
                    <button class="email-item-delete" data-email="${email}" data-index="${index}">
                        <svg viewBox="0 0 24 24" width="18" height="18">
                            <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                        </svg>
                    </button>
                </div>
            `;
        });

        container.innerHTML = html;

        container.querySelectorAll('.email-item-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const email = e.currentTarget.dataset.email;
                this.removeEmailRecipient(email);
            });
        });
    }

    async addEmailRecipient() {
        const input = this.elements.newEmail;
        const email = input?.value.trim();

        if (!email) {
            this.showToast('请输入邮箱地址', 'warning');
            return;
        }

        if (!api.validateEmail(email)) {
            this.showToast('邮箱格式不正确', 'warning');
            return;
        }

        if (this.alertRecipients.includes(email)) {
            this.showToast('该邮箱已存在', 'warning');
            return;
        }

        try {
            const response = await api.addAlertRecipient(email);
            if (response.success) {
                this.alertRecipients.push(email);
                Utils.localStorageSet('alert_recipients', this.alertRecipients);
                this.renderEmailList();
                if (input) input.value = '';
                this.showToast('邮箱添加成功', 'success');
            } else {
                throw new Error(response.error || '添加失败');
            }
        } catch (error) {
            console.error('Add email recipient failed:', error);
            this.showToast('添加邮箱失败', 'error');
        }
    }

    async removeEmailRecipient(email) {
        try {
            const response = await api.deleteAlertRecipient(email);
            if (response.success) {
                this.alertRecipients = this.alertRecipients.filter(e => e !== email);
                Utils.localStorageSet('alert_recipients', this.alertRecipients);
                this.renderEmailList();
                this.showToast('邮箱删除成功', 'success');
            } else {
                throw new Error(response.error || '删除失败');
            }
        } catch (error) {
            console.error('Remove email recipient failed:', error);
            this.showToast('删除邮箱失败', 'error');
        }
    }

    async sendTestEmail() {
        if (this.alertRecipients.length === 0) {
            this.showToast('请先添加邮箱地址', 'warning');
            return;
        }

        const btn = this.elements.testEmailBtn;
        if (btn) {
            btn.disabled = true;
            btn.textContent = '发送中...';
        }

        try {
            const recipient = this.alertRecipients[0];
            const response = await api.sendTestEmail(recipient);
            if (response.success) {
                this.showToast('测试邮件发送成功，请检查邮箱', 'success');
            } else {
                throw new Error(response.error || '发送失败');
            }
        } catch (error) {
            console.error('Send test email failed:', error);
            this.showToast('发送测试邮件失败', 'error');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.textContent = '发送测试邮件';
            }
        }
    }

    async loadAlertHistory(hours = 24) {
        try {
            const response = await api.getAlertHistory(hours);
            if (response.success) {
                this.alertHistoryData = response.data || [];
                this.renderAlertHistory();
            }
        } catch (error) {
            console.error('Load alert history failed:', error);
        }
    }

    renderAlertHistory() {
        const container = this.elements.alertHistory;
        if (!container) return;

        if (this.alertHistoryData.length === 0) {
            container.innerHTML = '<div class="alert-history-empty">暂无预警记录</div>';
            return;
        }

        let html = '';
        this.alertHistoryData.forEach((alert, index) => {
            const isPriceAlert = alert.type === 'price_threshold';
            const alertClass = isPriceAlert ? 'price-alert' : 'fund-alert';
            const timeStr = Utils.formatDateTime(alert.alert_time);
            
            html += `
                <div class="alert-history-item ${alertClass}" style="animation-delay: ${index * 0.05}s">
                    <div class="alert-history-header">
                        <span class="alert-history-type">
                            ${isPriceAlert ? '🔔' : '📊'} ${alert.asset_name || alert.fund_name || '预警'}
                        </span>
                        <span class="alert-history-time">${timeStr}</span>
                    </div>
                    <div class="alert-history-message">${alert.message}</div>
                    <div class="alert-history-details">
                        ${isPriceAlert ? `
                            <div class="alert-history-detail">
                                <span>当前价格</span>
                                <span>${alert.current_price?.toFixed(2)} 元/克</span>
                            </div>
                            <div class="alert-history-detail">
                                <span>预警阈值</span>
                                <span>${alert.threshold?.toFixed(2)} 元/克</span>
                            </div>
                        ` : `
                            <div class="alert-history-detail">
                                <span>当前净值</span>
                                <span>${alert.current_value?.toFixed(4)}</span>
                            </div>
                            <div class="alert-history-detail">
                                <span>涨跌幅</span>
                                <span>${Utils.formatPercent(alert.change_percent)}</span>
                            </div>
                            <div class="alert-history-detail">
                                <span>预警阈值</span>
                                <span>${alert.threshold}%</span>
                            </div>
                        `}
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    // Service Worker
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('sw.js').then(registration => {
                    console.log('Service Worker registered:', registration);
                    
                    registration.onupdatefound = () => {
                        const installingWorker = registration.installing;
                        installingWorker.onstatechange = () => {
                            if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                this.showToast('有新版本可用，刷新页面更新', 'warning');
                            }
                        };
                    };
                }).catch(err => {
                    console.log('Service Worker registration failed:', err);
                });
            });
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FinancialMonitorApp();
});
