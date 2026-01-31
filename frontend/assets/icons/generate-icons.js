const fs = require('fs');
const path = require('path');

const sizes = [16, 32, 72, 96, 128, 144, 152, 192, 384, 512];

const svgTemplate = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="110" fill="url(#bg-gradient)"/>
  <g transform="translate(106, 106)">
    <text x="150" y="280" font-family="Arial, sans-serif" font-size="200" text-anchor="middle" fill="#ffffff" font-weight="bold">📊</text>
  </g>
</svg>`;

const assetsDir = path.join(__dirname, '..');
const iconsDir = path.join(assetsDir, 'icons');

if (!fs.existsSync(iconsDir)) {
    fs.mkdirSync(iconsDir, { recursive: true });
}

sizes.forEach(size => {
    const svgContent = svgTemplate.replace('viewBox="0 0 512 512"', `viewBox="0 0 512 512" width="${size}" height="${size}"`);
    const filename = path.join(iconsDir, `icon-${size}.png`);
    
    console.log(`Icon ${size}x${size} will be generated at: ${filename}`);
    console.log('Note: You need to convert SVG to PNG using an image processing tool like sharp, canvas, or online converter');
});

console.log('\nIcon configuration complete!');
console.log('\nTo convert SVG icons to PNG, you can:');
console.log('1. Use an online tool: https://convertio.co/svg-png/');
console.log('2. Use Node.js with sharp: npm install sharp');
console.log('3. Use ImageMagick: convert icon.svg icon.png');
