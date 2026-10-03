// 월드 편집: 벽, 아이템, 몹 배치/삭제, 맵 크기 조절, 캐릭터 정보

import { CHARACTER_INFO, MAP_MAX, MAP_MIN } from './config.js';
import {
    actorAt,
    cloneState,
    newCharacter,
    newMob,
    posKey,
    resizeState,
} from './state.js';
import { isTyping, showAlert, toast } from './ui.js';

const DIRECTION_TEXT = ['0 (동쪽)', '1 (북쪽)', '2 (서쪽)', '3 (남쪽)'];

export class WorldEditor {
    constructor({ world, view, mapSection, isBusy, onCharacterReset }) {
        this.world = world;
        this.view = view;
        this.mapSection = mapSection;
        this.isBusy = isBusy; // () => 코드 실행/재생 중인지
        this.onCharacterReset = onCharacterReset;
        this.wallType = 'wall';
        this.selection = null; // { kind: 'item' | 'mob', name }
        this.bubbleTimer = null;

        this.bindToolbar();
        this.bindMap();
        this.bindSliders();
        this.bindKeys();
        view.addEventListener('build', () => this.applyPointerMode());
    }

    get state() {
        return this.world.state;
    }

    canEdit() {
        return !this.isBusy() && !this.world.story.mode;
    }

    blocked() {
        if (this.canEdit()) return false;
        toast(
            this.isBusy()
                ? '실행 중에는 월드를 편집할 수 없습니다.'
                : '스토리 모드에서는 월드를 편집할 수 없습니다.',
        );
        return true;
    }

    // ------------------------------------------------------------------
    // 도구 모음 (벽 종류, 아이템/몹 선택)
    bindToolbar() {
        document
            .querySelectorAll("input[name='wall-type']")
            .forEach((input) => {
                input.addEventListener('change', () => {
                    this.wallType = input.value;
                    this.applyPointerMode();
                });
            });
        document.querySelectorAll("input[name='item']").forEach((input) => {
            input.addEventListener('click', () =>
                this.toggleSelection('item', input.id),
            );
        });
        document.querySelectorAll("input[name='mob']").forEach((input) => {
            input.addEventListener('click', () =>
                this.toggleSelection('mob', input.id),
            );
        });
        // 아이템 패널을 다시 열었을 때 선택 표시 유지
        document
            .querySelector('.btn-assets')
            ?.addEventListener('click', () => this.markSelectedLabel());
    }

    toggleSelection(kind, name) {
        const same =
            this.selection &&
            this.selection.kind === kind &&
            this.selection.name === name;
        this.clearSelection();
        if (!same) {
            this.selection = { kind, name };
            this.markSelectedLabel();
            const cursor =
                kind === 'item'
                    ? `url(assets/img/item/${name}.png) 16 16, copy`
                    : `url(assets/img/characters/${name}-0.webp) 16 16, copy`;
            this.mapSection.style.cursor = cursor;
        }
        this.applyPointerMode();
    }

    markSelectedLabel() {
        if (!this.selection) return;
        document
            .querySelector(`label[for='${this.selection.name}']`)
            ?.classList.add('select');
    }

    clearSelection() {
        if (this.selection) {
            document
                .querySelector(`label[for='${this.selection.name}']`)
                ?.classList.remove('select');
        }
        this.selection = null;
        this.mapSection.style.cursor = '';
        this.mapSection.querySelector('.mouse-tooltip')?.remove();
        this.applyPointerMode();
    }

    // 아이템/몹을 배치할 때는 벽이 클릭을 가로채지 않게 합니다.
    applyPointerMode() {
        const walls = this.view.wallContainer;
        if (!walls) return;
        walls.classList.toggle(
            'walls-locked',
            Boolean(this.selection) || this.world.story.mode,
        );
        walls.classList.toggle('delete-mode', this.wallType === 'delete');
        this.view.mapItems.style.pointerEvents = this.world.story.mode
            ? 'none'
            : '';
    }

