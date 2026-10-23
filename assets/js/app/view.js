// 월드 화면 그리기
//
// sync(state)로 상태에 맞게 화면을 맞추고, move/turn 같은 메서드로
// 재생기(player.js)가 애니메이션을 보여 줍니다.

import { CELL, CHARACTER_INFO, MOB_INFO } from './config.js';
import { asset, store } from './env.js';
import { posKey, wallSlots } from './state.js';

export const actorKey = (who) => `${who.kind}:${who.name}`;

const statusHidden = () => (store.get('status-mode') || 'hide') === 'hide';

// 칸 안에서 스프라이트를 가운데에 놓기 위한 보정값(px)
const OFFSET = {
    character: { top: 21, left: 20 },
    mob: { top: 29, left: 33 },
};

const setPosition = (el, kind, x, y) => {
    el.style.top = `${x * CELL + OFFSET[kind].top}px`;
    el.style.left = `${y * CELL + OFFSET[kind].left}px`;
};

const createBar = (type, value, max) => {
    const item = document.createElement('div');
    item.className = `status-item ${type}`;
    if (statusHidden()) item.classList.add('hide');
    const bar = document.createElement('div');
    bar.className = 'bar';
    const text = document.createElement('span');
    text.className = 'text';
    item.append(bar, text);
    updateBar(item, value, max);
    return item;
};

const updateBar = (item, value, max) => {
    if (!item) return;
    const ratio = max ? Math.max(0, Math.min(1, value / max)) : 0;
    item.querySelector('.bar').style.transform = `scaleX(${ratio})`;
    item.querySelector('.text').textContent = `${value}/${max}`;
};

const spriteUrl = (sprite, direction) =>
    asset(`img/characters/${sprite}-${direction}.webp`);

const drawSprite = (el, direction) => {
    el.dataset.directions = direction;
    el.style.backgroundImage = `url("${spriteUrl(el.dataset.sprite, direction)}")`;
};

// 도는 중이면 멈춘다 (월드를 다시 그리거나 건너뛰기로 방향을 바로 정할 때)
const stopTurn = (el) => {
    const turn = el.wwTurn;
    if (!turn) return;
    el.wwTurn = null;
    turn.animation?.cancel();
};

const reducedMotion = () =>
    globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false;

// 돌 때 새 방향 그림이 비어 보이지 않게 네 방향을 미리 받아 둔다
const preloadedSprites = new Set();
const preloadSprites = (sprite) => {
    if (preloadedSprites.has(sprite) || typeof Image === 'undefined') return;
    preloadedSprites.add(sprite);
    for (let d = 0; d < 4; d += 1) new Image().src = spriteUrl(sprite, d);
};

export class WorldView extends EventTarget {
    constructor(root) {
        super();
        this.root = root;
        this.map = null;
        this.container = null;
        this.cells = new Map(); // 'x,y' -> .map-item
        this.walls = new Map(); // 'x,y' -> .wall
        this.actors = new Map(); // 'kind:name' -> element
    }

    // ------------------------------------------------------------------
    // 맵 만들기
    build(map) {
        this.map = { ...map };
        this.cells.clear();
        this.walls.clear();
        this.actors.clear();

        const container = document.createElement('div');
        container.className = 'map-container';

        const mapItems = document.createElement('div');
        mapItems.className = 'map-items';
        mapItems.style.gridTemplateRows = `repeat(${map.height}, 10rem)`;
        mapItems.style.gridTemplateColumns = `repeat(${map.width}, 10rem)`;
        for (let x = 0; x < map.height; x++) {
            for (let y = 0; y < map.width; y++) {
                const cell = document.createElement('div');
                cell.className = 'map-item';
                cell.dataset.x = x;
                cell.dataset.y = y;
                mapItems.appendChild(cell);
                this.cells.set(posKey(x, y), cell);
            }
        }

        const wallContainer = document.createElement('div');
        wallContainer.className = 'wall-container';
        for (const [x, y] of wallSlots(map)) {
            const wall = document.createElement('div');
            wall.className = 'wall';
            wall.dataset.x = x;
            wall.dataset.y = y;
            wall.dataset.type = '';
            wall.dataset.direction = Number.isInteger(x)
                ? 'portrait'
                : 'landscape';
            wall.style.top = `${(x + 0.5) * CELL}px`;
            wall.style.left = `${(y + 0.5) * CELL + 1}px`;
            wallContainer.appendChild(wall);
            this.walls.set(posKey(x, y), wall);
        }

        container.append(mapItems, wallContainer);
        this.container = container;
        this.mapItems = mapItems;
        this.wallContainer = wallContainer;
        this.root.replaceChildren(container);
        this.dispatchEvent(new CustomEvent('build'));
    }

