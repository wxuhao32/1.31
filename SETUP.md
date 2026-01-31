# 部署到Render前的设置指南

## 首次部署设置

### 1. 复制配置文件

在部署到Render后，需要在服务器上创建实际的配置文件：

```bash
cp config/config.ini.example config/config.ini
cp config/fund_list.txt.example config/fund_list.txt
cp config/email_list.txt.example config/email_list.txt
```

### 2. 配置邮件服务器

编辑 `config/config.ini` 中的邮件设置：

```ini
[email]
smtp_server = smtp.qq.com
smtp_port = 465
sender_email = your_email@qq.com
sender_password = your_auth_code
```

**注意**：
- QQ邮箱需要使用授权码，不是密码
- 获取授权码：QQ邮箱 → 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务 → 生成授权码

### 3. 添加基金代码

编辑 `config/fund_list.txt`，每行一个基金代码：

```
001123
110007
004815
```

### 4. 配置收件人邮箱

编辑 `config/email_list.txt`，每行一个邮箱地址：

```
recipient1@example.com
recipient2@example.com
```

### 5. 设置价格阈值

在 `config/config.ini` 中设置预警阈值：

```ini
[gold]
price_threshold_gold = 2800
price_threshold_silver = 32

[fund]
change_percent_threshold = 5
```

## Render环境变量配置

在Render Web Service页面添加以下环境变量：

| 变量名 | 说明 | 示例值 |
|---------|------|---------|
| `SMTP_SERVER` | SMTP服务器地址 | smtp.qq.com |
| `SMTP_PORT` | SMTP端口 | 465 |
| `SENDER_EMAIL` | 发件邮箱 | your@qq.com |
| `SENDER_PASSWORD` | 邮箱授权码 | your_auth_code |

**注意**：环境变量会覆盖config.ini中的设置
