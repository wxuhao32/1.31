@echo off
chcp 65001 >nul
title APK 快速构建工具
color 0A

cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║           📱 金融价格监控 - APK 快速构建工具               ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 正在准备构建环境...
echo.

set PWA_URL=https://financial-monitor-api.onrender.com

:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                    选择 APK 构建方式                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo   [1] PWABuilder    - 推荐，最快（2-3 分钟）
echo   [2] Bubblewrap     - 功能强大
echo   [3] GoNative      - 专业版
echo   [4] 查看完整指南
echo   [0] 退出
echo.
set /p choice="请选择 (1-4): "

if "%choice%"=="1" goto pwabuilder
if "%choice%"=="2" goto bubblewrap
if "%choice%"=="3" goto gonative
if "%choice%"=="4" goto guide
if "%choice%"=="0" goto end

echo.
echo 无效选择，请重新输入
timeout /t 2 >nul
goto menu

:pwabuilder
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo   正在打开 PWABuilder...
echo ═══════════════════════════════════════════════════════════
echo.
echo 📋 你的 PWA URL: %PWA_URL%
echo.
echo 📌 步骤说明:
echo    1. 网页会自动打开
echo    2. 输入或粘贴上面的 URL
echo    3. 点击 Generate APK
echo    4. 等待 1-2 分钟
echo    5. 下载 APK 文件
echo.
pause
start https://www.pwabuilder.com/
goto end

:bubblewrap
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo   正在打开 Bubblewrap...
echo ═══════════════════════════════════════════════════════════
echo.
echo 📋 你的 PWA URL: %PWA_URL%
echo.
echo 📌 步骤说明:
echo    1. 网页会自动打开
echo    2. 注册或登录 Google 账号
echo    3. 输入 PWA URL
echo    4. 配置应用信息
echo    5. 生成并下载 APK
echo.
pause
start https://bubblewrap.dev/
goto end

:gonative
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo   正在打开 GoNative...
echo ═══════════════════════════════════════════════════════════
echo.
echo 📋 你的 PWA URL: %PWA_URL%
echo.
echo 📌 步骤说明:
echo    1. 网页会自动打开
echo    2. 注册免费账号
echo    3. 创建新应用
echo    4. 输入 PWA URL
echo    5. 构建并下载 APK
echo.
pause
start https://gonative.io/
goto end

:guide
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo   打开完整构建指南...
echo ═══════════════════════════════════════════════════════════
echo.
pause
start notepad APK-BUILD-GUIDE.md
goto end

:end
cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                    构建完成！                              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 💡 提示:
echo    - APK 下载后可直接安装到 Android 手机
echo    - 需要开启"未知来源"安装权限
echo    - 应用会自动获取最新数据
echo.
echo 如需再次构建，请重新运行此脚本
echo.
pause
