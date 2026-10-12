// 설치판에 넣을 파일을 만든다 (npm run prepare-app, dist·start 전에 저절로 돈다)
//
//   app/     위니브월드 사이트 빌드(저장소 루트 npm run build → dist/)를 복사. 3D 시험 화면(threejs)은 뺀다
//   vendor/  인터넷 대신 쓸 파일 — Pyodide(사이트가 쓰는 판과 같은 판), 글꼴(Pretendard, Source Code Pro)
//            offline.json: '이 인터넷 주소로 오는 요청 → vendor 안 이 파일' 목록 (main.cjs가 읽는다)
//
// 사이트가 쓰는 Pyodide 판(assets/js/app/config.js PYODIDE_URL)과 desktop/package.json의 pyodide 판이 다르면 멈춘다.
// 사이트 CSS가 부르는 인터넷 글꼴 주소가 offline.json에 없으면 멈춘다(설치판이 인터넷 없이 글꼴을 못 그리는 일을 막는다).
//
//   node scripts/prepare.mjs                 루트 npm run build 까지
//   node scripts/prepare.mjs --skip-web-build 이미 만든 루트 dist/를 그대로 쓴다
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const desktop = fileURLToPath(new URL('../', import.meta.url));
const root = path.resolve(desktop, '..');
const appDir = path.join(desktop, 'app');
const vendorDir = path.join(desktop, 'vendor');
const modules = path.join(desktop, 'node_modules');
const args = process.argv.slice(2);

const fail = (message) => {
    console.error(`prepare: ${message}`);
    process.exit(1);
};
const read = (file) => fs.readFileSync(file, 'utf8');
const copy = (from, to) => {
    fs.mkdirSync(path.dirname(to), { recursive: true });
    fs.copyFileSync(from, to);
};

// ---------------------------------------------------------------- Pyodide 판 확인
const config = read(path.join(root, 'assets/js/app/config.js'));
const pyodideUrl = config.match(/PYODIDE_URL\s*=\s*'([^']+)'/)?.[1];
const siteVersion = pyodideUrl?.match(/\/pyodide\/v([^/]+)\/full\/$/)?.[1];
if (!siteVersion) fail(`config.js에서 PYODIDE_URL을 읽지 못했습니다: ${pyodideUrl}`);
const npmVersion = JSON.parse(read(path.join(modules, 'pyodide/package.json'))).version;
if (npmVersion !== siteVersion) {
    fail(`사이트는 Pyodide ${siteVersion}, 설치판(desktop/package.json)은 ${npmVersion}입니다. 같은 판으로 맞추세요.`);
}

// ---------------------------------------------------------------- 사이트 빌드 → app/
if (!args.includes('--skip-web-build')) {
    console.log('prepare: 위니브월드 사이트 빌드 (루트 npm run build)');
    execSync('npm run build', { cwd: root, stdio: 'inherit' });
}
const dist = path.join(root, 'dist');
if (!fs.existsSync(path.join(dist, 'index.html'))) fail('루트 dist/index.html이 없습니다. 루트에서 npm ci 후 다시 실행하세요.');

const SKIP = [/^assets[\\/]model([\\/]|$)/, /^assets[\\/]js[\\/]three\.js$/, /^threejs\.html$/];
fs.rmSync(appDir, { recursive: true, force: true });
const copyTree = (from, rel = '') => {
    for (const entry of fs.readdirSync(path.join(from, rel), { withFileTypes: true })) {
        const child = path.join(rel, entry.name);
        if (SKIP.some((pattern) => pattern.test(child))) continue;
        if (entry.isDirectory()) copyTree(from, child);
        else copy(path.join(from, child), path.join(appDir, child));
    }
};
copyTree(dist);
copy(path.join(root, 'LICENSE.txt'), path.join(appDir, 'LICENSE.txt'));

// ---------------------------------------------------------------- vendor/
fs.rmSync(vendorDir, { recursive: true, force: true });

