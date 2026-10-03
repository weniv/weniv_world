// 위니브월드 앱 진입점
//
//  노트북(셀) ──실행──▶ PythonEngine(Web Worker, Pyodide)
//      ▲                         │ 이벤트 목록 + 실행 후 월드 상태
//      │                         ▼
//  셀 결과 ◀──── Player(이벤트 재생) ──▶ WorldView(맵, 캐릭터, 아이템) / Terminal
//
// 월드 상태(World)는 화면이 가지고 있고, 실행할 때마다 워커로 보냅니다.

import { MOB_INFO } from './config.js';
import { PythonEngine } from './engine.js';
import { Notebook, DEFAULT_CODE } from './notebook.js';
import { Player } from './player.js';
import {
    cloneState,
    defaultState,
    fromTransfer,
    inWorld,
    isValidWall,
    newCharacter,
    posKey,
    storyState,
    toTransfer,
} from './state.js';
import { StoryManager } from './story.js';
import { Terminal } from './terminal.js';
import {
    createSpeedControl,
    setupShortcutHelp,
    showAlert,
    toast,
} from './ui.js';
import { WorldView } from './view.js';
import { World } from './world.js';
import { WorldEditor } from './world-editor.js';

const $ = (selector) => document.querySelector(selector);

// ----------------------------------------------------------------------
// 구성 요소
const world = new World();
const view = new WorldView($('#app'));
const terminal = new Terminal({
    output: $('#output'),
    indexList: $('.world-output .index-list'),
    scroller: $('.output-result'),
    clearButton: $('#output-init'),
    downloadButton: $('#output-download'),
});
const speed = createSpeedControl($('#speed-range'), $('#speed-text'));
const engine = new PythonEngine();

let pendingRuns = 0;
const notebook = new Notebook({
    section: $('#notebookSection'),
    onRun: (cell) => runCell(cell),
});
const player = new Player({
    view,
    terminal,
    notebook,
    alert: showAlert,
    stepSeconds: speed.seconds,
});
const isBusy = () => pendingRuns > 0 || engine.running || player.busy;

const editor = new WorldEditor({
    world,
    view,
    mapSection: $('.world-map'),
    isBusy,
    onCharacterReset: () => view.clearLines(),
});

world.addEventListener('change', () => view.sync(world.state));

// ----------------------------------------------------------------------
// 실행 상태 표시 (상단 상태 문구, 중지 버튼)
const statusText = $('#engine-status');
const stopButton = $('#btn-stop');

const updateBusy = () => {
    const busy = isBusy();
    document.body.classList.toggle('is-busy', busy);
    stopButton.hidden = !busy;
};

const renderEngineStatus = ({ status, detail }) => {
    statusText.dataset.status = status;
    statusText.textContent =
        {
            loading: '파이썬 준비 중…',
            running: '실행 중…',
            failed: '파이썬을 불러오지 못했습니다. 눌러서 다시 시도',
        }[status] || '';
    statusText.title = detail || '';
    updateBusy();
};
engine.addEventListener('status', (e) => renderEngineStatus(e.detail));
player.addEventListener('busy', updateBusy);

statusText.addEventListener('click', () => {
    if (engine.status === 'failed') engine.stop();
});

stopButton.addEventListener('click', () => {
    if (pendingRuns > 0 || engine.running) {
        engine.stop();
        terminal.append(
            '실행을 중지했습니다. 파이썬을 다시 시작합니다. (셀에서 만든 변수는 초기화됩니다)',
            {
                error: true,
            },
        );
    }
    player.skip();
});

// ----------------------------------------------------------------------
// 셀 실행
const askInput = async (promptText) =>
    window.prompt(promptText || '입력하세요');

async function runCell(cell) {
    const code = cell.view.state.doc.toString();
    const label = notebook.label(cell);
    notebook.clearOutput(cell);
    notebook.setStatus(
        cell,
        engine.status === 'loading' ? 'loading' : 'queued',
    );
    pendingRuns += 1;
    updateBusy();

    try {
        await engine.run({
            code,
            label,
            askInput,
            getState: () => {
                notebook.setStatus(cell, 'running');
                return toTransfer(world.state);
            },
            onResult: (result) => {
                // 다음 실행이 이 결과 상태에서 시작하도록 바로 반영합니다. (화면은 재생기가 따라 그림)
                const state = fromTransfer(result.state);
                world.replace(state, { render: false });
                const error = result.error ? { ...result.error, label } : null;
                // 끝나지 않는 반복으로 동작 수 한도에 걸린 경우, 수천 개의 애니메이션을 재생하지 않고
                // 출력과 오류만 보여 준 뒤 최종 상태로 맞춥니다.
                const events =
                    error?.name === 'TooManyActions'
                        ? result.events.filter(
                              (e) => e.t === 'print' || e.t === 'error',
                          )
                        : result.events;
                player.push([
                    ...events,
                    {
                        t: 'cell-output',
                        cell,
                        result: { result: result.result, error },
                    },
                    { t: 'sync', state: cloneState(state) },
                ]);
            },
        });
    } catch (err) {
        if (err.stopped) {
            notebook.showOutput(cell, {
                error: { name: '중지됨', message: err.message },
            });
        } else {
            notebook.showOutput(cell, {
                error: {
                    name: '실행 오류',
                    message: err.message,
                    hint: '인터넷 연결을 확인하고 새로고침해 보세요. 문제가 계속되면 알려 주세요.',
                },
            });
        }
    } finally {
        pendingRuns -= 1;
        notebook.setStatus(cell, null);
        updateBusy();
    }
}

