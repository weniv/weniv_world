// 단독 사이트 머리 줄 (다크 모드, 더보기 메뉴, 프로필, 인증서)
// 노트북·월드·스토리와 월드 메뉴·툴팁 같은 화면 조작은 app/ 의 모듈(app.js, controls.js)에 있습니다.

import { asset, store } from './app/env.js';
import {
    chapterProgress,
    chaptersOf,
    DEFAULT_CHAPTERS,
    downloadUrl,
    drawCertificate,
    formatDate,
    localRecords,
} from './app/records.js';
import { toast } from './app/ui.js';

// 다크모드
const darkModeButton = document.querySelector('.btn-dark-mode');
const applyTheme = (theme) => {
    store.set('color-theme', theme);
    document.documentElement.setAttribute('color-theme', theme);
    darkModeButton.classList.toggle('active', theme === 'dark');
    darkModeButton.setAttribute(
        'name',
        theme === 'dark' ? '다크모드 OFF' : '다크모드 ON',
    );
};
const osColorTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';
applyTheme(store.get('color-theme') || osColorTheme);
darkModeButton.addEventListener('click', () =>
    applyTheme(darkModeButton.classList.contains('active') ? 'light' : 'dark'),
);

// 케밥 메뉴
const kebabMenu = document.querySelector('.btn-kebab');
kebabMenu.addEventListener('click', () => {
    kebabMenu.classList.toggle('active');
});
window.addEventListener('click', (e) => {
    if (!kebabMenu.contains(e.target)) kebabMenu.classList.remove('active');
});

// 프로필 모달
const profileModal = document.querySelector('.profile-modal');
const btnProfileOpen = document.querySelector('.btn-profile');
const btnProfileClose = profileModal.querySelector('.btn-close');
window.addEventListener('click', (e) => {
    if (btnProfileOpen.contains(e.target)) {
        btnProfileOpen.classList.toggle('active');
    } else if (e.target == btnProfileClose) {
        btnProfileOpen.classList.remove('active');
    } else if (!profileModal.contains(e.target)) {
        btnProfileOpen.classList.remove('active');
    }
});

const profileImages = document.querySelectorAll('.profile-img');
const profileName = profileModal.querySelector('.txt-name');
const inpProfileName = profileModal.querySelector('.inp-name');
const setProfileName = (name) => {
    if (name) profileName.textContent = name;
    else profileName.innerHTML = '프로필 편집을 눌러<br>이름을 입력하세요';
};
const initProfile = () => {
    const profile = store.getJson('profile');
    if (profile) {
        profileImages.forEach((profileImage) => {
            profileImage.src = profile?.img.replace(window.location.origin, '');
        });
        setProfileName(profile?.name);
        inpProfileName.value = profile?.name || '';
    }
};
initProfile();

// 변경 설정
const profileImage = document.querySelector('.profileimg-wrap .profile-img');
const PROFILE_SIZE = 256;
const changeProfileImg = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
        const scale = Math.min(
            1,
            PROFILE_SIZE / Math.max(img.width, img.height),
        );
        const canvas = document.createElement('canvas');
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);
        canvas
            .getContext('2d')
            .drawImage(img, 0, 0, canvas.width, canvas.height);
        profileImage.src = canvas.toDataURL('image/jpeg', 0.85);
        URL.revokeObjectURL(url);
    };
    img.onerror = () => {
        URL.revokeObjectURL(url);
        toast('이미지를 불러오지 못했습니다.');
    };
    img.src = url;
};
const inpProfileImg = profileModal.querySelector('.inp-profile');
inpProfileImg.addEventListener('change', (e) => changeProfileImg(e));
const changeProfile = () => {
    const saved = store.set(
        'profile',
        JSON.stringify({
            img: profileImage.src,
            name: inpProfileName.value,
        }),
    );
    if (!saved) {
        toast('프로필을 저장하지 못했습니다. 더 작은 이미지를 사용해 주세요.');
        return;
    }
    setProfileName(inpProfileName.value);
    const profileMenuImg = document.querySelector('button .profile-img');
    profileMenuImg.src = profileImage.src;
};

const profileImageWrap = profileModal.querySelector('.profileimg-wrap');
const profileView = profileModal.querySelector('.profile-view');
const profileEdit = profileModal.querySelector('.profile-edit');
const changeProfileMode = (mode) => {
    profileImageWrap.classList.toggle('active', mode === 'edit');
    profileView.classList.toggle('active', mode === 'view');
    profileEdit.classList.toggle('active', mode === 'edit');
};

profileModal.querySelector('.btn-edit').addEventListener('click', () => {
    changeProfileMode('edit');
    initProfile();
});
profileModal.querySelector('.btn-confirm').addEventListener('click', () => {
    changeProfileMode('view');
    changeProfile();
});
profileModal.querySelector('.btn-cancel').addEventListener('click', () => {
    changeProfileMode('view');
    initProfile();
});

/* 인증서 모달 */
const certifBtn = document.querySelector('.btn-certif');
const certifWrap = document.querySelector('.certif-wrap');
const certifClose = certifWrap.querySelector('.btn-close');
const certifList = certifWrap.querySelector('.certif-list');
let storyChapter = DEFAULT_CHAPTERS;

window.addEventListener('click', (e) => {
    if (certifBtn.contains(e.target)) {
        certifBtn.classList.toggle('active');
    } else if (e.target == certifClose) {
        certifBtn.classList.remove('active');
    } else if (!certifWrap.contains(e.target)) {
        certifBtn.classList.remove('active');
    }
    if (certifBtn.classList.contains('active')) {
        updateCertifItem();
    }
});

const setCertifItem = () => {
    certifList.replaceChildren();
    Object.keys(storyChapter).forEach((chapter) => {
        const li = document.createElement('li');
        li.classList.add('certif-item');

        li.innerHTML = `
        <p class="title">${chapter}</p>
        <p class="progress"><span class="solved">0</span>/<span class="total">${storyChapter[chapter].length}</span></p>
        <div class="progress-bar">
            <div class="progress-bar-inner"></div>
        </div>
        <button class="btn-download-certif"><span class="sr-only">인증서 다운로드</span></button>
        `;
        li.querySelector('.btn-download-certif').addEventListener(
            'click',
            async () => {
                try {
                    const url = await drawCertificate({
                        chapter,
                        name: localRecords.name(),
                        // 날짜를 남기지 못한 경우 오늘 날짜
                        date:
                            localRecords.certificateDate(chapter) ||
                            formatDate(),
                    });
                    downloadUrl(url, `${chapter}_인증서.png`);
                } catch (err) {
                    toast(err.message);
                }
            },
        );
        certifList.append(li);
    });
};

const updateCertifItem = () => {
    const certifItems = certifList.querySelectorAll('.certif-item');
    chapterProgress(storyChapter, localRecords.isSolved).forEach(
        ({ solved, total, done }, index) => {
            const li = certifItems[index];
            li.querySelector('.solved').innerText = solved;
            li.querySelector('.progress-bar-inner').style.transform =
                `scaleX(${(solved / total) * 100}%)`;
            li.querySelector('.btn-download-certif').toggleAttribute(
                'disabled',
                !done,
            );
        },
    );
};
setCertifItem();
updateCertifItem();

fetch(asset('data/story/story.json'))
    .then((response) => response.json())
    .then((stories) => {
        storyChapter = chaptersOf(stories);
        setCertifItem();
        updateCertifItem();
    })
    .catch(() => {});
