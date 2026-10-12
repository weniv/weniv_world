// 설치판 주소 처리(protocol.cjs): 앱 파일·인터넷 대신 쓸 파일을 돌려주고, 폴더 밖은 막는다
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import os from 'node:os';
import path from 'node:path';
import { test } from 'node:test';

const require = createRequire(import.meta.url);
const { appResponse, loadOfflineRoutes, offlineResponse, safeJoin } = require('../protocol.cjs');

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'weniv-world-protocol-'));
const appDir = path.join(tmp, 'app');
const vendorDir = path.join(tmp, 'vendor');
const write = (file, text) => {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, text);
};
write(path.join(appDir, 'index.html'), '<h1>world</h1>');
write(path.join(appDir, 'assets/py/runner.py'), 'print(1)');
write(path.join(appDir, 'assets/data/story/story1.md'), '# 1편');
write(path.join(tmp, 'secret.txt'), 'secret');
write(path.join(vendorDir, 'pyodide/pyodide.asm.wasm'), 'wasm');
write(path.join(vendorDir, 'fonts/source-code-pro.css'), '@font-face{}');
const routes = [
    { prefix: 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/', dir: 'pyodide' },
    { prefix: 'https://fonts.googleapis.com/css2?family=Source+Code+Pro', file: 'fonts/source-code-pro.css' },
];
write(path.join(vendorDir, 'offline.json'), JSON.stringify({ routes }));

test('앱 주소는 app 폴더 파일 (쿼리 무시, / 는 index.html)', async () => {
    let res = appResponse(appDir, 'weniv-world://app/');
    assert.equal(res.status, 200);
    assert.match(res.headers.get('content-type'), /text\/html/);
    assert.equal(await res.text(), '<h1>world</h1>');
    res = appResponse(appDir, 'weniv-world://app/assets/py/runner.py?v=2026.10.05.1');
    assert.equal(await res.text(), 'print(1)');
    res = appResponse(appDir, 'weniv-world://app/assets/data/story/story1.md');
    assert.match(res.headers.get('content-type'), /text\/markdown/);
    assert.equal(appResponse(appDir, 'weniv-world://app/none.js').status, 404);
    assert.equal(appResponse(appDir, 'weniv-world://other/index.html').status, 404);
    assert.equal(appResponse(appDir, 'weniv-world://app/assets').status, 404);
});

test('app 폴더 밖은 열지 않는다', () => {
    assert.equal(appResponse(appDir, 'weniv-world://app/%2e%2e/secret.txt').status, 404);
    assert.equal(appResponse(appDir, 'weniv-world://app/..%2Fsecret.txt').status, 404);
    assert.equal(safeJoin(appDir, '../secret.txt'), null);
    assert.equal(safeJoin(appDir, ''), null);
    assert.equal(safeJoin(appDir, 'index.html'), path.join(appDir, 'index.html'));
});

test('목록에 있는 인터넷 주소는 vendor 파일 (CORS 허용), 없는 주소는 null', async () => {
    assert.deepEqual(loadOfflineRoutes(vendorDir), routes);
    assert.deepEqual(loadOfflineRoutes(path.join(tmp, 'none')), []);
    let res = offlineResponse(vendorDir, routes, 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.asm.wasm');
    assert.equal(res.status, 200);
    assert.equal(res.headers.get('content-type'), 'application/wasm');
    assert.equal(res.headers.get('access-control-allow-origin'), '*');
    res = offlineResponse(vendorDir, routes, 'https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@500&display=swap');
    assert.equal(await res.text(), '@font-face{}');
    assert.equal(offlineResponse(vendorDir, routes, 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/none.js').status, 404);
    assert.equal(offlineResponse(vendorDir, routes, 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/../../offline.json').status, 404);
    assert.equal(offlineResponse(vendorDir, routes, 'https://www.googletagmanager.com/gtag/js?id=G-1'), null);
    assert.equal(offlineResponse(vendorDir, routes, 'https://cdn.jsdelivr.net/pyodide/v999/full/pyodide.mjs'), null);
});
