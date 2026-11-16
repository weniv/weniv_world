// 효과음 (공격, 포션 먹기)
//
// 위니브 스페이스 던전(FE/src/audio/sfx.ts)과 같은 파일·재생 구간·음량을 씁니다.
// <audio> 대신 Web Audio를 쓰는 까닭: 연달아 공격할 때 소리가 겹쳐 울려야 하고,
// 스킬마다 재생 속도로 음정을 바꾸며, 한 번 받은 소리를 다시 받지 않기 때문입니다.
//
// 이 파일은 밖으로 오류를 던지지 않습니다. 소리가 안 나는 것은 불편이지만
// 실행 결과 재생이 멈추는 것은 고장이라, 실패하면 조용히 넘어갑니다.

import { asset } from './env.js';

// 0이면 끕니다. 던전의 기본 효과음 크기와 같습니다.
const VOLUME = 0.6;

// start/end: mp3 앞뒤 무음을 건너뛰는 재생 구간(초). gain: 파일마다 다른 녹음 크기를 맞춘 값.
const SOUNDS = {
    swing: { src: 'sound/swing.mp3', start: 0.024, end: 0.82, gain: 0.28, minGapMs: 120, maxVoices: 3 },
    potion: { src: 'sound/potion.mp3', start: 0.025, end: 0.8, gain: 4.3, minGapMs: 120, maxVoices: 2 },
};

// 스킬별 휘두르는 소리 음정 (던전의 WEAPON_PITCH와 같은 값)
const SKILL_PITCH = {
    'claw-yellow': 1.1,
    'claw-white': 1.1,
    beam: 1.35,
    explosion: 0.75,
};
const PITCH_JITTER = 0.06;

let ctx = null;
let master = null;
const buffers = new Map(); // 이름 → AudioBuffer | null(실패)
const loading = new Map();
const lastAt = {};
const voices = {};

function ensureContext() {
    if (ctx) return ctx;
    const AudioCtx = globalThis.AudioContext || globalThis.webkitAudioContext;
    if (!AudioCtx) return null;
    try {
        ctx = new AudioCtx();
        master = ctx.createGain();
        master.gain.value = VOLUME;
        master.connect(ctx.destination);
    } catch (e) {
        ctx = null;
        master = null;
    }
    return ctx;
}

function load(name) {
    if (buffers.has(name)) return Promise.resolve(buffers.get(name));
    if (loading.has(name)) return loading.get(name);
    const audio = ensureContext();
    if (!audio) return Promise.resolve(null);
    const work = (async () => {
        try {
            const res = await fetch(asset(SOUNDS[name].src));
            if (!res.ok) throw new Error(String(res.status));
            const decoded = await audio.decodeAudioData(await res.arrayBuffer());
            buffers.set(name, decoded);
            return decoded;
        } catch (e) {
            buffers.set(name, null); // 실패한 소리는 다시 받지 않고 무음으로 둡니다
            return null;
        } finally {
            loading.delete(name);
        }
    })();
    loading.set(name, work);
    return work;
}

// 브라우저는 사용자가 누르기 전에는 소리를 막아 둡니다. 실행 버튼·Shift+Enter 같은
// 첫 입력에 오디오를 깨우고 소리를 미리 받아 두어, 첫 attack()부터 제때 울리게 합니다.
export function primeSounds() {
    if (VOLUME <= 0) return;
    const audio = ensureContext();
    if (!audio) return;
    if (audio.state === 'suspended') audio.resume().catch(() => {});
    Object.keys(SOUNDS).forEach((name) => load(name));
}

export function setupSoundPrimer(target = globalThis.document) {
    if (!target?.addEventListener) return () => {};
    const events = ['pointerdown', 'keydown'];
    const prime = () => {
        primeSounds();
        events.forEach((type) => target.removeEventListener(type, prime, true));
    };
    events.forEach((type) => target.addEventListener(type, prime, true));
    return () =>
        events.forEach((type) => target.removeEventListener(type, prime, true));
}

function fadeOut(node, audio) {
    try {
        const now = audio.currentTime;
        node.gainNode.gain.cancelScheduledValues(now);
        node.gainNode.gain.setValueAtTime(node.gainNode.gain.value, now);
        node.gainNode.gain.linearRampToValueAtTime(0, now + 0.005);
        node.stop(now + 0.006);
    } catch (e) {
        /* 이미 끝난 소리 */
    }
}

function start(name, buffer, pitch) {
    const def = SOUNDS[name];
    try {
        const node = ctx.createBufferSource();
        node.buffer = buffer;
        node.playbackRate.value =
            pitch * (1 + (Math.random() * 2 - 1) * PITCH_JITTER);
        const gain = ctx.createGain();
        gain.gain.value = def.gain;
        node.connect(gain);
        gain.connect(master);
        node.gainNode = gain;

        const live = (voices[name] ??= []);
        while (live.length >= def.maxVoices) fadeOut(live.shift(), ctx);
        live.push(node);
        node.onended = () => {
            const i = live.indexOf(node);
            if (i >= 0) live.splice(i, 1);
            try {
                node.disconnect();
                gain.disconnect();
            } catch (e) {
                /* 이미 끊김 */
            }
        };
        const length = Math.max(0.01, (def.end ?? buffer.duration) - (def.start ?? 0));
        node.start(0, def.start ?? 0, length);
    } catch (e) {
        /* 오디오를 쓸 수 없는 환경 — 무음 */
    }
}

// name: 'swing' | 'potion', skill: 공격 스킬 이름(음정)
export function playSound(name, { skill } = {}) {
    if (VOLUME <= 0 || !SOUNDS[name]) return;
    const audio = ensureContext();
    if (!audio || !master) return;
    if (audio.state === 'suspended') audio.resume().catch(() => {});

    const now = globalThis.performance?.now() ?? Date.now();
    if (now - (lastAt[name] ?? -Infinity) < SOUNDS[name].minGapMs) return;
    lastAt[name] = now;

    const pitch = SKILL_PITCH[skill] ?? 1;
    const buffer = buffers.get(name);
    if (buffer === null) return;
    if (buffer) start(name, buffer, pitch);
    // 아직 못 받았으면 받는 대로 울립니다 (첫 실행 직후 한 번만 조금 늦을 수 있습니다).
    else load(name).then((b) => b && start(name, b, pitch));
}
