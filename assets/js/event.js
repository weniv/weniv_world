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

const setSliderTrack = (element) => {
    const value = element.value;
    const max = parseInt(element.max);
    const min = parseInt(element.min);
    const width = ((value - min) / (max - min)) * 100;
    const color = getComputedStyle(element).color;

    element.style.background = `linear-gradient(to right, ${color} 0%, ${color} ${width}%, #d9dbe0 ${width}%, #d9dbe0 100%)`;
};

sliders.forEach((slider) => {
    setSliderTrack(slider);

    slider.addEventListener('input', (e) => {
        if (e.target.tagName == 'INPUT') {
            setSliderTrack(e.target);
        }
    });
});

// 다크모드
const userColorTheme = localStorage.getItem('color-theme');
const osColorTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';
const darkModeButton = document.querySelector('.btn-dark-mode');

const getUserTheme = () => (userColorTheme ? userColorTheme : osColorTheme);

window.onload = () => {
    if (getUserTheme === 'dark') {
        localStorage.setItem('color-theme', 'dark');
        document.documentElement.setAttribute('color-theme', 'dark');
        darkModeButton.classList.add('active');
    } else {
        localStorage.setItem('color-theme', 'light');
        document.documentElement.setAttribute('color-theme', 'light');
    }
};

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
