// 노트북 (CodeMirror 6 코드 셀)

import {
    EditorView,
    EditorState,
    keymap,
    Prec,
    basicSetup,
    indentWithTab,
    indentUnit,
    python,
    pythonLanguage,
    completeFromList,
    HighlightStyle,
    syntaxHighlighting,
    tags,
    Decoration,
    StateField,
    StateEffect,
} from '../../vendor/codemirror.js';
import { toast } from './ui.js';

export const DEFAULT_CODE = `# shift + enter를 눌러 실행해 보세요.
# 변수, 함수 목록은 World에 있습니다.
set_item(2, 2, 'fish-1')
move()
move()
turn_left()
turn_left()
turn_left()
repeat(2, move)
# pick()
`;

// 자동 완성 목록 (World의 함수 리스트와 같은 내용)
const API = [
    ['say', '캐릭터의 말풍선에 출력', 1],
    ['item', '캐릭터가 가진 아이템 반환', 0],
    ['on_item', '캐릭터 아래 아이템 여부 반환', 0],
    ['directions', '캐릭터의 방향을 반환', 0],
    ['move', '바라보는 방향으로 한 칸 이동', 0],
    ['turn_left', '왼쪽(반시계방향)으로 회전', 0],
    ['pick', '발 아래 아이템 획득', 0],
    ['put', '가진 아이템을 발 아래에 내려놓기', 1],
    ['repeat', '함수를 count 횟수만큼 반복: repeat(2, move)', 1],
    ['open_door', '앞의 문(door) 열기', 0],
    ['set_item', '맵에 아이템 추가: set_item(x, y, item, count)', 1],
    ['front_is_clear', '앞이 비어 있는지 확인', 0],
    ['left_is_clear', '왼쪽이 비어 있는지 확인', 0],
    ['right_is_clear', '오른쪽이 비어 있는지 확인', 0],
    ['back_is_clear', '뒤가 비어 있는지 확인', 0],
    ['typeof_wall', '앞에 있는 벽의 종류 반환', 0],
    ['attack', '앞의 몬스터를 스킬로 공격', 0],
    ['eat', '포션을 먹어 체력·마나 회복', 1],
    ['add_ch', '캐릭터 추가: add_ch(x, y, name)', 1],
    ['add_mob', '몬스터 추가: add_mob(x, y, type, name)', 1],
    ['turn_right', 'from modules import turn_right', 0],
    ['turn_around', 'from modules import turn_around', 0],
    ['move_to_wall', 'from modules import move_to_wall', 0],
    ['turn_left_until_clear', 'from modules import turn_left_until_clear', 0],
    ['jump', 'from modules import jump', 0],
];
const VARIABLES = [
    ['character_data', '캐릭터 데이터'],
    ['map_data', '지도 데이터'],
    ['item_data', '아이템 데이터'],
    ['wall_data', '벽 데이터'],
    ['mob_data', '몬스터 데이터'],
    ['skill_data', '스킬 데이터'],
];
const completions = completeFromList([
    ...API.map(([name, info, args]) => ({
        label: name,
        type: 'function',
        info,
        apply: args ? `${name}(` : `${name}()`,
        boost: 2,
    })),
    ...VARIABLES.map(([name, info]) => ({
        label: name,
        type: 'variable',
        info,
        boost: 1,
    })),
]);

const highlight = HighlightStyle.define([
    { tag: tags.keyword, color: 'var(--ColorCodePurple)' },
    {
        tag: [tags.string, tags.special(tags.string)],
        color: 'var(--ColorCodeOrange)',
    },
    {
        tag: [tags.number, tags.bool, tags.null],
        color: 'var(--ColorCodeGreen)',
    },
    { tag: tags.comment, color: 'var(--ColorGrayLv3)' },
    {
        tag: [
            tags.function(tags.definition(tags.variableName)),
            tags.definition(tags.className),
        ],
        color: 'var(--ColorCodeBlue)',
    },
    { tag: [tags.self, tags.className], color: 'var(--ColorCodePink)' },
]);

// 오류가 난 줄 표시
const setErrorLine = StateEffect.define();
const errorLineField = StateField.define({
    create: () => Decoration.none,
    update(deco, tr) {
        if (tr.docChanged) deco = Decoration.none;
        for (const effect of tr.effects) {
            if (!effect.is(setErrorLine)) continue;
            const line = effect.value;
            deco =
                line && line <= tr.state.doc.lines
                    ? Decoration.set([
                          Decoration.line({ class: 'cm-error-line' }).range(
                              tr.state.doc.line(line).from,
                          ),
                      ])
                    : Decoration.none;
        }
        return deco;
    },
    provide: (field) => EditorView.decorations.from(field),
});

const dateStamp = () => {
    const d = new Date();
    return [
        d.getFullYear(),
        d.getMonth() + 1,
        d.getDate(),
        d.getHours(),
        d.getMinutes(),
        d.getSeconds(),
    ].join('-');
};

const downloadText = (text, filename, type = 'text/plain') => {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([text], { type }));
    link.download = filename;
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
};

