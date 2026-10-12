// 위니버시티 안(iframe)·설치판 감지(assets/js/host.js)와 부모 창 알림(assets/js/app/embed.js)
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';

const HOST_SCRIPT = readFileSync(new URL('../assets/js/host.js', import.meta.url), 'utf8');

// host.js를 가짜 window에서 돌리고 정해진 값을 돌려준다
function detect({ href, parentOrigin, sameWindow = false, parentThrows = false }) {
    const url = new URL(href);
    const attrs = {};
    const win = {
        location: { protocol: url.protocol, search: url.search, origin: url.origin },
        document: { documentElement: { setAttribute: (k, v) => (attrs[k] = v) } },
        URLSearchParams,
    };
    win.window = win;
    if (sameWindow) win.parent = win;
    else if (parentThrows)
        win.parent = {
            get location() {
                throw new Error('SecurityError');
            },
        };
    else win.parent = { location: { origin: parentOrigin } };
    vm.runInNewContext(HOST_SCRIPT, { ...win, window: win });
    assert.equal(attrs['data-host'], win.WENIV_WORLD_HOST);
    return win.WENIV_WORLD_HOST;
}

test('단독으로 열면 web', () => {
    assert.equal(detect({ href: 'https://world.weniv.co.kr/', sameWindow: true }), 'web');
    // ?embed가 있어도 iframe이 아니면 web
    assert.equal(
        detect({ href: 'https://world.weniv.co.kr/?embed=weniversity', sameWindow: true }),
        'web',
    );
});

test('같은 출처 부모 + ?embed=weniversity 일 때만 weniversity', () => {
    const href = 'https://weniversity.co.kr/tools/world/app/?embed=weniversity';
    assert.equal(detect({ href, parentOrigin: 'https://weniversity.co.kr' }), 'weniversity');
    // 쿼리가 없으면 web
    assert.equal(
        detect({ href: 'https://weniversity.co.kr/tools/world/app/', parentOrigin: 'https://weniversity.co.kr' }),
        'web',
    );
    // 다른 사이트가 iframe으로 띄우면 부모 location을 읽을 수 없다 → web
    assert.equal(detect({ href, parentThrows: true }), 'web');
});

test('설치판 주소(weniv-world://)는 desktop', () => {
    assert.equal(detect({ href: 'weniv-world://app/index.html', sameWindow: true }), 'desktop');
});

test('notifyHost는 위니버시티 안에서만 같은 출처로 보낸다', async () => {
    const sent = [];
    globalThis.window = {
        WENIV_WORLD_HOST: 'web',
        location: { origin: 'https://weniversity.co.kr' },
        parent: { postMessage: (data, origin) => sent.push([data, origin]) },
    };
    const { notifyHost } = await import('../assets/js/app/embed.js');

    assert.equal(notifyHost('story-cleared', { storyId: 1, attempts: 1 }), false);
    assert.equal(sent.length, 0);

    window.WENIV_WORLD_HOST = 'weniversity';
    assert.equal(notifyHost('story-cleared', { storyId: 3, attempts: 2 }), true);
    assert.deepEqual(sent, [
        [
            { source: 'weniv-world', version: 1, type: 'story-cleared', storyId: 3, attempts: 2 },
            'https://weniversity.co.kr',
        ],
    ]);

    window.WENIV_WORLD_HOST = 'desktop';
    assert.equal(notifyHost('ready'), false);
    delete globalThis.window;
});