// ----------------------------------------------------------------------
// 월드 초기화 / 스토리
const stories = new StoryManager({
    list: $('.story-list'),
    progress: $('.story-progress'),
    onSelect: (index) => selectStory(index),
    getCodes: () => notebook.getCodes(),
    runForGrading: (index, codes) => runForGrading(index, codes),
});

// 제출 채점: 진행 중인 실행이 끝나기를 기다린 뒤 스토리 월드를 처음 상태로 되돌리고,
// 셀 전체를 학습자 변수와 섞이지 않는 새 환경에서 처음부터 실행합니다.
async function runForGrading(index, codes) {
    player.skip();
    const initial = storyState(stories.worlds[index]);
    pendingRuns += 1;
    updateBusy();
    try {
        const result = await engine.runAll({
            codes,
            askInput,
            // 즉시 큐에 넣어 중지/스토리 전환 시 대기 중인 채점도 취소합니다.
            getState: () => {
                player.clear();
                notebook.cells.forEach((cell) => notebook.clearOutput(cell));
                document
                    .querySelectorAll('.modal.alert')
                    .forEach((modal) => modal.remove());
                return toTransfer(initial);
            },
            // 다음 셀의 getState()가 호출되기 전에 채점 결과를 반영합니다.
            onResult: (result) => {
                const state = fromTransfer(result.state);
                world.replace(state);
                view.clearEffects();
                editor.closeCharacterInfo();

                terminal.append(
                    `── ${index}편 제출: 코드를 처음부터 다시 실행한 결과 ──`,
                );
                state.print_data.forEach((line) => terminal.append(line));
                const error = result.error;
                if (error) {
                    terminal.append(`${error.name}: ${error.message}`, { error: true });
                    const cell =
                        notebook.cells[Number(error.file?.replace('셀 ', '')) - 1];
                    if (cell) notebook.showOutput(cell, { error });
                }
            },
        });
        return { state: fromTransfer(result.state), error: result.error };
    } catch (err) {
        if (err.stopped) toast('채점을 중지했습니다.');
        else
            showAlert(`채점하지 못했습니다.
${err.message}`);
        return null;
    } finally {
        pendingRuns -= 1;
        updateBusy();
    }
}

const stopEverything = () => {
    if (pendingRuns > 0 || engine.running) engine.stop();
    player.clear();
};

function resetWorld() {
    stopEverything();
    const { mode, index } = world.story;
    const story = mode && index ? stories.worlds[index] : null;
    world.replace(story ? storyState(story) : defaultState());
    view.clearEffects();
    editor.closeCharacterInfo();
    editor.clearSelection();
}

function loadNotebook() {
    const { mode, index } = world.story;
    if (mode && index) {
        notebook.useStorage(`${index}_draft`);
        notebook.setCodes(stories.codesFor(index));
    } else {
        notebook.useStorage('free_code');
        notebook.setCodes(readCodes('free_code') || [DEFAULT_CODE]);
    }
}

function selectStory(index) {
    world.story.index = index;
    resetWorld();
    loadNotebook();
}

function setStoryMode(mode) {
    world.story.mode = mode;
    if (mode && !$('.story-list > li.active')) world.story.index = 0;
    resetWorld();
    loadNotebook();
}

$('#init').addEventListener('click', resetWorld);
// event.js가 먼저 active 클래스를 바꾼 뒤 실행됩니다.
$('.btn-story').addEventListener('click', (e) =>
    setStoryMode(e.currentTarget.classList.contains('active')),
);
$('.btn-close-story').addEventListener('click', () => setStoryMode(false));

terminal.onClear = () => {
    terminal.clear();
    world.state.print_data = [];
};

// ----------------------------------------------------------------------
// 노트북 / 월드 파일 내보내기·불러오기
$('.notebook-header .btn-add-code').addEventListener('click', () => {
    const last = notebook.cells[notebook.cells.length - 1];
    notebook.createCell('', { after: last, focus: true });
});
$('.downloadNotebookBtn').addEventListener('click', () =>
    notebook.exportNotebook(),
);
$('.uploadNotebookBtn').addEventListener('click', () =>
    notebook.importNotebook(),
);

const tupleKey = (key) => `(${key.replace(',', ', ')})`;
const parseTupleKey = (text) => {
    const [x, y] = String(text)
        .replace(/[()\s]/g, '')
        .split(',')
        .map(Number);
    return [x, y];
};

