// 스토리 목록, 선택, 제출(채점)

import { parser } from '../parser.js';
import { posKey } from './state.js';
import { showResultDialog, toast } from './ui.js';

const BASE = './assets/data/story/';

const fetchJson = async (url) => {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`${url} (${response.status})`);
    return response.json();
};

const sameDict = (a = {}, b = {}) => {
    const ka = Object.keys(a);
    const kb = Object.keys(b);
    return ka.length === kb.length && ka.every((k) => a[k] === b[k]);
};

// 채점 항목 (assets/data/story/solutions.json 의 키)
// 오답일 때 어떤 항목이 틀렸는지만 보여 주고, 정답 값은 보여 주지 않습니다.
const CHECKS = [
    {
        key: 'print_data',
        label: 'print로 출력한 내용',
        // 정답 문장이 모두 출력되어야 하고, 정답이 한 줄이면 마지막 출력이 그 문장이어야 합니다.
        test: (expected, ctx) =>
            expected.every((s) =>
                ctx.print_data.some((line) => line.includes(s)),
            ) &&
            !(
                expected.length === 1 &&
                ctx.print_data.length &&
                !expected.includes(ctx.print_data[ctx.print_data.length - 1])
            ),
    },
    {
        key: 'say_data',
        label: 'say로 말한 내용',
        test: (expected, ctx) =>
            expected.every((s) =>
                ctx.say_data.some((line) => line.includes(s)),
            ) &&
            !(
                expected.length === 1 &&
                ctx.say_data.length &&
                !expected.includes(ctx.say_data[ctx.say_data.length - 1])
            ),
    },
    {
        key: 'character_data',
        label: '캐릭터의 마지막 위치',
        test: (expected, ctx) => {
            const ch = ctx.character || {};
            return Object.keys(expected).every(
                (prop) => expected[prop] === ch[prop],
            );
        },
    },
    {
        key: 'item',
        label: '캐릭터가 가진 아이템',
        test: (expected, ctx) => sameDict(expected, ctx.item),
    },
    {
        key: 'item_data',
        label: '맵에 남은 아이템',
        test: (expected, ctx) => {
            const want = {};
            for (const [x, y, item, count] of expected)
                want[posKey(x, y)] = `${item}:${count}`;
            const have = {};
            for (const [key, v] of Object.entries(ctx.items))
                have[key] = `${v.item}:${v.count}`;
            return sameDict(want, have);
        },
    },
    {
        key: 'code',
        label: '문제에서 요구한 문법 사용',
        test: (expected, ctx) =>
            expected.every((snippet) =>
                ctx.code.some((code) => code.includes(snippet)),
            ),
    },
];

// 항목별 채점 결과: [{ label, ok }]
export const gradeDetail = (solution, ctx) =>
    CHECKS.filter((check) => check.key in solution).map((check) => ({
        label: check.label,
        ok: check.test(solution[check.key], ctx),
    }));

export const grade = (solution, ctx) =>
    gradeDetail(solution, ctx).every((c) => c.ok);

