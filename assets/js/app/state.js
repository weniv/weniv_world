// 월드 상태 모델
//
// 실행과 실행 사이의 월드 상태는 화면(JS)이 가지고 있습니다.
// 코드를 실행할 때 이 상태를 파이썬 워커로 보내고, 실행이 끝나면 워커가 돌려준
// 상태로 바꿉니다. 그래서 워커를 중지(재시작)해도 월드는 그대로 남습니다.
//
// state = {
//   map: { height, width },
//   characters: [{ character, x, y, directions, items, hp, mp }],
//   mobs: [{ name, mob, x, y, directions, hp }],
//   items: { 'x,y': { item, count } },
//   walls: { 'x,y': 'wall' | 'fence' | 'door' },
//   print_data: [], say_data: [],
// }

import { CHARACTER_INFO, DEFAULT_CHARACTER, MOB_INFO } from './config.js';

export const posKey = (x, y) => `${Number(x)},${Number(y)}`;
export const parseKey = (key) => key.split(',').map(Number);

export const newCharacter = (x = 0, y = 0, name = DEFAULT_CHARACTER) => ({
    character: name,
    x,
    y,
    directions: 0, // 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
    items: {},
    hp: CHARACTER_INFO[name].hp,
    mp: CHARACTER_INFO[name].mp,
});

export const newMob = (x, y, mob, name, directions = 0) => ({
    name,
    mob,
    x,
    y,
    directions,
    hp: MOB_INFO[mob].hp,
});

export const defaultState = (height = 5, width = 5) => ({
    map: { height, width },
    characters: [newCharacter()],
    mobs: [],
    items: {},
    walls: {},
    print_data: [],
    say_data: [],
});

export const cloneState = (state) => structuredClone(state);

// assets/data/story/worlds.json 의 한 스토리로 월드를 만듭니다.
export const storyState = (world) => {
    const state = defaultState(world.map.height, world.map.width);
    for (const [x, y, type] of world.walls) state.walls[posKey(x, y)] = type;
    for (const [x, y, item, count] of world.items)
        state.items[posKey(x, y)] = { item, count };
    state.mobs = world.mobs.map((m) =>
        newMob(m.x, m.y, m.mob, m.name, m.directions ?? 0),
    );
    return state;
};

// 워커와 주고받는 형식 (딕셔너리 키 대신 배열 사용)
export const toTransfer = (state) => ({
    map: state.map,
    characters: state.characters,
    mobs: state.mobs,
    items: Object.entries(state.items).map(([key, v]) => [
        ...parseKey(key),
        v.item,
        v.count,
    ]),
    walls: Object.entries(state.walls).map(([key, type]) => [
        ...parseKey(key),
        type,
    ]),
    print_data: state.print_data,
    say_data: state.say_data,
});

export const fromTransfer = (t) => {
    const state = {
        map: t.map,
        characters: t.characters,
        mobs: t.mobs,
        items: {},
        walls: {},
        print_data: t.print_data,
        say_data: t.say_data,
    };
    for (const [x, y, item, count] of t.items)
        state.items[posKey(x, y)] = { item, count };
    for (const [x, y, type] of t.walls) state.walls[posKey(x, y)] = type;
    return state;
};

export const inWorld = (state, x, y) =>
    x >= 0 && y >= 0 && x < state.map.height && y < state.map.width;

export const actorAt = (state, x, y) =>
    state.characters.find((c) => c.x === x && c.y === y) ||
    state.mobs.find((m) => m.x === x && m.y === y);

// 맵 크기에 맞는 벽 자리인지 확인합니다.
// 세로벽: (정수 x, n.5 y), 가로벽: (n.5 x, 정수 y)
export const isValidWall = (map, x, y) => {
    if (!Number.isInteger(x * 2) || !Number.isInteger(y * 2)) return false;
    const xHalf = !Number.isInteger(x);
    const yHalf = !Number.isInteger(y);
    if (xHalf === yHalf) return false;
    return x >= 0 && y >= 0 && x <= map.height - 1 && y <= map.width - 1;
};

// 맵 크기를 바꾸고 범위를 벗어난 데이터를 정리합니다.
export const resizeState = (state, height, width) => {
    state.map = { height, width };
    const inside = (o) => inWorld(state, o.x, o.y);
    state.characters = state.characters.filter(inside);
    state.mobs = state.mobs.filter(inside);
    for (const key of Object.keys(state.items)) {
        const [x, y] = parseKey(key);
        if (!inWorld(state, x, y)) delete state.items[key];
    }
    for (const key of Object.keys(state.walls)) {
        const [x, y] = parseKey(key);
        if (!isValidWall(state.map, x, y)) delete state.walls[key];
    }
};

// 맵 크기에 따른 모든 벽 자리
export const wallSlots = (map) => {
    const slots = [];
    for (let x = 0; x <= map.height - 1; x += 0.5) {
        for (
            let y = Number.isInteger(x) ? 0.5 : 0;
            y <= map.width - 1;
            y += 1
        ) {
            slots.push([x, y]);
        }
    }
    return slots;
};
