// 이벤트 재생기
//
// 파이썬 워커가 돌려준 이벤트를 순서대로 화면에 보여 줍니다.
// 이동처럼 시간이 걸리는 동작은 속도 설정만큼 기다리고, print/say 같은 출력은
// 기다리지 않습니다. 속도를 바꾸면 다음 동작부터 바로 적용됩니다.

import { CHARACTER_INFO } from './config.js';

const TIMED = new Set([
    'move',
    'turn',
    'jump',
    'pick',
    'put',
    'open_door',
    'attack',
    'eat',
]);

export class Player extends EventTarget {
    constructor({ view, terminal, notebook, alert, stepSeconds }) {
        super();
        this.view = view;
        this.terminal = terminal;
        this.notebook = notebook;
        this.alert = alert;
        this.stepSeconds = stepSeconds;
        this.queue = [];
        this.playing = false;
        this.skipping = false;
        this.wake = null;
        this.idleWaiters = [];
    }

    get busy() {
        return this.playing || this.queue.length > 0;
    }

    push(events) {
        this.queue.push(...events);
        if (!this.playing) this.loop();
    }

    // 남은 애니메이션을 건너뛰고 결과(출력, 최종 상태)만 바로 보여 줍니다.
    skip() {
        if (!this.busy) return;
        this.skipping = true;
        this.wake?.();
    }

    // 남은 이벤트를 모두 버립니다. (월드 초기화)
    clear() {
        this.queue.length = 0;
        if (this.playing) {
            this.skipping = true;
            this.wake?.();
        }
    }

    whenIdle() {
        if (!this.busy) return Promise.resolve();
        return new Promise((resolve) => this.idleWaiters.push(resolve));
    }

    sleep(seconds) {
        if (this.skipping || seconds <= 0) return Promise.resolve();
        return new Promise((resolve) => {
            const timer = setTimeout(done, seconds * 1000);
            function done() {
                clearTimeout(timer);
                resolve();
            }
            this.wake = done;
        });
    }

    async loop() {
        this.playing = true;
        this.dispatchEvent(new CustomEvent('busy', { detail: true }));
        while (this.queue.length) {
            const event = this.queue.shift();
            try {
                await this.apply(event);
            } catch (err) {
                console.error('[player]', event, err);
            }
        }
        this.playing = false;
        this.skipping = false;
        this.wake = null;
        this.dispatchEvent(new CustomEvent('busy', { detail: false }));
        this.idleWaiters.splice(0).forEach((resolve) => resolve());
    }

    async apply(e) {
        const step = this.stepSeconds();
        const animate = !this.skipping;
        const { view } = this;

        switch (e.t) {
            case 'move':
                if (animate) {
                    view.drawLine(e.frm, e.dir, step);
                    view.moveActor(e.who, e.to, step);
                }
                break;
            case 'jump':
                if (animate) view.jumpActor(e.who, e.to, step);
                break;
            case 'turn':
                if (animate) view.turnActor(e.who, e.dir);
                break;
            case 'pick':
            case 'put':
            case 'set_item':
                if (animate) view.setItem(e.pos[0], e.pos[1], e.item, e.count);
                break;
            case 'open_door':
                if (animate) view.setWall(e.pos[0], e.pos[1], '');
                break;
            case 'attack':
                if (animate) this.applyAttack(e, step);
                break;
            case 'eat':
            case 'stat': {
                if (!animate) break;
                const max = CHARACTER_INFO[e.who.name] || { hp: 100, mp: 100 };
                view.setBars(e.who, {
                    hp: e.hp,
                    mp: e.mp,
                    maxHp: max.hp,
                    maxMp: max.mp,
                });
                break;
            }
            case 'add':
                if (animate) view.addActor(e.who, e.data);
                break;
            case 'say':
                if (animate) view.bubble(e.who, e.text, e.time);
                break;
            case 'print':
                this.terminal.append(e.text);
                break;
            case 'alert':
                if (animate) this.alert(e.message, e.level);
                break;
            case 'error':
                this.terminal.append(`${e.name}: ${e.message}`, {
                    error: true,
                });
                if (e.hint)
                    this.terminal.append(`힌트: ${e.hint}`, { error: true });
                if (animate)
                    this.alert(
                        `${e.message}${e.hint ? `\n${e.hint}` : ''}`,
                        'error',
                    );
                break;
            case 'cell-output':
                this.notebook.showOutput(e.cell, e.result);
                break;
            case 'sync':
                view.sync(e.state);
                break;
            case 'call':
                e.fn();
                break;
            default:
                break;
        }

        if (TIMED.has(e.t)) await this.sleep(step);
    }

    applyAttack(e, step) {
        const { view } = this;
        view.attackEffect(e.target, e.skill, step);
        if (e.mp != null) {
            const max = CHARACTER_INFO[e.who.name] || { hp: 100, mp: 100 };
            view.setBars(e.who, { mp: e.mp, maxMp: max.mp });
        }
        const victim = e.victim;
        if (victim) {
            const who = { kind: victim.kind, name: victim.name };
            view.setBars(who, { hp: victim.hp, maxHp: victim.maxHp });
            if (victim.removed)
                view.removeActor(who, Math.max(200, step * 1000));
        }
    }
}
