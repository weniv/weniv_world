// 파이썬 워커와의 통신
//
// - 실행 요청은 순서대로 하나씩 처리합니다. 앞의 실행 결과(월드 상태)를 받은 다음
//   그 상태로 다음 실행을 보내야 하기 때문입니다.
// - stop()은 워커를 종료하고 새로 시작합니다. (무한 반복 탈출)
// - input()은 워커가 값을 요청하면 입력창을 띄우고, 받은 값으로 같은 셀을 처음부터
//   다시 실행합니다. 같은 상태와 같은 난수 시드로 실행하므로 결과가 같습니다.

import { APP_VERSION, PYODIDE_URL, PY_FILES } from './config.js';
import { asset, env } from './env.js';

// 파이썬 파일은 화면(메인 스레드)에서 받아 워커에 넘깁니다.
// 워커는 Pyodide(jsdelivr) 말고는 아무 데도 접속하지 않아도 되므로,
// 위니버시티처럼 워커 응답에 접속 제한(CSP)을 거는 곳에서도 그대로 동작합니다.
export const loadPythonSources = () =>
    Promise.all(
        PY_FILES.map(async (file) => {
            const url = asset(
                `py/${file}?v=${encodeURIComponent(APP_VERSION)}`,
            );
            const response = await fetch(url);
            if (!response.ok)
                throw new Error(
                    `${file}을(를) 불러오지 못했습니다. (${response.status})`,
                );
            return [file, await response.text()];
        }),
    );

export class StoppedError extends Error {
    constructor() {
        super('실행을 중지했습니다.');
        this.stopped = true;
    }
}

export class PythonEngine extends EventTarget {
    constructor() {
        super();
        this.worker = null;
        this.pending = new Map();
        this.nextId = 1;
        this.chain = Promise.resolve();
        this.status = 'idle';
        this.running = false;
        this.generation = 0;
    }

    setStatus(status, detail = '') {
        this.status = status;
        this.dispatchEvent(
            new CustomEvent('status', { detail: { status, detail } }),
        );
    }

    start() {
        this.generation += 1;
        const generation = this.generation;
        const workerUrl =
            env.workerUrl || new URL('./py-worker.js', import.meta.url);
        this.worker = new Worker(workerUrl, { type: 'module' });
        // 파이썬 파일을 받는 동안 워커가 죽어도 준비(ready)가 실패하게 합니다.
        let failStart;
        const workerFailed = new Promise((_, reject) => {
            failStart = reject;
        });
        workerFailed.catch(() => {});
        this.worker.onmessage = ({ data }) => {
            const request = this.pending.get(data.id);
            if (!request) return;
            this.pending.delete(data.id);
            data.ok
                ? request.resolve(data.value)
                : request.reject(new Error(data.error));
        };
        this.worker.onerror = (e) => {
            console.error('[python worker]', e.message);
            if (generation !== this.generation) return;
            const error = new Error(
                e.message || '파이썬 워커가 종료되었습니다.',
            );
            this.worker.terminate();
            for (const request of this.pending.values()) request.reject(error);
            this.pending.clear();
            this.running = false;
            failStart(error);
            this.ready = Promise.reject(error);
            this.ready.catch(() => {});
            this.setStatus('failed', error.message);
        };

        this.setStatus('loading');
        const startedAt = performance.now();
        // Pyodide는 바로 받기 시작하고, 파이썬 파일은 그동안 화면에서 받아 둡니다.
        this.worker.postMessage({ type: 'preload', pyodideUrl: PYODIDE_URL });
        const init = loadPythonSources().then((sources) =>
            generation === this.generation
                ? this.call('init', { pyodideUrl: PYODIDE_URL, sources })
                : null,
        );
        this.ready = Promise.race([init, workerFailed]).then(
            (info) => {
                if (generation !== this.generation) return;
                console.info(
                    `[python] Python ${info.python} 준비 (${Math.round(performance.now() - startedAt)}ms)`,
                );
                this.setStatus('ready');
            },
            (err) => {
                if (generation !== this.generation) return;
                this.setStatus('failed', err.message);
                throw err;
            },
        );
        this.ready.catch(() => {});
        return this.ready;
    }

    call(type, payload = {}) {
        const id = this.nextId++;
        return new Promise((resolve, reject) => {
            this.pending.set(id, { resolve, reject });
            try {
                this.worker.postMessage({ id, type, ...payload });
            } catch (error) {
                this.pending.delete(id);
                reject(error);
            }
        });
    }

    // 셀 하나 실행: getState()는 실제로 보낼 때 호출되어 그 시점의 월드 상태를 돌려줍니다.
    // onResult(result)는 다음 실행이 시작되기 전에 호출됩니다. (결과 상태를 반영할 곳)
    run({ code, getState, label, askInput, onResult }) {
        return this.enqueue({
            type: 'run',
            payload: () => ({
                code,
                label,
                state: JSON.stringify(getState()),
            }),
            askInput,
            onResult,
        });
    }

    // 제출 채점: 학습자 변수와 섞이지 않는 새 환경에서 셀 전체를 처음부터 실행합니다.
    runAll({ codes, getState, askInput, onResult }) {
        return this.enqueue({
            type: 'run-all',
            payload: () => ({
                codes: JSON.stringify(codes),
                state: JSON.stringify(getState()),
            }),
            askInput,
            onResult,
        });
    }

    enqueue(request) {
        const generation = this.generation;
        const task = this.chain.then(() =>
            this.request({ ...request, generation }),
        );
        this.chain = task.catch(() => {});
        return task;
    }

    async request({ type, payload, askInput, onResult, generation }) {
        // 중지 버튼을 누르기 전에 줄 서 있던 실행은 취소합니다.
        if (generation !== this.generation) throw new StoppedError();
        await this.ready;
        if (generation !== this.generation) throw new StoppedError();
        const seed = Math.floor(Math.random() * 2 ** 31);
        const inputs = [];
        this.running = true;
        this.setStatus('running');
        try {
            const data = payload();
            for (;;) {
                if (generation !== this.generation) throw new StoppedError();
                const result = await this.call(type, {
                    ...data,
                    inputs: JSON.stringify(inputs),
                    seed,
                });
                if (generation !== this.generation) throw new StoppedError();
                if (result.need_input === undefined) {
                    onResult?.(result);
                    return result;
                }
                const value = await askInput(result.need_input);
                if (generation !== this.generation) throw new StoppedError();
                inputs.push(value ?? null);
            }
        } finally {
            if (generation === this.generation) {
                this.running = false;
                if (this.status !== 'failed') this.setStatus('ready');
            }
        }
    }

    // 실행 중인 코드를 멈추고 워커를 다시 시작합니다. (학습자 변수는 초기화됩니다)
    stop() {
        const stopped = new StoppedError();
        this.worker?.terminate();
        for (const request of this.pending.values()) request.reject(stopped);
        this.pending.clear();
        this.running = false;
        this.chain = Promise.resolve();
        return this.start();
    }
}
