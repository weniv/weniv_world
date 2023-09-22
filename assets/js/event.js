const $btnQue = document.querySelectorAll('.btn-que');
// tutorial 로딩
$btnQue.forEach((element) => {
    element.addEventListener('click', function(e) {
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

// 스토리 section / 스토리 컨텐츠 여닫기
const storyShowButton = document.querySelector('.btn-story');
const storyCloseButton = document.querySelector('.btn-close-story');
const storySection = document.querySelector('.story');
const storyList = document.querySelector('.story-list');
const storyResizer = document.querySelector('.story-resizer');

storyShowButton.addEventListener('click', () => {
    storyShowButton.classList.toggle('active');
    storySection.classList.toggle('show');
    storyResizer.style.display = 'block';
});

storyCloseButton.addEventListener('click', () => {
    storyShowButton.classList.remove('active');
    storySection.classList.remove('show');
    storyResizer.style.display = 'none';
});

storyList.addEventListener('click', (e) => {
    if (
        (e.target.tagName =
            'BUTTON' && e.target.classList.contains('btn-toggle'))
    ) {
        e.target.closest('li').classList.toggle('active');
    }
});

// 툴팁 표시
const tooltipTargetElement = document.querySelectorAll('.show-tooltip');

const createTooltip = (textContent) => {
    const div = document.createElement('div');
    div.setAttribute('class', 'tooltip');
    div.textContent = textContent;

    return div;
};

const addTooltip = (target) => {
    const textContent = target.getAttribute('name');
    const targetHeight = target.clientHeight;
    const tooltip = createTooltip(textContent);
    tooltip.style.top = `${targetHeight + 10}px`;

    target.append(tooltip);
};

const removeTooltip = (target) => {
    const tooltip = target.querySelector('.tooltip');

    tooltip.remove();
};

const setTooltipPosition = (target) => {
    const targetHeight = target.clientHeight;
    console.log(targetHeight);
};

tooltipTargetElement.forEach((target) => {
    target.addEventListener('mouseover', () => {
        setTimeout(() => {
            addTooltip(target);
        }, 500);
    });

    target.addEventListener('mouseout', () => {
        setTimeout(() => {
            removeTooltip(target);
        }, 500);
    });
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
    if (e.target == worldMenu || !worldMenu.contains(e.target)) {
        toggleActive(e.target);
    }
});

// worldmenu - 모달 크기 조절
const world = document.querySelector('.world');
const modals = document.querySelectorAll('.controller-modal');

const resizeModal = (target, ratio) => {
    const targetWidth = target.clientWidth;
    const resizedWidth = targetWidth * ratio;

    target.style.maxWidth = `${resizedWidth}px`;
};

const resizeIfHidden = (targetModal) => {
    const modalRect = targetModal.getBoundingClientRect();
    const containerRect = world.getBoundingClientRect();

    const isPartiallyHiddenOrFullyHidden =
        modalRect.right >= containerRect.right;

    if (isPartiallyHiddenOrFullyHidden) {
        const term = modalRect.right - containerRect.right;
        const visibleRatio = 1 - term / modalRect.width;
        resizeModal(targetModal, visibleRatio);
    } else {
        targetModal.style.maxWidth = '700px';
    }
};

const resizeObserver = new ResizeObserver(() => {
    const activeButton = world.querySelector('.active');
    if (activeButton) {
        const targetModal = activeButton
            .closest('li')
            .querySelector('.controller-modal');

        resizeIfHidden(targetModal);
    }
});

const observerCallback = (entries, observer) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            const intersectionRatio = entry.intersectionRatio;
            if (intersectionRatio < 1) {
                resizeModal(entry.target, intersectionRatio);
            }
        } else {
            entry.target.style.maxWidth = '700px';
        }
    });
};

const modalIntersectionObserver = new IntersectionObserver(observerCallback, {
    root: null,
    rootMargin: '0px',
    threshold: 0.1,
});

modals.forEach((modal) => {
    modalIntersectionObserver.observe(modal);
});

resizeObserver.observe(world);
resizeObserver.observe(window.document.body);


const addCodeNextCellFromSelectCell = (target) => {
    const selectCell = target.target.parentNode;
    const nextCell = selectCell.nextElementSibling;
    const newCell = document.createElement('py-repl');
    newCell.innerHTML = ``;
    selectCell.parentNode.insertBefore(newCell, nextCell);
};

const downloadCode = (target) => {
    const pyRepl = target.target.closest('py-repl');
    const code= pyRepl.querySelector('.cm-content').innerText;
    const blob = new Blob([code], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `code_${dateFormat()}.py`;
    link.click();
};
const uploadCode = (target) => {
    const pyRepl = target.target.closest('py-repl');
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.py';
    input.onchange = (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = (e) => {
            pyRepl.querySelector('.cm-content').innerText = e.target.result;
        };
        reader.readAsText(file);
    };
    input.click();
};
const deleteCode = (target) => {
    const pyRepl = target.target.closest('py-repl');
    const nextpyReplBtnWrapFromPyRepl = pyRepl.nextElementSibling;
    nextpyReplBtnWrapFromPyRepl.remove();
    pyRepl.remove();
};
