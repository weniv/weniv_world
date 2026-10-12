// 다른 사이트(위니버시티 /tools/world)에 위니브월드를 붙이기 위한 묶음을 만듭니다.
//
//   node scripts/build-embed.mjs --asset-base /world-runtime/ [--out embed]
//
// 만드는 것 (--out 아래)
//   module/   붙이는 사이트가 번들에 넣을 코드 (앱 모듈 그대로 + 아래 두 파일)
//     template.js   index.html의 앱 화면(<main class="main">) — 머리 줄은 붙이는 사이트가 따로 그립니다
//     world.css     style.scss를 .weniv-world 안으로 가둔 스타일 (html·body·:root 규칙은 .weniv-world로,
//                   애니메이션 이름은 ww- 를 붙이고, 그림 주소는 --asset-base 기준으로 바꿉니다)
//     index.js      붙이는 사이트가 쓰는 것만 모아 내보냅니다
//   runtime/  정적 파일로 올릴 것 (--asset-base 주소에서 서비스)
//     py-worker.js, py/, img/, data/story/
//   manifest.json  원본 커밋·앱 버전·필요한 글꼴
//
// 앱 코드(assets/js)는 바꾸지 않고 복사만 합니다. 단독 사이트와 같은 코드가 돕니다.

import { execFileSync } from 'node:child_process';
import {
    cpSync,
    existsSync,
    mkdirSync,
    readdirSync,
    readFileSync,
    rmSync,
    writeFileSync,
} from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import postcss from 'postcss';
import * as sass from 'sass';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const SCOPE = '.weniv-world';

const args = process.argv.slice(2);
const option = (name, fallback) => {
    const index = args.indexOf(`--${name}`);
    return index >= 0 ? args[index + 1] : fallback;
};

// ------------------------------------------------------------------
// 스타일 가두기
const ROOT_SELECTOR = /^(?:html|body|:root)(?=$|[.[:\s>+~])/;
const ATTR_ONLY = /^((?:\[[^\]]+\])+)(?=$|[\s>+~])/;

export function scopeSelector(selector) {
    const s = selector.trim();
    if (ROOT_SELECTOR.test(s)) return s.replace(ROOT_SELECTOR, SCOPE);
    // [data-host=…] .x, [color-theme=dark] .x 처럼 html에 붙던 속성 선택자
    if (ATTR_ONLY.test(s)) return s.replace(ATTR_ONLY, `${SCOPE}$1`);
    return `${SCOPE} ${s}`;
}

