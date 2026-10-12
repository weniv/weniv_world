// 위니브월드 설치판: 앱 주소(weniv-world://app/)와 인터넷 주소 요청을 앱 안 파일로 돌려주는 도우미 (main.cjs)
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const MIME = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.mjs': 'text/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.md': 'text/markdown; charset=utf-8',
    '.py': 'text/x-python; charset=utf-8',
    '.txt': 'text/plain; charset=utf-8',
    '.svg': 'image/svg+xml',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.ico': 'image/x-icon',
    '.pdf': 'application/pdf',
    '.wasm': 'application/wasm',
    '.zip': 'application/zip',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.map': 'application/json',
};

/** root 안의 파일 경로 (../ 등으로 root 밖을 가리키면 null) */
function safeJoin(root, relative) {
    const base = path.resolve(root);
    const target = path.resolve(base, `.${path.sep}${relative}`);
    return target.startsWith(base + path.sep) ? target : null;
}

function fileResponse(file, extraHeaders = {}) {
    let data = null;
    try {
        if (file && fs.statSync(file).isFile()) data = fs.readFileSync(file);
    } catch {
        data = null;
    }
    if (!data) return new Response('Not Found', { status: 404 });
    const type = MIME[path.extname(file).toLowerCase()] || 'application/octet-stream';
    return new Response(data, { status: 200, headers: { 'Content-Type': type, ...extraHeaders } });
}

/** weniv-world://app/<경로> → appDir 안 파일 (끝이 / 면 index.html, ?v= 같은 쿼리는 무시) */
function appResponse(appDir, requestUrl) {
    const url = new URL(requestUrl);
    if (url.host !== 'app') return new Response('Not Found', { status: 404 });
    let pathname;
    try {
        pathname = decodeURIComponent(url.pathname);
    } catch {
        return new Response('Bad Request', { status: 400 });
    }
    if (pathname.endsWith('/')) pathname += 'index.html';
    return fileResponse(safeJoin(appDir, pathname.replace(/^\/+/, '')));
}

/** 인터넷 대신 앱 안 파일로 돌려줄 주소 목록 (scripts/prepare.mjs가 vendor/offline.json으로 만든다) */
function loadOfflineRoutes(vendorDir) {
    try {
        const manifest = JSON.parse(fs.readFileSync(path.join(vendorDir, 'offline.json'), 'utf8'));
        return Array.isArray(manifest.routes) ? manifest.routes : [];
    } catch {
        return [];
    }
}

/** 목록에 있는 인터넷 주소면 앱 안 파일 응답, 아니면 null (부르는 쪽이 요청을 막는다) */
function offlineResponse(vendorDir, routes, requestUrl) {
    const href = String(requestUrl).split('#')[0];
    for (const route of routes) {
        if (!href.startsWith(route.prefix)) continue;
        // 다른 출처(weniv-world://app)에서 모듈·wasm·글꼴을 가져오므로 CORS 허용을 붙인다
        const headers = { 'Access-Control-Allow-Origin': '*' };
        if (route.file) return fileResponse(safeJoin(vendorDir, route.file), headers);
        let rest;
        try {
            rest = decodeURIComponent(href.slice(route.prefix.length).split('?')[0]);
        } catch {
            return new Response('Bad Request', { status: 400 });
        }
        return fileResponse(safeJoin(path.join(vendorDir, route.dir), rest), headers);
    }
    return null;
}

module.exports = { MIME, safeJoin, appResponse, loadOfflineRoutes, offlineResponse };