    // ------------------------------------------------------------------
    // 상태에 맞게 화면 맞추기 (애니메이션 없음)
    sync(state) {
        if (
            !this.map ||
            this.map.height !== state.map.height ||
            this.map.width !== state.map.width
        ) {
            this.build(state.map);
        }

        for (const [key, wall] of this.walls) {
            const type = state.walls[key] || '';
            if (wall.dataset.type !== type) wall.dataset.type = type;
        }

        for (const [key, cell] of this.cells) {
            const [x, y] = key.split(',').map(Number);
            const item = state.items[key];
            this.setItem(x, y, item?.item ?? null, item?.count ?? 0, cell);
        }

        const alive = new Set();
        for (const c of state.characters) {
            const who = { kind: 'character', name: c.character };
            alive.add(actorKey(who));
            const el = this.ensureActor(who, c.character);
            this.place(el, who.kind, c.x, c.y, false);
            this.setSprite(el, c.directions);
            const max = CHARACTER_INFO[c.character] || { hp: 100, mp: 100 };
            updateBar(el.querySelector('.status-item.hp'), c.hp, max.hp);
            updateBar(el.querySelector('.status-item.mp'), c.mp, max.mp);
        }
        for (const m of state.mobs) {
            const who = { kind: 'mob', name: m.name };
            alive.add(actorKey(who));
            const el = this.ensureActor(who, m.mob);
            this.place(el, who.kind, m.x, m.y, false);
            this.setSprite(el, m.directions);
            updateBar(
                el.querySelector('.status-item.hp'),
                m.hp,
                MOB_INFO[m.mob]?.hp ?? 50,
            );
        }
        for (const [key, el] of this.actors) {
            if (!alive.has(key)) {
                el.remove();
                this.actors.delete(key);
            }
        }
    }

    // ------------------------------------------------------------------
    // 캐릭터 / 몹
    ensureActor(who, sprite) {
        const key = actorKey(who);
        let el = this.actors.get(key);
        if (el && el.dataset.sprite === sprite) return el;
        el?.remove();

        el = document.createElement('div');
        el.className = `${who.kind} ${sprite}`;
        el.dataset.kind = who.kind;
        el.dataset.name = who.name;
        el.dataset.sprite = sprite;
        el.dataset.directions = '0';

        const status = document.createElement('div');
        status.className = 'status-container';
        if (who.kind === 'character') {
            const max = CHARACTER_INFO[sprite] || { hp: 100, mp: 100 };
            status.append(
                createBar('hp', max.hp, max.hp),
                createBar('mp', max.mp, max.mp),
            );
        } else {
            const max = MOB_INFO[sprite]?.hp ?? 50;
            status.append(createBar('hp', max, max));
        }
        el.appendChild(status);
        preloadSprites(sprite);
        this.setSprite(el, 0);
        this.container.appendChild(el);
        this.actors.set(key, el);
        return el;
    }

    actor(who) {
        return this.actors.get(actorKey(who));
    }

    place(el, kind, x, y, animate, duration = 0) {
        if (!animate) {
            el.style.transition = 'none';
            setPosition(el, kind, x, y);
            // 다음 애니메이션이 이 위치에서 시작하도록 스타일을 바로 반영합니다.
            void el.offsetWidth;
            el.style.transition = '';
        } else {
            el.style.transition = `top ${duration}s linear, left ${duration}s linear, scale ${duration / 2}s ease-out`;
            setPosition(el, kind, x, y);
        }
        el.dataset.x = x;
        el.dataset.y = y;
    }

    setSprite(el, direction) {
        stopTurn(el);
        drawSprite(el, direction);
    }

    addActor(who, data) {
        const sprite = who.kind === 'mob' ? data.mob : data.character;
        const el = this.ensureActor(who, sprite);
        this.place(el, who.kind, data.x, data.y, false);
        this.setSprite(el, data.directions ?? 0);
    }

    moveActor(who, to, duration) {
        const el = this.actor(who);
        if (el) this.place(el, who.kind, to[0], to[1], true, duration * 0.9);
    }

    jumpActor(who, to, duration) {
        const el = this.actor(who);
        if (!el) return;
        this.place(el, who.kind, to[0], to[1], true, duration * 0.9);
        el.style.scale = '1.2';
        setTimeout(() => {
            el.style.scale = '1';
        }, duration * 500);
    }

