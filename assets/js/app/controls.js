// 월드 메뉴·툴팁·슬라이더·체력 표시 같은 화면 조작
//
// 단독 사이트와 위니버시티가 함께 씁니다. setupControls(root)는 앱을 내릴 때 부를 정리 함수를 돌려줍니다.
// (프로필·인증서·다크 모드처럼 머리 줄에 있는 것은 각 사이트가 따로 만듭니다)

import { store } from './env.js';
import { toast } from './ui.js';

// ------------------------------------------------------------------
// 툴팁: name 속성의 글자를 마우스를 올렸을 때 보여 줍니다.
const createTooltip = (textContent) => {
    const div = document.createElement('div');
    div.setAttribute('class', 'tooltip');
    div.textContent = textContent;
    return div;
};

const removeTooltip = (target) => {
    target.querySelector(':scope > .tooltip')?.remove();
};

export const addTooltipEvent = (target) => {
    target.addEventListener('mouseover', () => {
        const text = target.getAttribute('name');
        if (!text || target.querySelector(':scope > .tooltip')) return;
        const tooltip = createTooltip(text);
        tooltip.style.top = `${target.clientHeight + 10}px`;
        target.append(tooltip);
    });
    target.addEventListener('mouseout', () => removeTooltip(target));
    target.addEventListener('click', () => removeTooltip(target));
};

// ------------------------------------------------------------------
// 슬라이더 채운 부분 색
const setSliderTrack = (element) => {
    const min = parseInt(element.min);
    const max = parseInt(element.max);
    const width = ((element.value - min) / (max - min)) * 100;
    const color = getComputedStyle(element).color;
    element.style.background = `linear-gradient(to right, ${color} 0%, ${color} ${width}%, #d9dbe0 ${width}%, #d9dbe0 100%)`;
};

// ------------------------------------------------------------------
// 체력·마나 표시 (월드 메뉴의 체력 버튼)
export const getStatusMode = () => store.get('status-mode') || 'hide';

export function setupControls(root) {
    const $ = (selector) => root.querySelector(selector);
    const $$ = (selector) => [...root.querySelectorAll(selector)];
    const cleanups = [];
    const listen = (target, type, handler, options) => {
        target.addEventListener(type, handler, options);
        cleanups.push(() => target.removeEventListener(type, handler, options));
    };
    const observe = (observer) => cleanups.push(() => observer.disconnect());

    $$('.show-tooltip').forEach(addTooltipEvent);

    // 슬라이더: 값이 바뀌면(값 글자가 바뀌면) 채운 부분을 다시 그립니다.
    $$('.slider').forEach((slider) => setSliderTrack(slider));
    const sliderObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            const slider = mutation.target.previousElementSibling;
            if (slider?.classList.contains('slider')) setSliderTrack(slider);
        });
    });
    $$('.slider + strong').forEach((target) =>
        sliderObserver.observe(target, {
            childList: true,
            characterData: true,
        }),
    );
    observe(sliderObserver);

    // 월드 메뉴: 버튼을 누르면 그 버튼의 창만 열고, 바깥을 누르면 닫습니다.
    const worldMenu = $('.world-menu');
    const world = $('.world');
    if (worldMenu && world) {
        const toggleActive = (target) => {
            const current = worldMenu.querySelector('.active');
            if (target.classList?.contains('btn-toggle')) {
                if (target === current) target.classList.remove('active');
                else {
                    current?.classList.remove('active');
                    target.classList.add('active');
                }
            } else {
                current?.classList.remove('active');
            }
        };
        listen(worldMenu, 'click', (e) => {
            if (e.target.tagName === 'BUTTON') toggleActive(e.target);
        });
        listen(window, 'click', (e) => {
            if (e.target === worldMenu || !worldMenu.contains(e.target))
                toggleActive(e.target);
        });

        // 메뉴 창이 월드 오른쪽 밖으로 나가면 폭을 줄입니다.
        const resizeModal = (target, ratio) => {
            target.style.maxWidth = `${target.clientWidth * ratio}px`;
        };
        const resizeObserver = new ResizeObserver(() => {
            const activeButton = world.querySelector('.active');
            const modal = activeButton
                ?.closest('li')
                ?.querySelector('.controller-modal');
            if (!modal) return;
            const modalRect = modal.getBoundingClientRect();
            const containerRect = world.getBoundingClientRect();
            if (modalRect.right >= containerRect.right) {
                const term = modalRect.right - containerRect.right;
                resizeModal(modal, 1 - term / modalRect.width);
            } else {
                modal.style.maxWidth = '700px';
            }
        });
        resizeObserver.observe(world);
        resizeObserver.observe(document.body);
        observe(resizeObserver);

        const intersectionObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting)
                        entry.target.style.maxWidth = '700px';
                    else if (entry.intersectionRatio < 1)
                        resizeModal(entry.target, entry.intersectionRatio);
                });
            },
            { root: null, rootMargin: '0px', threshold: 0.1 },
        );
        $$('.controller-modal').forEach((modal) =>
            intersectionObserver.observe(modal),
        );
        observe(intersectionObserver);
    }

    // 함수·변수 목록: 누르면 클립보드에 복사합니다.
    const copyToClipboard = (e) => {
        const target = e.target;
        if (
            target.tagName !== 'BUTTON' ||
            !target.classList.contains('code-item')
        )
            return;
        navigator.clipboard
            ?.writeText(target.innerText)
            .then(() => toast('클립보드에 복사되었습니다.'))
            .catch(() => {});
    };
    ['.function-list', '.variable-list'].forEach((selector) => {
        const list = $(selector);
        if (list) listen(list, 'click', copyToClipboard);
    });

    // 체력·마나 표시 켜고 끄기
    const statusButton = $('.btn-status');
    const app = $('#app');
    if (statusButton && app) {
        const srText = statusButton.querySelector('.sr-only');
        const render = () => {
            const show = getStatusMode() === 'show';
            statusButton.classList.toggle('hide', !show);
            const label = show ? '체력 상태 숨기기' : '체력 상태 보기';
            statusButton.setAttribute('name', label);
            if (srText) srText.innerText = label;
            app.querySelectorAll('.status-item').forEach((item) =>
                item.classList.toggle('hide', !show),
            );
        };
        listen(statusButton, 'click', () => {
            store.set(
                'status-mode',
                getStatusMode() === 'show' ? 'hide' : 'show',
            );
            render();
        });
        render();
    }

    return () => cleanups.splice(0).forEach((cleanup) => cleanup());
}