const pickFile = (accept) =>
    new Promise((resolve) => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = accept;
        input.onchange = () => resolve(input.files[0] || null);
        input.click();
    });

let cellSeq = 0;

export class Notebook {
    constructor({ section, onRun }) {
        this.section = section;
        this.onRun = onRun;
        this.cells = [];
        this.storageKey = null;
        this.saveTimer = null;

        section.addEventListener('click', (e) => this.handleClick(e));
    }

    // ------------------------------------------------------------------
    // 셀 만들기 / 지우기
    createCell(code = '', { after = null, focus = false } = {}) {
        const cell = { id: ++cellSeq };

        const root = document.createElement('article');
        root.className = 'cell';
        root.dataset.cellId = cell.id;
        root.innerHTML = `
            <div class="cell-box">
                <header class="cm-header">
                    <div class="cell-run">
                        <button type="button" class="btn-play cell-run-button" title="실행 (Shift + Enter)">
                            <span class="sr-only">코드 실행</span>
                        </button>
                        <span class="cell-status" aria-live="polite"></span>
                    </div>
                    <ul class="btn-list">
                        <li class="show-tooltip" name="download code">
                            <button type="button" class="btn-code-download code-export"><span class="sr-only">코드 다운로드</span></button>
                        </li>
                        <li class="show-tooltip" name="upload code">
                            <button type="button" class="btn-code-upload code-import"><span class="sr-only">코드 불러오기</span></button>
                        </li>
                        <li class="show-tooltip" name="delete">
                            <button type="button" class="btn-close code-delete"><span class="sr-only">셀 삭제</span></button>
                        </li>
                    </ul>
                </header>
                <div class="cell-editor"></div>
            </div>
            <div class="cell-output" hidden></div>`;

        const addWrap = document.createElement('div');
        addWrap.className = 'cell-add-wrap';
        addWrap.innerHTML =
            '<button type="button" class="btn-add-code add-code-next">코드 추가</button>';

        cell.root = root;
        cell.addWrap = addWrap;
        cell.output = root.querySelector('.cell-output');
        cell.status = root.querySelector('.cell-status');
        cell.view = new EditorView({
            parent: root.querySelector('.cell-editor'),
            state: EditorState.create({
                doc: code,
                extensions: [
                    Prec.highest(
                        keymap.of([
                            {
                                key: 'Shift-Enter',
                                run: () => (
                                    this.run(cell, { advance: true }),
                                    true
                                ),
                            },
                            {
                                key: 'Mod-Enter',
                                run: () => (this.run(cell), true),
                            },
                        ]),
                    ),
                    basicSetup,
                    keymap.of([indentWithTab]),
                    indentUnit.of('    '),
                    python(),
                    pythonLanguage.data.of({ autocomplete: completions }),
                    syntaxHighlighting(highlight),
                    errorLineField,
                    EditorView.updateListener.of((update) => {
                        if (update.docChanged) this.scheduleSave();
                    }),
                ],
            }),
        });

        // 툴팁(event.js)
        root.querySelectorAll('.show-tooltip').forEach((el) =>
            window.addTooltipEvent?.(el),
        );

        const index = after ? this.cells.indexOf(after) + 1 : this.cells.length;
        const anchor = after ? after.addWrap.nextSibling : null;
        this.section.insertBefore(root, anchor);
        this.section.insertBefore(addWrap, anchor);
        this.cells.splice(index, 0, cell);

        if (focus) this.focus(cell);
        return cell;
    }

    removeCell(cell) {
        if (this.cells.length === 1) {
            toast('셀이 하나뿐일 때는 삭제할 수 없습니다.');
            return;
        }
        cell.view.destroy();
        cell.root.remove();
        cell.addWrap.remove();
        this.cells.splice(this.cells.indexOf(cell), 1);
        this.scheduleSave();
    }

    setCodes(codes) {
        for (const cell of this.cells) {
            cell.view.destroy();
            cell.root.remove();
            cell.addWrap.remove();
        }
        this.cells = [];
        const list = codes && codes.length ? codes : [''];
        list.forEach((code) => this.createCell(code));
    }

    getCodes() {
        return this.cells.map((cell) => cell.view.state.doc.toString());
    }

    focus(cell) {
        cell.view.focus();
        cell.root.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }

    label(cell) {
        return `셀 ${this.cells.indexOf(cell) + 1}`;
    }

    // ------------------------------------------------------------------
    // 실행
    run(cell, { advance = false } = {}) {
        this.onRun(cell);
        if (advance) {
            const next = this.cells[this.cells.indexOf(cell) + 1];
            this.focus(next || this.createCell('', { after: cell }));
        }
    }

    setStatus(cell, status) {
        const text =
            {
                queued: '대기 중',
                running: '실행 중…',
                loading: '파이썬 준비 중…',
            }[status] || '';
        cell.status.textContent = text;
        cell.root.classList.toggle('is-running', Boolean(status));
    }

