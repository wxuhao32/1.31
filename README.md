# 金融价格监控系统

贵金属和基金价格实时监控与预警系统

## 功能特性

- 贵金属（黄金、白银）实时价格监控
- 基金净值实时查询
- 价格预警功能，支持邮件通知
- 实时汇率转换（USD/CNY）
- 响应式设计，支持移动端
- PWA支持，可安装到手机主屏幕

## 本地运行

### 环境要求

- Python 3.11+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

1. 复制配置文件：
```bash
cp config/fund_list.txt.example config/fund_list.txt
cp config/email_list.txt.example config/email_list.txt
```

2. 修改 `config/config.ini`：
- 设置SMTP邮件服务器配置
- 配置价格阈值
- 设置监控开关

### 启动服务器

```bash
python api_server.py
```

访问：http://localhost:5000

## Render部署

### 前置要求

- GitHub账户
- Render账户（免费）

### 部署步骤

1. **创建GitHub仓库**

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

2. **在Render上部署**

- 访问 https://render.com
- 注册并登录
- 点击 "New +"
- 选择 "Web Service"
- 连接到GitHub仓库
- 配置：
  - Name: `financial-monitor-api`
  - Region: Singapore (或离你最近的)
  - Branch: `main`
  - Runtime: `Python 3`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `gunicorn --workers 4 --threads 8 --bind 0.0.0.0:$PORT --timeout 120 api_server:app`

3. **配置环境变量**

在Render Web Service页面，添加以下环境变量：

| 变量名 | 说明 | 示例 |
|---------|------|------|
| `SMTP_SERVER` | SMTP服务器地址 | smtp.qq.com |
| `SMTP_PORT` | SMTP端口 | 465 |
| `SENDER_EMAIL` | 发件邮箱 | your@email.com |
| `SENDER_PASSWORD` | 邮箱密码/授权码 | yourpassword |

4. **获取API地址**

部署完成后，Render会提供一个类似以下的URL：
```
https://financial-monitor-api.onrender.com
```

5. **更新前端API地址**

编辑 `frontend/js/api.js`，修改 `API_BASE_URL`：

```javascript
// 开发环境
const API_BASE_URL = 'http://localhost:5000/api';

// 生产环境（Render）
const API_BASE_URL = 'https://financial-monitor-api.onrender.com/api';
```

6. **部署前端（可选）**

将 `frontend` 目录部署到 Vercel 或 Netlify：

- Vercel: https://vercel.com
- Netlify: https://netlify.com

## 移动APP封装

### 使用Capacitor（推荐）

1. **安装依赖**

```bash
cd mobile-app
npm install
```

2. **配置服务器地址**

编辑 `mobile-app/capacitor.config.json`：

```json
{
  "appId": "com.financial.monitor",
  "appName": "金融监控",
  "webDir": "../frontend",
  "server": {
    "url": "https://financial-monitor-api.onrender.com"
  }
}
```

3. **同步到Android**

```bash
npx cap sync android
```

4. **打开Android Studio**

```bash
npx cap open android
```

5. **构建APK**

在Android Studio中：
- Build → Build Bundle(s) / APK(s) → Build APK(s)
- APK文件位于：`mobile-app/android/app/build/outputs/apk/`

### iOS打包

需要Mac电脑和Xcode：

```bash
npx cap sync ios
npx cap open ios
```

在Xcode中构建并发布到App Store。

### PWA安装（无需打包）

在手机浏览器中打开应用：

- **iOS Safari**: 分享按钮 → 添加到主屏幕
- **Android Chrome**: 菜单 → 安装应用

## API文档

### 贵金属价格
```
GET /api/market/precious-metals
```

### 基金数据
```
GET /api/market/funds
GET /api/market/fund/{fund_code}
```

### 预警配置
```
GET /api/alert/config
POST /api/alert/config
POST /api/alert/test-email
GET /api/alert/history
```

### 汇率转换
```
GET /api/exchange/rate
POST /api/exchange/refresh
GET /api/exchange/convert?price=2000&direction=usd_oz_to_cny_gram
GET /api/exchange/validate
```

## 故障排除

### 邮件发送失败

1. 检查SMTP配置是否正确
2. QQ邮箱需要使用授权码，不是密码
3. 检查端口：465使用SSL，587使用STARTTLS

### 汇率获取失败

1. 检查网络连接
2. 系统会自动尝试多个API源
3. 汇率数据缓存1小时，可手动刷新

### 部署到Render后无法访问

1. 检查服务是否启动（Render Dashboard）
2. 查看日志确认是否有错误
3. 确认端口配置正确（Render会自动分配PORT环境变量）

## 许可证

MIT License
