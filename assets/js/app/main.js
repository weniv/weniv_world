// 단독 사이트(world.weniv.co.kr)·설치판 진입점
//
// 앱 기능은 app.js(createWorldApp)에 있고, 여기서는 머리 줄의 스토리 버튼만 잇습니다.
// 프로필·인증서·다크 모드는 event.js, 학습 보고서는 report.js 가 맡습니다.

import { createWorldApp } from './app.js';
import { notifyHost } from './embed.js';

const storyButton = document.querySelector('.btn-story');

const app = createWorldApp({
    root: document,
    onStoryModeChange: (open) => storyButton.classList.toggle('active', open),
});

storyButton.addEventListener('click', () => app.setStoryMode(!app.storyMode));

app.ready.then(() => notifyHost('ready')).catch(() => {});

// 개발자 도구 / 자동 테스트에서 상태를 확인하기 위한 핸들
window.__wenivDebug = app;