const IMAGE_URL = /url\((["']?)(?:\.\.\/)+(?:assets\/)?(img\/[^"')]+)\1\)/g;

export function scopeCss(css, { assetBase }) {
    const tree = postcss.parse(css);
    const keyframes = new Set();
    tree.walkAtRules((rule) => {
        if (rule.name === 'charset' || rule.name === 'import') rule.remove();
        else if (rule.name === 'keyframes') {
            keyframes.add(rule.params);
            rule.params = `ww-${rule.params}`;
        }
    });
    tree.walkRules((rule) => {
        if (rule.parent?.type === 'atrule' && rule.parent.name === 'keyframes')
            return;
        rule.selectors = rule.selectors.map(scopeSelector);
    });
    const renameAnimation = (value) =>
        value.replace(/[A-Za-z_][\w-]*/g, (word) =>
            keyframes.has(word) ? `ww-${word}` : word,
        );
    tree.walkDecls((decl) => {
        // 브라우저는 그냥 넘기지만 붙이는 쪽 CSS 처리기(Next.js)는 멈추는 값
        if (/var\(-[^-]/.test(decl.value))
            throw new Error(`잘못된 CSS 변수: ${decl.prop}: ${decl.value}`);
        if (decl.prop === 'animation' || decl.prop === 'animation-name')
            decl.value = renameAnimation(decl.value);
        if (decl.value.includes('url(')) {
            decl.value = decl.value.replace(
                IMAGE_URL,
                (_, quote, file) => `url("${assetBase}${file}")`,
            );
            const left = decl.value.match(
                /url\((?!["']?(?:https?:|data:|\/))[^)]*\)/,
            );
            if (left) throw new Error(`바꾸지 못한 그림 주소: ${left[0]}`);
        }
    });
    return tree.toString();
}

// index.html의 <main class="main"> … </main> → 붙이는 사이트에서는 <div class="main">
export function extractTemplate(html, { assetBase }) {
    const start = html.indexOf('<main class="main">');
    const end = html.lastIndexOf('</main>');
    if (start < 0 || end < 0)
        throw new Error('index.html에서 앱 화면을 찾지 못했습니다.');
    return html
        .slice(start, end + '</main>'.length)
        .replace('<main class="main">', '<div class="main">')
        .replace(/<\/main>$/, '</div>')
        .replace(/(["'(])\.\/assets\//g, `$1${assetBase}`)
        .replace(/\r\n/g, '\n');
}

const FONT_IMPORT = /@import url\(["']?([^"')]+)["']?\)/g;

// ------------------------------------------------------------------
function gitInfo() {
    try {
        const run = (...git) =>
            execFileSync('git', git, { cwd: ROOT, encoding: 'utf8' }).trim();
        return {
            commit: run('rev-parse', 'HEAD'),
            dirty:
                run('status', '--porcelain', '--', 'assets', 'index.html') !==
                '',
        };
    } catch (e) {
        return { commit: null, dirty: null };
    }
}

const copy = (from, to, filter) =>
    cpSync(path.join(ROOT, from), to, {
        recursive: true,
        filter: (src) =>
            !/__pycache__|\.DS_Store|\.scss$/.test(src) &&
            (!filter || filter(src)),
    });

function build({ assetBase, out }) {
    if (!assetBase.endsWith('/'))
        throw new Error('--asset-base는 /로 끝나야 합니다.');
    rmSync(out, { recursive: true, force: true });
    const moduleDir = path.join(out, 'module');
    const runtimeDir = path.join(out, 'runtime');

    // 1) 코드: assets/js(단독 사이트 전용 스크립트 제외) + vendor/codemirror.js
    const appFiles = readdirSync(path.join(ROOT, 'assets/js/app')).filter(
        (file) => file.endsWith('.js') && file !== 'main.js',
    );
    mkdirSync(path.join(moduleDir, 'js/app'), { recursive: true });
    for (const file of appFiles)
        cpSync(
            path.join(ROOT, 'assets/js/app', file),
            path.join(moduleDir, 'js/app', file),
        );
    cpSync(
        path.join(ROOT, 'assets/js/parser.js'),
        path.join(moduleDir, 'js/parser.js'),
    );
    mkdirSync(path.join(moduleDir, 'vendor'), { recursive: true });
    cpSync(
        path.join(ROOT, 'assets/vendor/codemirror.js'),
        path.join(moduleDir, 'vendor/codemirror.js'),
    );

    // 2) 화면 틀과 스타일
    const html = readFileSync(path.join(ROOT, 'index.html'), 'utf8');
    writeFileSync(
        path.join(moduleDir, 'template.js'),
        `// index.html의 앱 화면 (scripts/build-embed.mjs가 만듭니다)\nexport const MAIN_HTML = ${JSON.stringify(extractTemplate(html, { assetBase }))};\n`,
    );
    const compiled = sass.compile(path.join(ROOT, 'assets/css/style.scss'), {
        style: 'expanded',
    }).css;
    const fonts = [...compiled.matchAll(FONT_IMPORT)].map((m) => m[1]);
    writeFileSync(
        path.join(moduleDir, 'world.css'),
        `/* 위니브월드 스타일 (assets/css/style.scss를 ${SCOPE} 안으로 가둔 것, scripts/build-embed.mjs가 만듭니다) */\n` +
            scopeCss(compiled, { assetBase }),
    );
    writeFileSync(
        path.join(moduleDir, 'index.js'),
        `// 위니브월드를 다른 사이트에 붙일 때 쓰는 것 (scripts/build-embed.mjs가 만듭니다)
export { createWorldApp } from './js/app/app.js';
export { APP_VERSION } from './js/app/config.js';
export { configure, store } from './js/app/env.js';
export * as records from './js/app/records.js';
export { MAIN_HTML } from './template.js';
`,
    );

    // 3) 정적 파일
    mkdirSync(runtimeDir, { recursive: true });
    cpSync(
        path.join(ROOT, 'assets/js/app/py-worker.js'),
        path.join(runtimeDir, 'py-worker.js'),
    );
    copy(
        'assets/py',
        path.join(runtimeDir, 'py'),
        (src) => !src.endsWith('.pyc'),
    );
    // 공유 미리보기 그림(og)은 위니브월드 사이트 전용이라 뺍니다.
    copy(
        'assets/img',
        path.join(runtimeDir, 'img'),
        (src) => !/[\\/]og([\\/]|$)/.test(src),
    );
    copy('assets/data/story', path.join(runtimeDir, 'data/story'));

    const config = readFileSync(
        path.join(ROOT, 'assets/js/app/config.js'),
        'utf8',
    );
    const manifest = {
        source: { repository: 'weniv/weniv_world', ...gitInfo() },
        appVersion: config.match(/APP_VERSION = '([^']+)'/)?.[1] ?? null,
        pyodideUrl: config.match(/PYODIDE_URL = '([^']+)'/)?.[1] ?? null,
        assetBase,
        fonts,
    };
    writeFileSync(
        path.join(out, 'manifest.json'),
        `${JSON.stringify(manifest, null, 2)}\n`,
    );
    return manifest;
}

if (
    process.argv[1] &&
    path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
    const assetBase = option('asset-base');
    if (!assetBase) {
        console.error(
            '사용법: node scripts/build-embed.mjs --asset-base /world-runtime/ [--out embed]',
        );
        process.exit(1);
    }
    const out = path.resolve(option('out', path.join(ROOT, 'embed')));
    const manifest = build({ assetBase, out });
    console.log(
        `만들었습니다: ${out} (앱 ${manifest.appVersion}, 커밋 ${manifest.source.commit?.slice(0, 7) ?? '-'}${manifest.source.dirty ? ' + 고친 파일' : ''})`,
    );
    if (!existsSync(path.join(out, 'module/world.css'))) process.exit(1);
}
