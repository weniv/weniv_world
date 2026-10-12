// 앱 아이콘(resources/icon.png, 1024px)을 위니브월드 로고(assets/img/icon/icon-logo.svg)로 만든다.
// 로고를 바꿨을 때만 다시 돌린다: node scripts/icon.mjs (Chrome 필요)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const desktop = fileURLToPath(new URL('../', import.meta.url));
const svg = fs.readFileSync(path.join(desktop, '../assets/img/icon/icon-logo.svg'), 'utf8');
const size = 1024;
const browser = await chromium.launch({ channel: 'chrome' });
const page = await browser.newPage({ viewport: { width: size, height: size } });
await page.setContent(
    `<html><body style="margin:0;background:transparent">${svg.replace('<svg ', `<svg style="display:block;width:${size}px;height:${size}px" `)}</body></html>`,
);
await page.screenshot({ path: path.join(desktop, 'resources/icon.png'), omitBackground: true });
await browser.close();
console.log('resources/icon.png');
