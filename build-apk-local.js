const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const PWA_URL = 'https://financial-monitor-api.onrender.com';
const PROJECT_DIR = path.join(__dirname, 'android-app');

console.log('=================================');
console.log('  PWA to APK 构建工具');
console.log('=================================\n');

function downloadFile(url, dest) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(dest);
        https.get(url, (response) => {
            response.pipe(file);
            file.on('finish', () => {
                file.close();
                resolve();
            });
        }).on('error', (err) => {
            fs.unlink(dest);
            reject(err);
        });
    });
}

function openBrowser(url) {
    const platform = process.platform;
    let command;
    
    if (platform === 'win32') {
        command = `start ${url}`;
    } else if (platform === 'darwin') {
        command = `open ${url}`;
    } else {
        command = `xdg-open ${url}`;
    }
    
    exec(command, (error) => {
        if (error) console.error('无法打开浏览器:', error);
    });
}

async function checkDependencies() {
    console.log('检查依赖...');
    
    const commands = ['java', 'gradle'];
    const missing = [];
    
    for (const cmd of commands) {
        try {
            exec(`${cmd} --version`, (error) => {
                if (error) missing.push(cmd);
            });
        } catch (e) {
            missing.push(cmd);
        }
    }
    
    if (missing.length > 0) {
        console.log(`缺少: ${missing.join(', ')}`);
        console.log('\n将使用在线构建方式...\n');
        return false;
    }
    
    console.log('依赖检查通过！');
    return true;
}

async function main() {
    console.log(`PWA URL: ${PWA_URL}`);
    console.log(`项目目录: ${PROJECT_DIR}\n`);
    
    const hasDependencies = await checkDependencies();
    
    if (!hasDependencies) {
        console.log('正在打开在线构建工具...');
        console.log('\n请在浏览器中：');
        console.log('1. 输入 URL: ' + PWA_URL);
        console.log('2. 配置应用信息');
        console.log('3. 点击生成 APK');
        console.log('4. 等待下载');
        
        openBrowser('https://www.pwabuilder.com/');
        return;
    }
    
    console.log('开始本地构建...\n');
    
    try {
        console.log('步骤 1/4: 安装依赖...');
        exec('npm install -g @capacitor/cli @capacitor/android', (error, stdout, stderr) => {
            if (error) {
                console.error('安装失败:', error);
                return;
            }
            console.log('依赖安装完成');
            
            console.log('\n步骤 2/4: 初始化项目...');
            exec(`npx cap init "金融价格监控" com.financialmonitor.app --web-dir=frontend`, { cwd: __dirname }, (error) => {
                if (error) {
                    console.error('初始化失败:', error);
                    return;
                }
                console.log('项目初始化完成');
                
                console.log('\n步骤 3/4: 同步 PWA...');
                exec('npx cap sync android', { cwd: __dirname }, (error) => {
                    if (error) {
                        console.error('同步失败:', error);
                        return;
                    }
                    console.log('PWA 同步完成');
                    
                    console.log('\n步骤 4/4: 构建 APK...');
                    exec('npx cap build android', { cwd: __dirname }, (error, stdout, stderr) => {
                        if (error) {
                            console.error('构建失败:', error);
                            console.log('\n尝试使用在线构建方式...');
                            openBrowser('https://www.pwabuilder.com/');
                            return;
                        }
                        console.log('\n=================================');
                        console.log('  APK 构建成功！');
                        console.log('=================================\n');
                        console.log('APK 位置:');
                        console.log(path.join(__dirname, 'android', 'app', 'build', 'outputs', 'apk', 'debug', 'app-debug.apk'));
                        console.log('\n可以直接安装到 Android 手机！');
                    });
                });
            });
        });
    } catch (error) {
        console.error('构建出错:', error);
        console.log('\n使用在线构建方式...');
        openBrowser('https://www.pwabuilder.com/');
    }
}

main();
