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

const observer = new MutationObserver((mutationsList) => {
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
    observer.observe(target, {
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

// world 메뉴 - 버튼 이벤트 추가
const worldMenu = document.querySelector('.world-menu');

worldMenu.addEventListener('click', (e) => {
    const target = e.target;
    if (target.classList.contains('btn-toggle')) {
        target.classList.toggle('active');
    }
});

// modal
const wallButton = document.querySelector('.btn-wall');

const createModal = (type, className, contents) => {
    const modalDiv = document.createElement('div');
    modalDiv.setAttribute('class', `${type}-modal ${className}`);

    modalDiv.innerHTML += contents;

    return modalDiv;
};

wallButton.addEventListener('click', () => {
    const contents = `
        <div class="input-wrap">
            <input type="radio" name="wall-type" id="wall" value="wall" checked>
            <label for="wall">wall(기본): orange</label>
        </div>
        <div class="input-wrap">
            <input type="radio" name="wall-type" id="door" value="door">
            <label for="door">door: sienna</label>
        </div>
        <div class="input-wrap">
            <input type="radio" name="wall-type" id="fence" value="fence">
            <label for="fence">fence: seagreen</label>
        </div>
        <div class="input-wrap">
            <input type="radio" name="wall-type" id="delete" value="delete">
            <label for="delete">delete</label>
        </div>
    `;

    const modalElement = createModal('controller', 'wall-type', contents);
    wallButton.parentNode.append(modalElement);
});
