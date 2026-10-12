// 다른 사이트에 붙이는 묶음(scripts/build-embed.mjs)의 스타일 가두기·화면 틀 꺼내기
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import {
    extractTemplate,
    scopeCss,
    scopeSelector,
} from '../scripts/build-embed.mjs';

test('html·body·:root 규칙은 앱을 담은 요소로, 나머지는 그 안으로 가둔다', () => {
    assert.equal(scopeSelector('html'), '.weniv-world');
    assert.equal(scopeSelector('body'), '.weniv-world');
    assert.equal(
        scopeSelector(':root[color-theme=dark]'),
        '.weniv-world[color-theme=dark]',
    );
    assert.equal(
        scopeSelector(':root[color-theme=dark] .controller-modal::before'),
        '.weniv-world[color-theme=dark] .controller-modal::before',
    );
    assert.equal(
        scopeSelector('body.is-busy .map-item'),
        '.weniv-world.is-busy .map-item',
    );
    assert.equal(
        scopeSelector("[data-host='weniversity-page'] .main"),
        ".weniv-world[data-host='weniversity-page'] .main",
    );
    assert.equal(
        scopeSelector('.story-list > li'),
        '.weniv-world .story-list > li',
    );
    assert.equal(
        scopeSelector('button:disabled'),
        '.weniv-world button:disabled',
    );
    // bodyguard 같은 이름은 body로 보지 않는다
    assert.equal(scopeSelector('.bodyguard'), '.weniv-world .bodyguard');
});

test('애니메이션 이름에 ww-를 붙이고 그림 주소를 바꾸고 바깥 글꼴 @import는 뺀다', () => {
    const css = scopeCss(
        `@import url("https://example.com/font.css");
@keyframes spin { to { transform: rotate(360deg); } }
.a { animation: spin 1s linear infinite; background: url("../../assets/img/icon/a.svg") no-repeat; }
.b { animation-name: spin; background-image: url(../img/icon/b.svg); }
.c { background: url("data:image/png;base64,AA"); }`,
        { assetBase: '/world-runtime/' },
    );
    assert.doesNotMatch(css, /@import/);
    assert.match(css, /@keyframes ww-spin/);
    assert.match(
        css,
        /\.weniv-world \.a \{ animation: ww-spin 1s linear infinite; background: url\("\/world-runtime\/img\/icon\/a\.svg"\) no-repeat;/,
    );
    assert.match(
        css,
        /animation-name: ww-spin; background-image: url\("\/world-runtime\/img\/icon\/b\.svg"\)/,
    );
    assert.match(css, /url\("data:image\/png;base64,AA"\)/);
    // keyframes 안의 to {} 는 가두지 않는다
    assert.match(css, /\{ to \{ transform/);
});

test('잘못된 CSS 변수(var(-x))가 있으면 멈춘다', () => {
    assert.throws(
        () => scopeCss('.a { color: var(-Color); }', { assetBase: '/x/' }),
        /잘못된 CSS 변수/,
    );
});

test('바꾸지 못한 상대 그림 주소가 있으면 멈춘다', () => {
    assert.throws(
        () =>
            scopeCss('.a { background: url(foo.png); }', { assetBase: '/x/' }),
        /바꾸지 못한 그림 주소/,
    );
});

test('index.html에서 앱 화면만 꺼내 main을 div로 바꾼다', () => {
    const html = readFileSync(
        new URL('../index.html', import.meta.url),
        'utf8',
    );
    const template = extractTemplate(html, { assetBase: '/world-runtime/' });
    assert.match(template, /^<div class="main">/);
    assert.match(template, /<\/div>$/);
    assert.doesNotMatch(template, /<main|<header class="header"|<script/);
    for (const id of [
        'notebookSection',
        'app',
        'output',
        'engine-status',
        'btn-stop',
        'init',
        'speed-range',
    ])
        assert.match(template, new RegExp(`id=["']${id}["']`));
    assert.match(template, /class="story-list"/);
});