    // 제자리에서 도는 것처럼 보이게: 세로축으로 반 바퀴 접었다가(옆모습) 새 방향 그림으로 바꿔 다시 편다.
    // 걷기(moveActor)와 같은 시간(한 칸 시간의 0.9)을 쓰고, 너무 빠르거나 움직임 줄이기 설정이면 바로 바꾼다.
    turnActor(who, direction, duration = 0) {
        const el = this.actor(who);
        if (!el) return;
        const ms = duration * 900;
        if (ms < 80 || typeof el.animate !== 'function' || reducedMotion()) {
            this.setSprite(el, direction);
            return;
        }
        stopTurn(el);
        const turn = {};
        el.wwTurn = turn;
        const half = ms / 2;
        turn.animation = el.animate(
            [{ rotate: 'y 0deg' }, { rotate: 'y 90deg' }],
            { duration: half, easing: 'ease-in' },
        );
        turn.animation.finished
            .then(() => {
                if (el.wwTurn !== turn) return;
                drawSprite(el, direction);
                turn.animation = el.animate(
                    [{ rotate: 'y -90deg' }, { rotate: 'y 0deg' }],
                    { duration: half, easing: 'ease-out' },
                );
                return turn.animation.finished;
            })
            .then(() => {
                if (el.wwTurn === turn) el.wwTurn = null;
            })
            .catch(() => {});
    }

    removeActor(who, delay = 0) {
        const el = this.actor(who);
        if (!el) return;
        this.actors.delete(actorKey(who));
        setTimeout(() => el.remove(), delay);
    }

    setBars(who, { hp, mp, maxHp, maxMp }) {
        const el = this.actor(who);
        if (!el) return;
        if (hp != null)
            updateBar(el.querySelector('.status-item.hp'), hp, maxHp);
        if (mp != null)
            updateBar(el.querySelector('.status-item.mp'), mp, maxMp);
    }

    bubble(who, text, time = 5000) {
        const el = this.actor(who);
        if (!el) return;
        const bubble = document.createElement('div');
        bubble.className = 'speech-bubble';
        bubble.textContent = text;
        el.appendChild(bubble);
        setTimeout(() => bubble.remove(), time);
    }

    // ------------------------------------------------------------------
    // 아이템 / 벽 / 효과
    setItem(x, y, name, count, cell = this.cells.get(posKey(x, y))) {
        if (!cell) return;
        let box = cell.querySelector('.item-container');
        if (!name || count <= 0) {
            box?.remove();
            return;
        }
        if (!box) {
            box = document.createElement('div');
            box.className = 'item-container';
            box.innerHTML =
                '<img class="item" alt=""><span class="count"></span>';
            cell.appendChild(box);
        }
        const img = box.querySelector('img');
        if (box.dataset.item !== name) {
            box.dataset.item = name;
            img.src = asset(`img/item/${name}.png`);
            img.alt = name;
        }
        const countEl = box.querySelector('.count');
        countEl.textContent = count;
        countEl.dataset.digits = String(count).length;
    }

    setWall(x, y, type) {
        const wall = this.walls.get(posKey(x, y));
        if (wall) wall.dataset.type = type || '';
    }

    drawLine(from, direction, duration) {
        const line = document.createElement('div');
        line.className = 'line';
        line.style.left = `${from[1] * CELL + 52}px`;
        line.style.top = `${from[0] * CELL + 52}px`;
        line.style.rotate = `${[0, -90, -180, 90][direction]}deg`;
        line.style.animationDuration = `${Math.max(0.1, duration * 2)}s`;
        this.container.appendChild(line);
    }

    clearLines() {
        this.container
            ?.querySelectorAll('.line')
            .forEach((line) => line.remove());
    }

    // 이동 경로, 말풍선, 공격 효과 등 이전 실행의 흔적을 지웁니다.
    clearEffects() {
        this.container
            ?.querySelectorAll('.line, .speech-bubble, .attack')
            .forEach((el) => el.remove());
    }

    attackEffect(target, skill, duration) {
        const effect = document.createElement('div');
        effect.className = 'attack';
        effect.style.left = `${target[1] * CELL + 36}px`;
        effect.style.top = `${target[0] * CELL + 34}px`;
        effect.style.backgroundImage = `url("${asset(`img/weapon/${skill}.png`)}")`;
        this.container.appendChild(effect);
        setTimeout(
            () => effect.remove(),
            Math.max(300, Math.min(1000, duration * 1000)),
        );
    }
}
