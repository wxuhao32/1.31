# 📱 APK 构建指南

## 方法一：使用 PWABuilder（推荐 - 最简单）

### 步骤：

1. **访问 PWABuilder 网站**
   - 打开：https://www.pwabuilder.com/

2. **输入 PWA URL**
   ```
   https://financial-monitor-api.onrender.com
   ```

3. **上传 Manifest**
   - 如果有自定义 manifest.json，可以上传
   - 或让 PWABuilder 自动检测

4. **配置应用信息**
   - 应用名称：金融价格监控
   - 包名：com.financialmonitor.app
   - 版本号：1.0.0

5. **选择图标**
   - 上传图标或使用默认

6. **生成 APK**
   - 点击 "Generate APK"
   - 等待构建完成（约 1-2 分钟）
   - 下载 APK 文件

---

## 方法二：使用 Bubblewrap

### 步骤：

1. **访问 Bubblewrap**
   - 打开：https://bubblewrap.dev/

2. **安装 Bubblewrap CLI**（可选）
   ```bash
   npm install -g @anthropic/bubblewrap
   ```

3. **输入 URL 和配置**
   - PWA URL: https://financial-monitor-api.onrender.com
   - 应用名称: 金融价格监控
   - 包名: com.financialmonitor.app

4. **生成签名**
   - 使用 Web 界面自动生成密钥

5. **构建 APK**
   - 点击 Build
   - 下载生成的 APK

---

## 方法三：使用 GoNative.io

### 步骤：

1. **访问 GoNative**
   - 打开：https://gonative.io/

2. **注册账号**（免费）

3. **创建新应用**
   - 输入：https://financial-monitor-api.onrender.com
   - 配置应用信息

4. **构建**
   - 选择免费套餐
   - 生成并下载 APK

---

## 方法四：使用 PWA to APK 在线工具

### 可用工具：

1. **PWA to APK Converter**
   - 网址：https://pwabuilder.com/

2. **App Maker**
   - 网址：https://apps.mobi/

3. **Web2APK**
   - 网址：https://www.web2apk.com/

---

## 快速构建（推荐流程）

### 最快方式 - 3 分钟获得 APK：

```
1. 打开 https://www.pwabuilder.com/
2. 输入: https://financial-monitor-api.onrender.com
3. 点击 Generate
4. 等待 1-2 分钟
5. 下载 APK
```

### APK 安装说明：

1. **启用未知来源**
   - Android 设置 > 安全 > 允许未知来源

2. **安装 APK**
   - 下载 APK 到手机
   - 点击文件安装

3. **首次运行**
   - 允许网络权限
   - 应用会像原生 App 一样运行

---

## PWA 特性说明

使用上述工具生成的 APK 会保留以下特性：

- ✅ 离线访问
- ✅ 添加到主屏幕
- ✅ 全屏显示
- ✅ 无浏览器地址栏
- ✅ 自定义图标和名称
- ✅ 推送通知支持
- ✅ 自动更新

---

## 注意事项

1. **HTTPS 必需**
   - PWA 转 APK 需要 HTTPS
   - 你的网站已经支持

2. **图标很重要**
   - 建议使用 512x512 的高质量图标
   - 可以使用项目中的 generate-icons.html 生成

3. **签名**
   - 在线工具会自动签名
   - 也可以使用自己的密钥签名

4. **测试**
   - 先在模拟器测试
   - 然后在真机测试

5. **更新**
   - 更新网站内容
   - APK 会自动获取最新内容
   - 如需更新 App 本身，需重新构建

---

## 自定义配置（可选）

### 创建自定义 manifest.json

如果需要更多控制，可以创建自定义配置：

```json
{
  "name": "金融价格监控",
  "short_name": "金融监控",
  "description": "实时监控贵金属和基金价格",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#4f46e5",
  "orientation": "portrait",
  "icons": [
    {
      "src": "https://financial-monitor-api.onrender.com/assets/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

---

## 获取帮助

如有问题：
- PWABuilder 支持：https://www.pwabuilder.com/support
- 查看文档：https://developer.chrome.com/docs/pwa/
- PWA 测试：访问 https://financial-monitor-api.onrender.com/pwa-test.html