// ------------------------------------------------------------------
// 영역 크기 조절 (.resizer 를 끌어서 옆 영역의 폭·높이를 바꿉니다)
export function setupResizers(root) {
    const cleanups = [];
    root.querySelectorAll('.resizer').forEach((resizer) => {
        const direction =
            resizer.getAttribute('data-direction') || 'horizontal';
        const target = resizer.getAttribute('data-target') || 'prev';
        const prevSibling = resizer.previousElementSibling;
        const nextSibling = resizer.nextElementSibling;
        const targetSibling = target === 'prev' ? prevSibling : nextSibling;
        let x = 0;
        let y = 0;
        let startHeight = 0;
        let startWidth = 0;

        const onMove = (e) => {
            const dx = target === 'prev' ? e.clientX - x : x - e.clientX;
            const dy = target === 'prev' ? e.clientY - y : y - e.clientY;
            const parent = resizer.parentNode.getBoundingClientRect();
            if (direction === 'vertical') {
                targetSibling.style.height = `${((startHeight + dy) * 100) / parent.height}%`;
            } else {
                targetSibling.style.width = `${((startWidth + dx) * 100) / parent.width}%`;
            }
            const cursor =
                direction === 'horizontal' ? 'col-resize' : 'row-resize';
            resizer.style.cursor = cursor;
            document.body.style.cursor = cursor;
            for (const sibling of [prevSibling, nextSibling]) {
                sibling.style.userSelect = 'none';
                sibling.style.pointerEvents = 'none';
            }
        };
        const onUp = () => {
            resizer.style.removeProperty('cursor');
            document.body.style.removeProperty('cursor');
            for (const sibling of [prevSibling, nextSibling]) {
                sibling.style.removeProperty('user-select');
                sibling.style.removeProperty('pointer-events');
            }
            resizer.classList.remove('active');
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
        };
        const onDown = (e) => {
            x = e.clientX;
            y = e.clientY;
            const rect = targetSibling.getBoundingClientRect();
            startHeight = rect.height;
            startWidth = rect.width;
            resizer.classList.add('active');
            document.addEventListener('mousemove', onMove);
            document.addEventListener('mouseup', onUp);
        };
        resizer.addEventListener('mousedown', onDown);
        cleanups.push(() => {
            resizer.removeEventListener('mousedown', onDown);
            onUp();
        });
    });
    return () => cleanups.splice(0).forEach((cleanup) => cleanup());
}
