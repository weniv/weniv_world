// 파이썬 실행 워커 (Pyodide)
//
// 메인 화면과 분리된 스레드에서 학습자 코드를 실행합니다.
// 무한 반복에 빠져도 화면은 멈추지 않고, 중지 버튼으로 워커를 종료할 수 있습니다.
// 워커는 DOM을 쓰지 않고 실행 결과(이벤트 목록과 월드 상태)만 돌려줍니다.

let runner = null;

const post = (id, payload) => self.postMessage({ id, ...payload });

async function init({ pyodideUrl, files, version }) {
    // Pyodide 314부터는 모듈 워커에서만 동작합니다. (engine.js에서 type: 'module'로 생성)
    const { loadPyodide } = await import(`${pyodideUrl}pyodide.mjs`);
    const pyodide = await loadPyodide({ indexURL: pyodideUrl });

    const dir = '/home/pyodide/world';
    pyodide.FS.mkdirTree(dir);
    const sources = await Promise.all(
        files.map(async (file) => {
            const url = new URL(
                `../../py/${file}?v=${encodeURIComponent(version)}`,
                self.location.href,
            );
            const response = await fetch(url);
            if (!response.ok)
                throw new Error(
                    `${file}을(를) 불러오지 못했습니다. (${response.status})`,
                );
            return [file, await response.text()];
        }),
    );
    for (const [file, text] of sources)
        pyodide.FS.writeFile(`${dir}/${file}`, text);

    pyodide.runPython(`import sys\nsys.path.insert(0, ${JSON.stringify(dir)})`);
    runner = pyodide.pyimport('runner');
    return { python: pyodide.runPython('import sys; sys.version.split()[0]') };
}

self.onmessage = async ({ data }) => {
    const { id, type } = data;
    try {
        if (type === 'init') {
            post(id, { ok: true, value: await init(data) });
        } else if (type === 'run') {
            const json = runner.run_cell(
                data.code,
                data.state,
                data.inputs,
                data.seed,
                data.label,
            );
            post(id, { ok: true, value: JSON.parse(json) });
        } else if (type === 'run-all') {
            // 제출 채점: 새 환경에서 셀 전체를 처음부터 실행
            const json = runner.run_all(
                data.codes,
                data.state,
                data.inputs,
                data.seed,
            );
            post(id, { ok: true, value: JSON.parse(json) });
        } else if (type === 'reset-namespace') {
            runner.reset_namespace();
            post(id, { ok: true });
        }
    } catch (err) {
        post(id, { ok: false, error: String(err?.message || err) });
    }
};
