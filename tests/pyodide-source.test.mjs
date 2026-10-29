import assert from 'node:assert/strict';
import { test } from 'node:test';
import { PYODIDE_FALLBACK_URL, PYODIDE_URL } from '../assets/js/app/config.js';
import { pyodideUrls, rememberPyodideSource } from '../assets/js/app/engine.js';

const store = new Map();
globalThis.localStorage = {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, String(v)),
    removeItem: (k) => store.delete(k),
};

test('처음에는 jsdelivr부터, 안 되면 S3', () => {
    store.clear();
    assert.deepEqual(pyodideUrls(), [PYODIDE_URL, PYODIDE_FALLBACK_URL]);
});

test('S3로 받았으면 7일 동안 S3부터', () => {
    store.clear();
    rememberPyodideSource([PYODIDE_URL, PYODIDE_FALLBACK_URL], PYODIDE_FALLBACK_URL);
    assert.deepEqual(pyodideUrls(), [PYODIDE_FALLBACK_URL, PYODIDE_URL]);
    store.set('weniv:pyodide-cdn-blocked', String(Date.now() - 8 * 86400000));
    assert.deepEqual(pyodideUrls(), [PYODIDE_URL, PYODIDE_FALLBACK_URL]);
});

test('jsdelivr로 받으면 기억을 지움', () => {
    store.set('weniv:pyodide-cdn-blocked', String(Date.now()));
    rememberPyodideSource([PYODIDE_FALLBACK_URL, PYODIDE_URL], PYODIDE_URL);
    assert.equal(store.has('weniv:pyodide-cdn-blocked'), false);
});

test('S3부터 시도해 S3로 받으면 기억 시각을 늘리지 않음', () => {
    const at = String(Date.now() - 3 * 86400000);
    store.set('weniv:pyodide-cdn-blocked', at);
    rememberPyodideSource([PYODIDE_FALLBACK_URL, PYODIDE_URL], PYODIDE_FALLBACK_URL);
    assert.equal(store.get('weniv:pyodide-cdn-blocked'), at);
});

test('저장소를 못 쓰면 jsdelivr부터', () => {
    globalThis.localStorage = {
        getItem() { throw new Error('blocked'); },
        setItem() { throw new Error('blocked'); },
        removeItem() { throw new Error('blocked'); },
    };
    assert.deepEqual(pyodideUrls(), [PYODIDE_URL, PYODIDE_FALLBACK_URL]);
    rememberPyodideSource([PYODIDE_URL, PYODIDE_FALLBACK_URL], PYODIDE_FALLBACK_URL);
});
