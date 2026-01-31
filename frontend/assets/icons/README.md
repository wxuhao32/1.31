# PWA 图标说明

## 方法一：使用在线工具（推荐）

1. 打开 [convertio.co](https://convertio.co/svg-png/)
2. 上传 `icon.svg` 文件
3. 选择 PNG 格式
4. 生成并下载所需尺寸的图标：
   - 16x16
   - 32x32
   - 72x72
   - 96x96
   - 128x128
   - 144x144
   - 152x152
   - 192x192
   - 384x384
   - 512x512

## 方法二：使用本地图标生成器

1. 用浏览器打开 `generate-icons.html`
2. 点击"下载所有图标"按钮
3. 所有图标会自动下载到你的下载文件夹

## 方法三：使用命令行工具（需要 Node.js）

```bash
cd frontend/assets/icons
npm install sharp
node generate-icons.js
```

## 图标放置位置

将生成的图标文件放置在以下位置：
```
frontend/
├── assets/
│   └── icons/
│       ├── icon-16.png
│       ├── icon-32.png
│       ├── icon-72.png
│       ├── icon-96.png
│       ├── icon-128.png
│       ├── icon-144.png
│       ├── icon-152.png
│       ├── icon-192.png
│       ├── icon-384.png
│       ├── icon-512.png
│       └── icon.svg
```

## 临时解决方案

如果没有图标，PWA 仍然可以工作，只是不会显示自定义图标。可以使用以下临时的 manifest.json 配置：

```json
{
  "icons": [
    {
      "src": "https://via.placeholder.com/192/4f46e5/ffffff?text=📊",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "https://via.placeholder.com/512/4f46e5/ffffff?text=📊",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

## 注意事项

- 确保图标是正方形
- 建议使用圆角图标（本设计使用了约 22% 的圆角）
- 背景色为渐变色：#4f46e5 到 #7c3aed
