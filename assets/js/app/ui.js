// 알림창, 토스트, 속도 조절, 단축키 도움말

// ------------------------------------------------------------------
// 알림창 (이전 show_modal_alert)
export const showAlert = (
    message,
    type = 'error',
    { duration = 2500 } = {},
) => {
    const modal = document.createElement('div');
    modal.className = `modal alert show${type === 'success' ? ' success' : ''}`;
    modal.setAttribute('role', 'alertdialog');

    const text = document.createElement('p');
    text.className = 'text';
    text.innerText = message;

    const button = document.createElement('button');
    button.className = 'confirm';
    button.type = 'button';
    button.innerText = '확인';

    modal.append(text, button);
    const close = () => modal.remove();
    button.addEventListener('click', close);
    if (duration) setTimeout(close, duration);

    (document.querySelector('.world-map') || document.body).appendChild(modal);
    button.focus({ preventScroll: true });
    return modal;
};

export const toast = (message) => {
    let wrap = document.querySelector('.toast-wrap');
    if (!wrap) {
        wrap = document.createElement('div');
        wrap.className = 'toast-wrap';
        wrap.setAttribute('aria-live', 'polite');
        document.body.appendChild(wrap);
    }
    const item = document.createElement('p');
    item.className = 'toast';
    item.textContent = message;
    wrap.appendChild(item);
    setTimeout(() => item.remove(), 2000);
};

// 채점 결과 창: 항목별 ✓/✗를 보여 주고, 확인을 누를 때까지 닫히지 않습니다.
export const showResultDialog = ({
    passed,
    title,
    description,
    checks = [],
    notes = [],
}) => {
    const dialog = document.createElement('dialog');
    dialog.className = `result-dialog ${passed ? 'passed' : 'failed'}`;
    dialog.setAttribute('aria-labelledby', 'result-dialog-title');

    const heading = document.createElement('h2');
    heading.id = 'result-dialog-title';
    heading.textContent = title;

    const desc = document.createElement('p');
    desc.className = 'result-desc';
    desc.textContent = description;

    const list = document.createElement('ul');
    list.className = 'result-checks';
    for (const check of checks) {
        const item = document.createElement('li');
        item.className = check.ok ? 'ok' : 'fail';
        const mark = document.createElement('span');
        mark.className = 'mark';
        mark.setAttribute('aria-hidden', 'true');
        mark.textContent = check.ok ? '✓' : '✗';
        const label = document.createElement('span');
        label.textContent = check.label;
        const sr = document.createElement('span');
        sr.className = 'sr-only';
        sr.textContent = check.ok ? ' (통과)' : ' (다시 확인 필요)';
        item.append(mark, label, sr);
        list.appendChild(item);
    }

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'confirm';
    button.textContent = '확인';
    button.addEventListener('click', () => dialog.close());

    // 내용은 안쪽 상자에 넣습니다. (dialog 자체를 누른 경우 = 배경을 누른 경우)
    const body = document.createElement('div');
    body.className = 'result-body';
    body.append(heading, desc, list);
    for (const note of notes) {
        const p = document.createElement('p');
        p.className = 'result-note';
        p.textContent = note;
        body.appendChild(p);
    }
    body.appendChild(button);
    dialog.appendChild(body);
    dialog.addEventListener('close', () => dialog.remove());
    // 바깥(배경)을 누르면 닫습니다.
    dialog.addEventListener('click', (e) => {
        if (e.target === dialog) dialog.close();
    });

    document.body.appendChild(dialog);
    dialog.showModal();
    button.focus();
    return dialog;
};

// event.js 같은 일반 스크립트에서도 쓸 수 있게 공개합니다.
window.WenivUI = { showAlert, toast };

// ------------------------------------------------------------------
// 속도 조절
// 슬라이더 1~100. 50(기본)에서 한 칸에 1초, 1에서 2.5초,
// 100에서 0.02초(50배속)가 되도록 두 구간을 지수 곡선으로 잇습니다.
// 이전에는 2차식이라 오른쪽 끝(100)에서 0.46초로 거의 빨라지지 않았습니다.
export const speedToSeconds = (value) => {
    const v = Math.min(100, Math.max(1, Number(value) || 50));
    if (v <= 50) return 2.5 * Math.pow(1.0 / 2.5, (v - 1) / 49);
    return Math.pow(0.02, (v - 50) / 50);
};

export const createSpeedControl = (slider, output) => {
    const render = () => {
        const seconds = speedToSeconds(slider.value);
        const ratio = 1 / seconds;
        output.textContent = `×${ratio < 10 ? ratio.toFixed(1) : Math.round(ratio)}`;
        slider.setAttribute(
            'aria-valuetext',
            `한 칸에 ${seconds.toFixed(2)}초`,
        );
    };
    try {
        const saved = localStorage.getItem('speed');
        if (saved) slider.value = saved;
    } catch (e) {
        /* 저장소를 쓸 수 없는 환경 */
    }
    slider.addEventListener('input', () => {
        render();
        try {
            localStorage.setItem('speed', slider.value);
        } catch (e) {
            /* 무시 */
        }
    });
    render();
    return { seconds: () => speedToSeconds(slider.value) };
};

// ------------------------------------------------------------------
// 단축키 도움말 (? 키)
const SHORTCUTS = [
    ['Shift + Enter', '셀 실행 후 다음 셀로 이동'],
    ['Ctrl(⌘) + Enter', '셀 실행'],
    ['Esc', '캐릭터 정보 닫기 / 도움말 닫기'],
    ['Ctrl(⌘) + Z (월드에서)', '벽·아이템·몹 배치 되돌리기'],
    ['마우스 오른쪽 클릭', '아이템·몹·벽 삭제, 배치 취소'],
    ['?', '단축키 도움말'],
];

export const isTyping = (target) =>
    target instanceof Element &&
    target.closest(
        'input, textarea, select, [contenteditable="true"], .cm-editor',
    ) !== null;

export const setupShortcutHelp = () => {
    let dialog = null;
    const close = () => {
        dialog?.remove();
        dialog = null;
    };
    const open = () => {
        if (dialog) return close();
        dialog = document.createElement('section');
        dialog.className = 'shortcut-help';
        dialog.setAttribute('role', 'dialog');
        dialog.setAttribute('aria-label', '단축키 도움말');
        dialog.innerHTML = `
            <h2>단축키</h2>
            <dl>${SHORTCUTS.map(([k, d]) => `<div><dt><kbd>${k}</kbd></dt><dd>${d}</dd></div>`).join('')}</dl>
            <button type="button" class="btn-close"><span class="sr-only">닫기</span></button>`;
        dialog.querySelector('.btn-close').addEventListener('click', close);
        document.body.appendChild(dialog);
    };
    document.addEventListener('keydown', (e) => {
        if (e.key === '?' && !isTyping(e.target)) {
            e.preventDefault();
            open();
        } else if (e.key === 'Escape') {
            close();
        }
    });
};
