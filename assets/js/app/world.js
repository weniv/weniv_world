// 월드 상태 보관 + 되돌리기(Ctrl+Z)

import { cloneState, defaultState } from './state.js';

const HISTORY_LIMIT = 50;

export class World extends EventTarget {
    constructor() {
        super();
        this.state = defaultState();
        this.history = [];
        this.story = { mode: false, index: 0 };
    }

    // 화면 편집(벽/아이템/몹 배치 등): 되돌리기 기록을 남기고 화면을 다시 그립니다.
    edit(mutate) {
        this.history.push(cloneState(this.state));
        if (this.history.length > HISTORY_LIMIT) this.history.shift();
        mutate(this.state);
        this.emit();
    }

    // 상태 전체 교체 (초기화, 스토리 불러오기 등)
    replace(state, { render = true } = {}) {
        this.state = state;
        this.history = [];
        if (render) this.emit();
    }

    undo() {
        const previous = this.history.pop();
        if (!previous) return false;
        // 터미널 출력 기록은 되돌리지 않습니다.
        previous.print_data = this.state.print_data;
        previous.say_data = this.state.say_data;
        this.state = previous;
        this.emit();
        return true;
    }

    emit() {
        this.dispatchEvent(new CustomEvent('change', { detail: this.state }));
    }
}