    clearOutput(cell) {
        cell.output.replaceChildren();
        cell.output.hidden = true;
        cell.output.classList.remove('error');
        cell.view.dispatch({ effects: setErrorLine.of(null) });
    }

    showOutput(cell, { result, error }) {
        if (!cell.root.isConnected) return;
        this.clearOutput(cell);
        if (error) {
            cell.output.classList.add('error');
            const title = document.createElement('p');
            title.className = 'cell-error-title';
            title.textContent = `${error.name}: ${error.message}`;
            cell.output.appendChild(title);
            if (error.hint) {
                const hint = document.createElement('p');
                hint.className = 'cell-error-hint';
                hint.textContent = `힌트: ${error.hint}`;
                cell.output.appendChild(hint);
            }
            if (error.traceback) {
                const details = document.createElement('details');
                details.innerHTML = '<summary>자세히 보기</summary><pre></pre>';
                details.querySelector('pre').textContent = error.traceback;
                cell.output.appendChild(details);
            }
            if (error.line && error.file === this.label(cell)) {
                cell.view.dispatch({ effects: setErrorLine.of(error.line) });
            }
            cell.output.hidden = false;
        } else if (result != null) {
            const pre = document.createElement('pre');
            pre.className = 'cell-result';
            pre.textContent = result;
            cell.output.appendChild(pre);
            cell.output.hidden = false;
        }
    }

    // ------------------------------------------------------------------
    // 버튼
    handleClick(e) {
        const button = e.target.closest('button');
        if (!button) return;
        const root = button.closest('.cell');
        const cell = root && this.cells.find((c) => c.root === root);

        if (button.classList.contains('cell-run-button') && cell)
            this.run(cell);
        else if (button.classList.contains('code-export') && cell)
            this.downloadCell(cell);
        else if (button.classList.contains('code-import') && cell)
            this.uploadCell(cell);
        else if (button.classList.contains('code-delete') && cell)
            this.removeCell(cell);
        else if (button.classList.contains('add-code-next')) {
            const wrap = button.closest('.cell-add-wrap');
            const after = this.cells.find((c) => c.addWrap === wrap);
            this.createCell('', { after, focus: true });
        }
    }

    downloadCell(cell) {
        downloadText(cell.view.state.doc.toString(), `code_${dateStamp()}.py`);
    }

    async uploadCell(cell) {
        const file = await pickFile('.py,.txt');
        if (!file) return;
        const text = await file.text();
        cell.view.dispatch({
            changes: { from: 0, to: cell.view.state.doc.length, insert: text },
        });
    }

    exportNotebook() {
        const notebook = {
            cells: this.getCodes().map((code) => ({
                cell_type: 'code',
                execution_count: null,
                metadata: {},
                outputs: [],
                source: code.split(/(?<=\n)/),
            })),
            metadata: {
                kernelspec: {
                    display_name: 'Python 3',
                    language: 'python',
                    name: 'python3',
                },
                language_info: {
                    name: 'python',
                    file_extension: '.py',
                    mimetype: 'text/x-python',
                },
            },
            nbformat: 4,
            nbformat_minor: 5,
        };
        downloadText(
            JSON.stringify(notebook, null, 2),
            `notebook_${dateStamp()}.ipynb`,
            'application/json',
        );
    }

    async importNotebook() {
        const file = await pickFile('.ipynb');
        if (!file) return;
        let codes;
        try {
            const notebook = JSON.parse(await file.text());
            // Jupyter는 source를 줄 단위 배열로 저장합니다. 문자열인 경우도 지원합니다.
            codes = (notebook.cells || [])
                .filter((c) => c.cell_type === 'code')
                .map((c) =>
                    Array.isArray(c.source)
                        ? c.source.join('')
                        : String(c.source ?? ''),
                );
        } catch (err) {
            toast('노트북 파일을 읽지 못했습니다.');
            return;
        }
        if (!codes.length) {
            toast('불러올 코드 셀이 없습니다.');
            return;
        }
        const last = this.cells[this.cells.length - 1];
        let after = last;
        // 마지막 셀이 비어 있으면 그 자리를 채웁니다.
        if (last && !last.view.state.doc.length) {
            last.view.dispatch({ changes: { from: 0, insert: codes.shift() } });
        }
        for (const code of codes) after = this.createCell(code, { after });
        this.scheduleSave();
    }

    // ------------------------------------------------------------------
    // 자동 저장 (새로고침해도 코드가 남도록)
    useStorage(key) {
        this.flushSave();
        this.storageKey = key;
    }

    scheduleSave() {
        if (!this.storageKey) return;
        clearTimeout(this.saveTimer);
        this.saveTimer = setTimeout(() => this.flushSave(), 600);
    }

    flushSave() {
        clearTimeout(this.saveTimer);
        if (!this.storageKey) return;
        try {
            localStorage.setItem(
                this.storageKey,
                JSON.stringify(this.getCodes()),
            );
        } catch (err) {
            /* 저장 공간이 부족하거나 사용할 수 없는 경우 */
        }
    }
}
