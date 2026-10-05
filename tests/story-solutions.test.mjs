// 스토리 모범 답안 검사
//
// tests/story_solutions/{번호}.py 의 모범 답안을 실제 파이썬 엔진(runner.run_all)으로 실행하고,
// 화면의 제출 기능과 같은 채점 함수(app/grading.js)로 채점합니다.
// 지도(worlds.json)·정답(solutions.json)·채점 규칙 중 하나라도 어긋나 통과할 수 없는 편이 생기면 실패합니다.
//
// 파이썬 실행 파일은 PYTHON 환경 변수로 바꿀 수 있습니다. (기본값: python)

import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { gradeDetail, gradingContext } from '../assets/js/app/grading.js';
import { fromTransfer, storyState, toTransfer } from '../assets/js/app/state.js';

const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8');
const readJson = (path) => JSON.parse(read(path));

const stories = readJson('../assets/data/story/story.json');
const worlds = readJson('../assets/data/story/worlds.json');
const solutions = readJson('../assets/data/story/solutions.json');
const prelude = read('./story_solutions/_prelude.py');

const jobs = stories.map(({ id }) => {
    const answer = read(`./story_solutions/${id}.py`).replace(
        '# {basic_code}',
        worlds[id].basic_code ?? '',
    );
    return {
        id,
        answer,
        codes: [prelude, answer],
        state: toTransfer(storyState(worlds[id])),
    };
});

const run = spawnSync(process.env.PYTHON || 'python', ['tests/run_story.py'], {
    cwd: new URL('..', import.meta.url),
    input: JSON.stringify(jobs.map(({ codes, state }) => ({ codes, state }))),
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
});
if (run.error || run.status !== 0)
    throw new Error(`run_story.py 실행 실패: ${run.error?.message ?? run.stderr}`);
const results = JSON.parse(run.stdout);

test('모든 스토리에 지도와 정답 데이터가 있다', () => {
    for (const { id } of stories) {
        assert.ok(worlds[id], `${id}편 worlds.json 없음`);
        assert.ok(Object.keys(solutions[id] ?? {}).length, `${id}편 solutions.json 없음`);
    }
});

jobs.forEach((job, i) => {
    test(`${job.id}편 모범 답안이 채점을 통과한다`, () => {
        const result = results[i];
        assert.ok(result.state, `입력을 요구함: ${JSON.stringify(result)}`);
        assert.equal(
            result.error,
            null,
            `${result.error?.file} ${result.error?.line}번째 줄: ${result.error?.name}: ${result.error?.message}`,
        );
        // '요구 문법' 검사는 학습자가 쓴 코드만 봅니다. (공통 도우미 제외)
        const ctx = gradingContext(fromTransfer(result.state), [job.answer]);
        const failed = gradeDetail(solutions[job.id], ctx).filter((c) => !c.ok);
        assert.deepEqual(
            failed.map((c) => c.label),
            [],
            `print: ${JSON.stringify(ctx.print_data)} say: ${JSON.stringify(ctx.say_data)} ` +
                `위치: ${ctx.character?.x},${ctx.character?.y} 아이템: ${JSON.stringify(ctx.item)} ` +
                `맵: ${JSON.stringify(ctx.items)}`,
        );
    });
});