    // ------------------------------------------------------------------
    // 맵 클릭
    bindMap() {
        const section = this.mapSection;

        section.addEventListener('click', (e) => {
            const actor = e.target.closest('.character');
            if (actor) {
                this.showCharacterInfo(actor);
                return;
            }
            if (e.target.closest('.character-info-bubble')) return;

            const wall = e.target.closest('.wall');
            if (wall) {
                this.clickWall(wall);
                return;
            }
            const cell = e.target.closest('.map-item');
            if (cell && this.selection)
                this.clickCell(Number(cell.dataset.x), Number(cell.dataset.y));
        });

        section.addEventListener('contextmenu', (e) => {
            if (!e.target.closest('.map-container')) return;
            if (this.selection) {
                e.preventDefault();
                this.clearSelection();
                return;
            }
            if (this.world.story.mode) return;
            e.preventDefault();
            this.deleteAt(e.target);
        });

        section.addEventListener('mousemove', (e) => {
            if (!this.selection) return;
            const container = section.querySelector('.map-container');
            if (!container) return;
            let tooltip = section.querySelector('.mouse-tooltip');
            if (!tooltip) {
                tooltip = document.createElement('div');
                tooltip.className = 'mouse-tooltip';
                tooltip.innerHTML =
                    '<img src="assets/img/icon/icon-mouse-click.svg" alt=""><p>우클릭으로 취소</p>';
                container.appendChild(tooltip);
            }
            const rect = container.getBoundingClientRect();
            tooltip.style.left = `${e.clientX - rect.left + 50}px`;
            tooltip.style.top = `${e.clientY - rect.top + 20}px`;
        });

        section.addEventListener('mouseleave', () =>
            section.querySelector('.mouse-tooltip')?.remove(),
        );
    }

    clickWall(wall) {
        if (this.world.story.mode || this.selection) return;
        if (this.blocked()) return;
        const key = posKey(wall.dataset.x, wall.dataset.y);
        const current = this.state.walls[key];
        if (this.wallType === 'delete') {
            if (current) this.world.edit((s) => delete s.walls[key]);
        } else if (!current) {
            this.world.edit((s) => (s.walls[key] = this.wallType));
        }
    }

    clickCell(x, y) {
        if (this.blocked()) return;
        const { kind, name } = this.selection;

        if (kind === 'item') {
            const input = prompt(
                '추가할 아이템 개수를 입력하세요\n(* 추가할 위치에 다른 아이템이 있는 경우 사라집니다.)',
                '1',
            );
            if (input === null) return;
            if (!/^\d+$/.test(input.trim()) || Number(input) < 1) {
                showAlert('1 이상의 자연수를 입력해주세요');
                return;
            }
            const count = Number(input);
            this.world.edit((s) => {
                const key = posKey(x, y);
                const current = s.items[key];
                s.items[key] = {
                    item: name,
                    count:
                        current?.item === name ? current.count + count : count,
                };
            });
        } else {
            if (actorAt(this.state, x, y)) {
                showAlert('다른 캐릭터 또는 몹이 있습니다.');
                return;
            }
            const input = prompt('추가할 몹의 이름을 작성해주세요');
            if (input === null) return;
            const mobName = input.trim();
            if (!mobName) {
                showAlert('이름을 입력해주세요');
                return;
            }
            if (this.state.mobs.some((m) => m.name === mobName)) {
                showAlert('해당 이름을 갖는 몹이 이미 맵에 존재합니다');
                return;
            }
            this.world.edit((s) => s.mobs.push(newMob(x, y, name, mobName)));
        }
        this.clearSelection();
    }

    // 마우스 오른쪽 클릭으로 아이템(칸 전체), 몹, 벽 삭제
    deleteAt(target) {
        if (!this.canEdit()) {
            this.blocked();
            return;
        }
        const mob = target.closest('.mob');
        if (mob) {
            const name = mob.dataset.name;
            this.world.edit(
                (s) => (s.mobs = s.mobs.filter((m) => m.name !== name)),
            );
            return;
        }
        const wall = target.closest('.wall');
        if (wall && wall.dataset.type) {
            const key = posKey(wall.dataset.x, wall.dataset.y);
            this.world.edit((s) => delete s.walls[key]);
            return;
        }
        const cell = target.closest('.map-item');
        if (cell && cell.querySelector('.item-container')) {
            const key = posKey(cell.dataset.x, cell.dataset.y);
            this.world.edit((s) => delete s.items[key]);
        }
    }

    // ------------------------------------------------------------------
    // 맵 크기 조절
    bindSliders() {
        this.sliderX = document.getElementById('map-range-x');
        this.sliderY = document.getElementById('map-range-y');
        this.textX = document.getElementById('map-text-x');
        this.textY = document.getElementById('map-text-y');
        [this.sliderX, this.sliderY].forEach((slider) => {
            slider.min = MAP_MIN;
            slider.max = MAP_MAX;
            slider.addEventListener('input', () => this.resize());
        });
        this.world.addEventListener('change', () => this.syncSliders());
        this.syncSliders();
    }

