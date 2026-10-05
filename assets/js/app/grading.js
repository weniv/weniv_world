// 스토리 채점 규칙 (DOM을 쓰지 않는 순수 함수)
//
// story.js의 제출 기능과 tests/story-solutions.test.mjs(모범 답안 검사)가 함께 씁니다.

import { posKey } from './state.js';

const sameDict = (a = {}, b = {}) => {
    const ka = Object.keys(a);
    const kb = Object.keys(b);
    return ka.length === kb.length && ka.every((k) => a[k] === b[k]);
};

// 공백 개수 차이(띄어쓰기 여러 칸, 탭, 앞뒤 공백)는 채점에서 구분하지 않습니다.
const normalize = (text) => String(text).replace(/\s+/g, ' ').trim();

// 정답 문장이 모두 나와야 하고, 정답이 한 줄이면 마지막 줄이 그 문장이어야 합니다.
const matchLines = (expected, lines) => {
    const want = expected.map(normalize);
    const have = lines.map(normalize);
    return (
        want.every((s) => have.some((line) => line.includes(s))) &&
        !(want.length === 1 && have.length && have[have.length - 1] !== want[0])
    );
};

// 채점 항목 (assets/data/story/solutions.json 의 키)
// 오답일 때 어떤 항목이 틀렸는지만 보여 주고, 정답 값은 보여 주지 않습니다.
const CHECKS = [
    {
        key: 'print_data',
        label: 'print로 출력한 내용',
        test: (expected, ctx) => matchLines(expected, ctx.print_data),
    },
    {
        key: 'say_data',
        label: 'say로 말한 내용',
        test: (expected, ctx) => matchLines(expected, ctx.say_data),
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

// 채점에 쓰는 값: 셀 전체를 다시 실행한 뒤의 월드 상태와 제출한 코드
export const gradingContext = (state, codes) => {
    const character = state.characters[0];
    return {
        print_data: state.print_data,
        say_data: state.say_data,
        items: state.items,
        character,
        item: character?.items || {},
        code: codes,
    };
};

// 항목별 채점 결과: [{ label, ok }]
export const gradeDetail = (solution, ctx) =>
    CHECKS.filter((check) => check.key in solution).map((check) => ({
        label: check.label,
        ok: check.test(solution[check.key], ctx),
    }));

export const grade = (solution, ctx) =>
    gradeDetail(solution, ctx).every((c) => c.ok);
