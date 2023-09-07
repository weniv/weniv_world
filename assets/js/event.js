const $btnQue = document.querySelectorAll('.btn-que');

// tutorial 로딩
$btnQue.forEach((element) => {
    element.addEventListener('click', function (e) {
        document.getElementById('t' + PAGE_NAME).classList.remove('active');
        PAGE_NAME = e.target.id.slice(1);
        document.getElementById('t' + PAGE_NAME).classList.add('active');
        history.pushState(null, PAGE_NAME, `?page=${PAGE_NAME}`);
        // // 문제 이동 시 에러 메시지 초기화
        // document.getElementById("result_desc").textContent = "";
        render(); // parser에 문제 렌더링
    });
});

// input range 스타일 적용을 위한 코드
const sliders = document.querySelectorAll('.slider');
const rangeValueText = document.querySelectorAll('.slider + strong');

const setSliderTrack = (element) => {
    const value = element.value;
    const max = parseInt(element.max);
    const min = parseInt(element.min);
    const width = ((value - min) / (max - min)) * 100;
    const color = getComputedStyle(element).color;

    element.style.background = `linear-gradient(to right, ${color} 0%, ${color} ${width}%, #d9dbe0 ${width}%, #d9dbe0 100%)`;
};

const sliderValueObserver = new MutationObserver((mutationsList) => {
    mutationsList.forEach((mutation) => {
        if (mutation.type === 'childList') {
            const slider = mutation.target.previousElementSibling;
            setSliderTrack(slider);
        }
    });
});

sliders.forEach((slider) => {
    setSliderTrack(slider);
});

rangeValueText.forEach((target) => {
    sliderValueObserver.observe(target, {
        childList: true,
        characterData: true,
    });
});

// 다크모드
const userColorTheme = localStorage.getItem('color-theme');
const osColorTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';
const darkModeButton = document.querySelector('.btn-dark-mode');

const getUserTheme = () => (userColorTheme ? userColorTheme : osColorTheme);

window.addEventListener('load', () => {
    if (getUserTheme() === 'dark') {
        localStorage.setItem('color-theme', 'dark');
        document.documentElement.setAttribute('color-theme', 'dark');
        darkModeButton.classList.add('active');
    } else {
        localStorage.setItem('color-theme', 'light');
        document.documentElement.setAttribute('color-theme', 'light');
        darkModeButton.classList.remove('active');
    }
});

darkModeButton.addEventListener('click', () => {
    if (darkModeButton.classList.contains('active')) {
        localStorage.setItem('color-theme', 'light');
        document.documentElement.setAttribute('color-theme', 'light');
        darkModeButton.classList.remove('active');
    } else {
        localStorage.setItem('color-theme', 'dark');
        document.documentElement.setAttribute('color-theme', 'dark');
        darkModeButton.classList.add('active');
    }
});

// world 메뉴 - 버튼 이벤트 추가(모달 여닫기)
const worldMenu = document.querySelector('.world-menu');

const toggleActive = (target) => {
    const currentActiveItem = worldMenu.querySelector('.active');

    if (target.classList.contains('btn-toggle')) {
        if (target == currentActiveItem) {
            target.classList.remove('active');
        } else {
            currentActiveItem && currentActiveItem.classList.remove('active');
            target.classList.add('active');
        }
    } else {
        currentActiveItem && currentActiveItem.classList.remove('active');
    }
};

worldMenu.addEventListener('click', (e) => {
    if (e.target.tagName == 'BUTTON') {
        toggleActive(e.target);
    }
});

window.addEventListener('click', (e) => {
    if (!worldMenu.contains(e.target)) {
        toggleActive(e.target);
    }
});

// 스토리 section / 스토리 컨텐츠 여닫기
const storyShowButton = document.querySelector('.btn-story');
const storyCloseButton = document.querySelector('.btn-close-story');
const storySection = document.querySelector('.story');
const storyList = document.querySelector('.story-list');

storyShowButton.addEventListener('click', () => {
    storyShowButton.classList.toggle('active');
    storySection.classList.toggle('show');
});

storyCloseButton.addEventListener('click', () => {
    storyShowButton.classList.remove('active');
    storySection.classList.remove('show');
});

storyList.addEventListener('click', (e) => {
    if (
        (e.target.tagName =
            'BUTTON' && e.target.classList.contains('btn-toggle'))
    ) {
        e.target.closest('li').classList.toggle('active');
    }
});