const now = (withTime) => {
    const d = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    const date = withTime
        ? `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
        : `${d.getFullYear()}.${pad(d.getMonth() + 1)}.${pad(d.getDate())}`;
    return withTime
        ? `${date} ${pad(d.getHours())}:${pad(d.getMinutes())}`
        : date;
};

const storage = {
    get(key) {
        try {
            return localStorage.getItem(key);
        } catch (e) {
            return null;
        }
    },
    set(key, value) {
        try {
            localStorage.setItem(key, value);
        } catch (e) {
            /* 무시 */
        }
    },
};

export class StoryManager {
    constructor({ list, progress, onSelect, getCodes, runForGrading }) {
        this.list = list;
        this.progress = progress;
        this.onSelect = onSelect; // (index) => void, 0이면 선택 해제
        this.getCodes = getCodes; // () => 노트북 셀 코드 목록
        // (index, codes) => 스토리 월드를 처음 상태로 되돌린 뒤 셀 전체를 새로 실행한 결과
        // { state, error } (중지하면 null)
        this.runForGrading = runForGrading;
        this.stories = [];
        this.worlds = {};
        this.solutions = {};
        this.grading = false;

        list.addEventListener('click', (e) => this.handleClick(e));
    }

    async load() {
        const [stories, worlds, solutions] = await Promise.all([
            fetchJson(`${BASE}story.json`),
            fetchJson(`${BASE}worlds.json`),
            fetchJson(`${BASE}solutions.json`),
        ]);
        this.stories = stories;
        this.worlds = worlds;
        this.solutions = solutions;

        const contents = await Promise.all(
            stories.map(async (story) => {
                try {
                    const response = await fetch(story.url);
                    return response.ok
                        ? parser(await response.text()).join('')
                        : '';
                } catch (e) {
                    return '';
                }
            }),
        );
        this.render(contents);
        this.updateProgress();
    }

    get chapters() {
        const chapters = {};
        for (const story of this.stories)
            (chapters[story.chapter] ||= []).push(story.id);
        return chapters;
    }

    isSolved(id) {
        return storage.get(`${id}_check`) === '정답';
    }

    render(contents) {
        const fragment = document.createDocumentFragment();
        this.stories.forEach((story, i) => {
            const li = document.createElement('li');
            li.dataset.id = story.id;
            if (this.isSolved(story.id)) li.classList.add('submit');

            const title = document.createElement('section');
            title.className = 'story-title';
            const heading = document.createElement('h3');
            heading.className = 'sl-ellipsis';
            const num = document.createElement('span');
            num.textContent = `${story.id}편`;
            heading.append(num, story.title);

            const submit = document.createElement('button');
            submit.type = 'button';
            submit.className = 'btn-submit';
            submit.textContent = '제출하기';

            const toggle = document.createElement('button');
            toggle.type = 'button';
            toggle.className = 'btn-toggle';
            toggle.setAttribute('aria-expanded', 'false');
            toggle.innerHTML = '<span class="sr-only">스토리 여닫기</span>';
            title.append(heading, submit, toggle);

            const content = document.createElement('section');
            content.className = 'story-contents';
            content.innerHTML = contents[i];
            const bottomSubmit = submit.cloneNode(true);
            bottomSubmit.title =
                '노트북의 코드를 처음부터 다시 실행해서 채점합니다.';
            content.appendChild(bottomSubmit);

            li.append(title, content);
            fragment.appendChild(li);
        });
        this.list.replaceChildren(fragment);
    }

    updateProgress() {
        if (!this.progress) return;
        const solved = this.stories.filter((s) => this.isSolved(s.id)).length;
        this.progress.textContent = `${solved} / ${this.stories.length} 완료`;
    }

    // 스토리를 열 때 노트북에 넣을 코드: 작성 중 코드 → 제출한 코드 → 기본 코드
    codesFor(index) {
        for (const key of [`${index}_draft`, `${index}_code`]) {
            try {
                const codes = JSON.parse(storage.get(key));
                if (Array.isArray(codes) && codes.length) return codes;
            } catch (e) {
                /* 무시 */
            }
        }
        const basic = this.worlds[index]?.basic_code;
        return [basic ? `${basic}\n` : ''];
    }

    handleClick(e) {
        const button = e.target.closest('button');
        if (!button) return;
        const li = button.closest('.story-list > li');
        if (!li) return;

        if (button.classList.contains('btn-toggle')) {
            const open = !li.classList.contains('active');
            this.list.querySelectorAll(':scope > li').forEach((item) => {
                item.classList.toggle('active', item === li && open);
                item.querySelector('.btn-toggle')?.setAttribute(
                    'aria-expanded',
                    String(item === li && open),
                );
            });
            this.onSelect(open ? Number(li.dataset.id) : 0);
        } else if (button.classList.contains('btn-submit')) {
            this.submit(li);
        }
    }

    setSubmitting(li, submitting) {
        this.grading = submitting;
        li.querySelectorAll('.btn-submit').forEach((button) => {
            button.disabled = submitting;
            button.textContent = submitting ? '채점 중…' : '제출하기';
        });
    }

    // 제출: 스토리 월드를 처음 상태로 되돌리고 노트북 셀 전체를 처음부터 다시 실행해서 채점합니다.
    // (여러 번 실행했거나 이전 출력이 남아 있어도 결과에 영향을 주지 않습니다)
    async submit(li) {
        const index = Number(li.dataset.id);
        if (!li.classList.contains('active')) {
            toast(`${index}편을 먼저 열고 문제를 풀어 주세요.`);
            return;
        }
        if (this.grading) return;

        const codes = this.getCodes();
        if (!codes.some((code) => code.trim())) {
            toast('노트북에 코드를 작성한 뒤 제출해 주세요.');
            return;
        }

        this.setSubmitting(li, true);
        let run;
        try {
            run = await this.runForGrading(index, codes);
        } finally {
            this.setSubmitting(li, false);
        }
        if (!run) return; // 채점 중에 중지함

        storage.set(`${index}_code`, JSON.stringify(codes));
        storage.set(`${index}_time`, now(true));

        const { state, error } = run;
        const character = state.characters[0];
        const ctx = {
            print_data: state.print_data,
            say_data: state.say_data,
            items: state.items,
            character,
            item: character?.items || {},
            code: codes,
        };
        const checks = [
            { label: '코드가 오류 없이 끝까지 실행됨', ok: !error },
            ...gradeDetail(this.solutions[index] || {}, ctx),
        ];
        const passed = checks.every((c) => c.ok);

        const notes = [];
        if (error) {
            notes.push(
                `${error.file ?? '셀'}${error.line ? ` ${error.line}번째 줄` : ''}에서 오류가 났습니다. ${error.name}: ${error.message}`,
            );
        }

        if (passed) {
            storage.set(`${index}_check`, '정답');
            li.classList.add('submit');
            this.updateProgress();
            for (const [chapter, ids] of Object.entries(this.chapters)) {
                if (!ids.includes(index)) continue;
                if (
                    ids.every((id) => this.isSolved(id)) &&
                    !storage.get(`${chapter}_certif_time`)
                ) {
                    storage.set(`${chapter}_certif_time`, now(false));
                    notes.push(
                        `${chapter} 챕터의 모든 문제를 풀었습니다. 인증서를 다운받을 수 있습니다.`,
                    );
                }
            }
        }

        showResultDialog({
            passed,
            title: passed
                ? `${index}편 정답입니다!`
                : `${index}편, 아직 정답이 아니에요`,
            description: passed
                ? '제출한 코드를 처음부터 다시 실행해서 확인했어요.'
                : '제출한 코드를 처음부터 다시 실행해서 확인했어요. 아래에서 ✗ 표시된 항목을 다시 살펴보세요.',
            checks,
            notes,
        });
    }
}