    syncSliders() {
        const { height, width } = this.state.map;
        this.sliderX.value = height;
        this.sliderY.value = width;
        this.textX.textContent = height;
        this.textY.textContent = width;
    }

    resize() {
        const height = Number(this.sliderX.value);
        const width = Number(this.sliderY.value);
        if (this.blocked()) {
            this.syncSliders();
            return;
        }
        const main = this.state.characters[0];
        if (main && (main.x > height - 1 || main.y > width - 1)) {
            showAlert('기본 캐릭터의 위치보다 작게 맵을 설정할 수 없습니다.');
            this.syncSliders();
            return;
        }
        this.world.edit((s) => resizeState(s, height, width));
    }

    // ------------------------------------------------------------------
    // 키보드
    bindKeys() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeCharacterInfo();
                if (this.selection) this.clearSelection();
            }
            if (
                (e.ctrlKey || e.metaKey) &&
                !e.shiftKey &&
                e.key.toLowerCase() === 'z' &&
                !isTyping(e.target)
            ) {
                if (!this.canEdit()) return;
                e.preventDefault();
                toast(
                    this.world.undo()
                        ? '되돌렸습니다.'
                        : '더 되돌릴 내용이 없습니다.',
                );
            }
        });
    }

    // ------------------------------------------------------------------
    // 캐릭터 정보 말풍선
    showCharacterInfo(el) {
        if (el.querySelector('.character-info-bubble')) return;
        this.closeCharacterInfo();
        const c = this.state.characters.find(
            (ch) => ch.character === el.dataset.name,
        );
        if (!c) return;
        const max = CHARACTER_INFO[c.character] || { hp: 100, mp: 100 };
        const items = Object.keys(c.items).length
            ? Object.entries(c.items)
                  .map(([k, v]) => `${k}: ${v}`)
                  .join(', ')
            : '없음';

        const bubble = document.createElement('div');
        bubble.className = 'character-info-bubble info-modal';
        bubble.innerHTML = `
            <p class="info-title">캐릭터 정보</p>
            <dl class="info-list"></dl>
            <button type="button" class="btn-reset init-character">
                <span class="sr-only">캐릭터 초기화</span>
            </button>`;
        const list = bubble.querySelector('.info-list');
        for (const [title, value] of [
            ['이름', c.character],
            ['x좌표', c.x],
            ['y좌표', c.y],
            ['방향', DIRECTION_TEXT[c.directions] ?? c.directions],
            ['아이템', items],
            ['체력', `${c.hp} / ${max.hp}`],
            ['마나', `${c.mp} / ${max.mp}`],
        ]) {
            const row = document.createElement('div');
            row.className = 'info-item';
            const dt = document.createElement('dt');
            dt.className = 'bubble-body-item-title';
            dt.textContent = title;
            const dd = document.createElement('dd');
            dd.className = 'bubble-body-item-content';
            dd.textContent = value;
            row.append(dt, dd);
            list.appendChild(row);
        }
        bubble
            .querySelector('.init-character')
            .addEventListener('click', (e) => {
                e.stopPropagation();
                this.closeCharacterInfo();
                this.resetCharacter(c.character);
            });
        el.appendChild(bubble);
        this.bubbleTimer = setTimeout(() => this.closeCharacterInfo(), 5000);
    }

    closeCharacterInfo() {
        clearTimeout(this.bubbleTimer);
        document
            .querySelectorAll('.character-info-bubble')
            .forEach((b) => b.remove());
    }

    resetCharacter(name) {
        if (this.isBusy()) {
            toast('실행 중에는 캐릭터를 초기화할 수 없습니다.');
            return;
        }
        const s = cloneState(this.state);
        const fresh = newCharacter(0, 0, name);
        const blocker = s.mobs.find((m) => m.x === 0 && m.y === 0);
        if (blocker) s.mobs = s.mobs.filter((m) => m !== blocker);
        const index = s.characters.findIndex((c) => c.character === name);
        if (index >= 0) s.characters[index] = fresh;
        else s.characters.unshift(fresh);
        this.world.replace(s);
        this.onCharacterReset?.();
    }
}
