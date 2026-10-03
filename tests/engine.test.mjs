import assert from 'node:assert/strict';
import { test } from 'node:test';
import { PythonEngine } from '../assets/js/app/engine.js';
import { defaultState, isValidWall } from '../assets/js/app/state.js';

class WorkerStub {
    messages = [];
    postMessage(data) {
        this.messages.push(data);
        if (data.type === 'init') queueMicrotask(() => this.reply({ python: 'test' }));
    }
    reply(value) {
        const { id } = this.messages.at(-1);
        this.onmessage({ data: { id, ok: true, value } });
    }
    terminate() {}
}

globalThis.Worker = WorkerStub;
const tick = () => new Promise((resolve) => setImmediate(resolve));
const start = async () => {
    const engine = new PythonEngine();
    await engine.start();
    return engine;
};
const runOptions = () => ({ code: 'move()', getState: defaultState, label: 'cell' });

test('worker failure rejects current and queued work and allows restart', async () => {
    const engine = await start();
    const run = engine.run(runOptions());
    const queued = engine.run(runOptions());
    const failures = Promise.all([
        assert.rejects(run, /crashed/),
        assert.rejects(queued, /crashed/),
    ]);
    await tick();
    engine.worker.onerror({ message: 'crashed' });
    await failures;
    assert.equal(engine.status, 'failed');
    assert.equal(engine.running, false);
    assert.equal(engine.pending.size, 0);
    await engine.stop();
    assert.equal(engine.status, 'ready');
});

test('worker failure during initialization rejects ready', async () => {
    const engine = new PythonEngine();
    const ready = engine.start();
    const failure = assert.rejects(ready, /startup failed/);
    engine.worker.onerror({ message: 'startup failed' });
    await failure;
    assert.equal(engine.status, 'failed');
});

test('stopping while awaiting input never sends old code to the new worker', async () => {
    const engine = await start();
    let answer;
    const run = engine.run({ ...runOptions(), askInput: () => new Promise((r) => { answer = r; }) });
    const stopped = assert.rejects(run, (error) => error.stopped);
    await tick();
    engine.worker.reply({ need_input: 'name?' });
    await tick();
    await engine.stop();
    answer('licat');
    await stopped;
    assert.deepEqual(engine.worker.messages.map((m) => m.type), ['init']);
});

test('queued grading is cancelled along with the running cell', async () => {
    const engine = await start();
    const cell = engine.run(runOptions());
    const grading = engine.runAll({ codes: ['move()'], getState: defaultState });
    const stopped = Promise.all([cell, grading].map((task) => assert.rejects(task, (e) => e.stopped)));
    await tick();
    await engine.stop();
    await stopped;
    assert.deepEqual(engine.worker.messages.map((m) => m.type), ['init']);
});

test('input replays use one initial state snapshot', async () => {
    const engine = await start();
    let reads = 0;
    const run = engine.run({ ...runOptions(), getState: () => ({ counter: ++reads }), askInput: async () => 'yes' });
    await tick();
    engine.worker.reply({ need_input: '?' });
    await tick();
    engine.worker.reply({ state: {} });
    await run;
    assert.equal(reads, 1);
    const messages = engine.worker.messages.filter((m) => m.type === 'run');
    assert.equal(messages[0].state, messages[1].state);
});

test('grading updates state before the following cell takes its snapshot', async () => {
    const engine = await start();
    let state = { counter: 0 };
    const grading = engine.runAll({ codes: [], getState: () => state, onResult: (r) => { state = r.state; } });
    const cell = engine.run({ ...runOptions(), getState: () => state });
    await tick();
    engine.worker.reply({ state: { counter: 42 } });
    await grading;
    await tick();
    assert.equal(JSON.parse(engine.worker.messages.at(-1).state).counter, 42);
    engine.worker.reply({ state });
    await cell;
});

test('walls must lie on half-cell boundaries inside the map', () => {
    const map = { height: 5, width: 5 };
    assert.ok(isValidWall(map, 0, 0.5));
    assert.ok(isValidWall(map, 3.5, 4));
    for (const [x, y] of [[0, 0.2], [1.1, 2], [0.5, 0.5], [0, 4.5], [NaN, 0]]) {
        assert.equal(isValidWall(map, x, y), false);
    }
});
