// llms.txt(AI가 읽는 사이트 소개)와 robots.txt가 실제 스토리·파일과 어긋나지 않는지 확인
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { test } from 'node:test';

const SITE = 'https://world.weniv.co.kr/';
const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8');
const exists = (path) => existsSync(new URL(`../${path}`, import.meta.url));

const llms = read('llms.txt');
const robots = read('robots.txt');
const stories = JSON.parse(read('assets/data/story/story.json'));

test('llms.txt에 스토리가 빠짐없이, 지금 제목·주제·주소로 적혀 있다', () => {
    for (const story of stories) {
        const url = new URL(story.url, SITE).href;
        const line = `- [${story.id}. ${story.title}](${url}): ${story.evaluation.join(', ')}`;
        assert.ok(llms.includes(line), `llms.txt에 없는 줄: ${line}`);
    }
    const listed = llms.match(/assets\/data\/story\/story\d+\.md/g) ?? [];
    assert.equal(listed.length, stories.length, '없어진 스토리가 llms.txt에 남아 있습니다');
});

test('llms.txt가 가리키는 이 사이트의 파일이 저장소에 있다', () => {
    const links = [...llms.matchAll(/\]\((https:\/\/world\.weniv\.co\.kr\/[^)]*)\)/g)].map((m) => m[1]);
    assert.ok(links.length > stories.length);
    for (const link of links) {
        const path = decodeURIComponent(new URL(link).pathname).slice(1);
        assert.ok(exists(path), `없는 파일을 가리킵니다: ${link}`);
    }
});

test('llms.txt에 적은 함수가 파이썬 엔진에 있다', () => {
    const source = read('assets/py/built_in_functions.py') + read('assets/py/modules.py');
    const names = new Set();
    for (const [, code] of llms.matchAll(/`([^`]+)`/g)) {
        // `move()`처럼 부르는 이름 (leo.move()처럼 객체에 딸린 것은 뺀다)
        for (const [, name] of code.matchAll(/(?<![.\w])([a-z_]+)\(/g)) names.add(name);
        // `from modules import a, b`로 가져오는 이름
        const imported = code.match(/^from modules import (.+)$/);
        if (imported) imported[1].split(',').forEach((name) => names.add(name.trim()));
    }
    // 파이썬에 원래 있는 함수
    names.delete('print');
    names.delete('input');
    assert.ok(names.size >= 20, `함수 이름을 ${names.size}개만 찾았습니다`);
    for (const name of names) {
        assert.ok(source.includes(`def ${name}(`), `엔진에 없는 함수: ${name}`);
    }
});

test('robots.txt가 사이트는 열어 두고 개발용 폴더만 뺀다', () => {
    const rules = robots
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter((line) => line && !line.startsWith('#'));
    assert.equal(rules[0], 'User-agent: *');
    assert.ok(rules.includes('Allow: /'));
    assert.equal(rules.filter((line) => line.startsWith('User-agent:')).length, 1);

    const blocked = rules.filter((line) => line.startsWith('Disallow:')).map((line) => line.slice('Disallow:'.length).trim());
    assert.ok(blocked.length > 0);
    for (const path of blocked) {
        // 앱과 학습 자료(index.html, assets/, llms.txt)는 막지 않는다
        assert.ok(!'/assets/'.startsWith(path) && !'/llms.txt'.startsWith(path) && !'/index.html'.startsWith(path), `막으면 안 되는 곳: ${path}`);
        assert.ok(exists(path.slice(1)), `없는 곳을 막고 있습니다: ${path}`);
    }
});