$('#btn-download-worlddata').addEventListener('click', () => {
    const s = world.state;
    // 이전 버전(world_data.json)과 같은 형식으로 저장합니다.
    const data = {
        character_data: s.characters.map((c) => ({
            ...c,
            character_obj: null,
        })),
        item_data: Object.fromEntries(
            Object.entries(s.items).map(([k, v]) => [tupleKey(k), v]),
        ),
        map_data: s.map,
        wall_data: Object.fromEntries(
            Object.entries(s.walls).map(([k, v]) => [tupleKey(k), v]),
        ),
        mob_data: s.mobs.map((m) => ({ ...m, mob_obj: null })),
    };
    const link = document.createElement('a');
    link.href = URL.createObjectURL(
        new Blob([JSON.stringify(data)], { type: 'application/json' }),
    );
    link.download = 'world_data.json';
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
});

const worldFileInput = $('#worldFileInput');
$('#btn-upload-worlddata').addEventListener('click', () => {
    if (world.story.mode) return;
    if (isBusy()) {
        toast('실행 중에는 월드를 불러올 수 없습니다.');
        return;
    }
    worldFileInput.click();
});
worldFileInput.addEventListener('change', async () => {
    const file = worldFileInput.files[0];
    worldFileInput.value = '';
    if (!file) return;
    try {
        const data = JSON.parse(await file.text());
        if (isBusy() || world.story.mode) {
            toast('실행 중이거나 스토리 모드에서는 월드를 불러올 수 없습니다.');
            return;
        }
        world.replace(parseWorldFile(data));
        view.clearLines();
    } catch (err) {
        console.warn(err);
        showAlert('올바른 월드 파일이 아닙니다.');
    }
});

const isInt = (v) => Number.isInteger(v);

function parseWorldFile(data) {
    const height = Number(data.map_data?.height);
    const width = Number(data.map_data?.width);
    if (
        !isInt(height) ||
        !isInt(width) ||
        height < 1 ||
        width < 1 ||
        height > 20 ||
        width > 20
    ) {
        throw new Error('map_data');
    }
    const state = defaultState(height, width);
    const taken = new Set();
    const free = (x, y) =>
        isInt(x) &&
        isInt(y) &&
        inWorld(state, x, y) &&
        !taken.has(posKey(x, y));

    state.characters = [];
    for (const c of data.character_data || []) {
        if (state.characters.length || c.character !== 'licat' || !free(c.x, c.y)) continue;
        const ch = newCharacter(c.x, c.y);
        ch.directions = [0, 1, 2, 3].includes(c.directions) ? c.directions : 0;
        ch.items = Object.fromEntries(
            Object.entries(c.items || {}).filter(([, n]) => isInt(n) && n > 0),
        );
        if (isInt(Number(c.hp))) ch.hp = Number(c.hp);
        if (isInt(Number(c.mp))) ch.mp = Number(c.mp);
        state.characters.push(ch);
        taken.add(posKey(c.x, c.y));
    }
    if (!state.characters.length) {
        state.characters.push(newCharacter());
        taken.add(posKey(0, 0));
    }

    for (const m of data.mob_data || []) {
        if (!MOB_INFO[m.mob] || !m.name || !free(m.x, m.y)) continue;
        if (state.mobs.some((other) => other.name === String(m.name))) continue;
        state.mobs.push({
            name: String(m.name),
            mob: m.mob,
            x: m.x,
            y: m.y,
            directions: [0, 1, 2, 3].includes(m.directions) ? m.directions : 0,
            hp: isInt(Number(m.hp)) ? Number(m.hp) : MOB_INFO[m.mob].hp,
        });
        taken.add(posKey(m.x, m.y));
    }

    for (const [key, v] of Object.entries(data.item_data || {})) {
        const [x, y] = parseTupleKey(key);
        if (
            isInt(x) &&
            isInt(y) &&
            inWorld(state, x, y) &&
            v?.item &&
            isInt(v.count) &&
            v.count > 0
        ) {
            state.items[posKey(x, y)] = {
                item: String(v.item),
                count: v.count,
            };
        }
    }
    for (const [key, type] of Object.entries(data.wall_data || {})) {
        const [x, y] = parseTupleKey(key);
        if (
            ['wall', 'fence', 'door'].includes(type) &&
            isValidWall(state.map, x, y)
        ) {
            state.walls[posKey(x, y)] = type;
        }
    }
    return state;
}

// ----------------------------------------------------------------------
// 시작
function readCodes(key) {
    try {
        const codes = JSON.parse(localStorage.getItem(key));
        return Array.isArray(codes) && codes.length ? codes : null;
    } catch (e) {
        return null;
    }
}

setupShortcutHelp();
world.replace(defaultState());
loadNotebook();
engine.start();
stories.load().catch((err) => {
    console.error(err);
    toast('스토리를 불러오지 못했습니다.');
});
window.addEventListener('pagehide', () => notebook.flushSave());

// 개발자 도구 / 자동 테스트에서 상태를 확인하기 위한 핸들
window.__wenivDebug = {
    world,
    engine,
    player,
    notebook,
    view,
    stories,
    isBusy,
};