// Pyodide: 파이썬 표준 라이브러리만 쓰므로 꾸러미(packages)는 넣지 않는다
const PYODIDE_FILES = ['pyodide.mjs', 'pyodide.asm.mjs', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json'];
for (const file of PYODIDE_FILES) copy(path.join(modules, 'pyodide', file), path.join(vendorDir, 'pyodide', file));

// Pretendard (jsdelivr gh/orioncactus/pretendard/dist/web/static/ 와 같은 배치, woff2만)
const pretendardSrc = path.join(modules, 'pretendard/dist/web/static');
copy(path.join(pretendardSrc, 'pretendard.css'), path.join(vendorDir, 'pretendard/pretendard.css'));
for (const file of fs.readdirSync(path.join(pretendardSrc, 'woff2'))) {
    if (file.endsWith('.woff2')) copy(path.join(pretendardSrc, 'woff2', file), path.join(vendorDir, 'pretendard/woff2', file));
}

// Source Code Pro 500 (Google Fonts 대신, 영문·확장 영문)
const GSTATIC = 'https://fonts.gstatic.com/s/sourcecodepro/weniv-world/';
// @fontsource 500.css에서 영문(latin)·확장 영문(latin-ext) 블록만 골라 주소를 바꾼다
const scpSource = read(path.join(modules, '@fontsource/source-code-pro/500.css'));
let scpCss = '/* Source Code Pro 500 — 위니브월드 설치판 (@fontsource/source-code-pro, SIL OFL 1.1) */\n';
for (const subset of ['latin-ext', 'latin']) {
    const marker = `/* source-code-pro-${subset}-500-normal */`;
    const start = scpSource.indexOf(marker);
    const end = start < 0 ? -1 : scpSource.indexOf('}', start);
    if (end < 0) fail(`@fontsource/source-code-pro 500.css에 ${subset} 블록이 없습니다.`);
    const block = scpSource.slice(start + marker.length, end + 1).trim();
    const file = `source-code-pro-${subset}-500-normal.woff2`;
    copy(path.join(modules, '@fontsource/source-code-pro/files', file), path.join(vendorDir, 'fonts', file));
    scpCss += block.replace(/src:[^;]*;/, `src: url(${GSTATIC}${file}) format('woff2');`) + '\n';
}
fs.writeFileSync(path.join(vendorDir, 'fonts/source-code-pro.css'), scpCss);

const routes = [
    { prefix: pyodideUrl, dir: 'pyodide' },
    { prefix: 'https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/', dir: 'pretendard' },
    { prefix: 'https://fonts.googleapis.com/css2?family=Source+Code+Pro', file: 'fonts/source-code-pro.css' },
    { prefix: GSTATIC, dir: 'fonts' },
];
fs.writeFileSync(
    path.join(vendorDir, 'offline.json'),
    JSON.stringify({ pyodideVersion: siteVersion, routes }, null, 2) + '\n',
);

// 사이트 CSS가 부르는 인터넷 주소가 모두 앱 안 파일로 돌아가는지 확인
const css = read(path.join(appDir, 'assets/css/style.css'));
const imports = [...css.matchAll(/@import\s+url\(['"]?(https?:[^'")]+)['"]?\)/g)].map((m) => m[1]);
const missing = imports.filter((url) => !routes.some((route) => url.startsWith(route.prefix)));
if (missing.length) fail(`인터넷 없이 불러올 수 없는 CSS 주소: ${missing.join(', ')}`);

const size = (dir) =>
    fs.readdirSync(dir, { withFileTypes: true }).reduce((sum, e) => {
        const full = path.join(dir, e.name);
        return sum + (e.isDirectory() ? size(full) : fs.statSync(full).size);
    }, 0);
const mb = (bytes) => `${(bytes / 1024 / 1024).toFixed(1)}MB`;
console.log(`prepare: app ${mb(size(appDir))}, vendor ${mb(size(vendorDir))} (Pyodide ${siteVersion})`);
