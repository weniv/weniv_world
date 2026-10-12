// 대표 이미지(1580×832)·상품 소개 이미지(860px 폭을 2배로 1720px)를 만든다: node store/render.mjs
// 먼저 node store/capture.mjs 로 실제 앱 화면(store/raw)을 찍어 둔다.
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const dir = fileURLToPath(new URL('./', import.meta.url));
const out = path.join(dir, '업로드');
const browser = await chromium.launch({ channel: 'chrome' });

const hero = await browser.newPage({ viewport: { width: 1580, height: 832 }, deviceScaleFactor: 1 });
await hero.goto(pathToFileURL(path.join(dir, '대표_1580.html')).href);
await hero.evaluate(() => document.fonts.ready);
await hero.waitForTimeout(300);
await hero.screenshot({ path: path.join(out, '1_대표이미지_1580x832.jpg'), type: 'jpeg', quality: 92 });

const detail = await browser.newPage({ viewport: { width: 860, height: 1000 }, deviceScaleFactor: 2 });
await detail.goto(pathToFileURL(path.join(dir, '상세.html')).href);
await detail.evaluate(() => document.fonts.ready);
await detail.waitForTimeout(300);
await detail.screenshot({ path: path.join(out, '2_상품소개이미지_1720px.jpg'), type: 'jpeg', quality: 88, fullPage: true });

await browser.close();
console.log('store/업로드/1_대표이미지_1580x832.jpg, 2_상품소개이미지_1720px.jpg');
