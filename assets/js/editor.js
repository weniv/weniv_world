// 코드 에디터 헤더 등 요소 추가
const notebookSection = document.querySelector('.notebook-section');
const pyReplElement = document.querySelector('py-repl');

const setHeader = (targetNode) => {
    const editorContainer = targetNode.querySelector('.cm-editor');
    const button = targetNode.querySelector('.py-repl-run-button');
    const header = document.createElement('header');
    header.setAttribute('class', 'cm-header');

    const ul = document.createElement('ul');
    ul.setAttribute('class', 'btn-list');
    ul.innerHTML = `
                <li>
                    <button type="button" class="btn-code-export code-export">
                        <span class="sr-only">코드 내보내기</span>
                    </button>
                </li>
                <li>
                    <button type="button" class="btn-code-import code-import">
                        <span class="sr-only">코드 추가하기</span>
                    </button>
                </li>
                <li>
                    <button type="button" class="btn-close code-delete">
                        <span class="sr-only">코드 삭제</span>
                    </button>
                </li>
            `;

    let querySelector = button.querySelector('svg');
    if (querySelector) {
        querySelector.remove();
    }
    button.classList.add('btn-play');
    header.append(button, ul);
    editorContainer.appendChild(header);
};

const observePyRepl = (mutationsList) => {
    mutationsList.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            for (const addedNode of mutation.addedNodes) {
                if (
                    addedNode.tagName === 'PY-REPL' ||
                    addedNode.className.includes('py-repl')
                ) {
                    setHeader(addedNode);
                }
            }
        }
    });
};

const ReplObserver = new MutationObserver(observePyRepl);
ReplObserver.observe(notebookSection, { childList: true });
ReplObserver.observe(pyReplElement, { childList: true });

// 코드 실행결과 인덱스 붙이기, 스크롤 하단으로 내리기
const outputElement = document.querySelector('#output');
const outputResult = document.querySelector('.output-result');

const createIndexList = (target) => {
    const indexList = document.querySelector('.world-output .index-list');
    const outputItems = document.querySelectorAll('.output-item');
    const currentIndex = Array.from(outputItems).indexOf(target);

    indexList.innerHTML = '';

    for (let index in Array.from(outputItems)) {
        const indexItem = document.createElement('li');
        indexItem.innerText = parseInt(index) + 1;

        index == currentIndex && indexItem.setAttribute('class', 'current');

        indexList.append(indexItem);
    }
};

const setCurrentItem = (target) => {
    const outputItems = document.querySelectorAll('.output-item');

    Array.from(outputItems).forEach((item) => {
        item.classList.contains('current') && item.classList.remove('current');
    });

    target.classList.add('current');
};

const scrollToBottom = () => {
    outputResult.scrollTop = outputResult.scrollHeight;
};

const observeOutput = (mutationsList) => {
    mutationsList.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            for (const addedNode of mutation.addedNodes) {
                setCurrentItem(addedNode);
                createIndexList(addedNode);
                scrollToBottom();
            }
        }
    });
};

const outputObserver = new MutationObserver(observeOutput);
outputObserver.observe(outputElement, { childList: true });
