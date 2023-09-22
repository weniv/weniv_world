// 코드 에디터 관련 요소 추가(헤더, 코드 추가 버튼 등)
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
                    <button type='button' class='btn-code-download code-export'>
                        <span class='sr-only'>download code</span>
                    </button>
                </li>
                <li>
                    <button type='button' class='btn-code-upload code-import'>
                        <span class='sr-only'>upload code</span>
                    </button>
                </li>
                <li>
                    <button type='button' class='btn-close code-delete'>
                        <span class='sr-only'>delete code</span>
                    </button>
                </li>
            `;

    let querySelector = button.querySelector('svg');
    if (querySelector) {
        querySelector.remove();
    }
    ul.addEventListener('click', (target) => {
        switch (target.target.className) {
            case 'btn-code-download code-export':
                downloadCode(target);
                break;
            case 'btn-code-upload code-import':
                uploadCode(target);
                break;
            case 'btn-close code-delete':
                // 만약 셀이 하나 밖에 없다면 동작하지 않는다.
                if (document.querySelectorAll('py-repl').length === 1) {
                    alert('셀이 하나 밖에 없는 경우, 코드를 삭제할 수 없습니다.');
                    return;
                }
                deleteCode(target);
                break;
        }
    });
    button.classList.add('btn-play');
    header.append(button, ul);
    editorContainer.appendChild(header);
};

const setAddCodeButton = (targetNode) => {
    const pyRepl =
        targetNode.tagName === 'PY-REPL'
            ? targetNode
            : targetNode.closest('PY-REPL');
    const buttonContainer = document.createElement('div');
    buttonContainer.setAttribute('class', 'py-repl-btn-wrap');
    buttonContainer.innerHTML = `
        <button type='button' class='btn-add-code add-code-next'>
            코드 추가
        </button>
    `;
    // 중간 셀 추가 기능
    buttonContainer.addEventListener('click', (target) => {
        addCodeNextCellFromSelectCell(target);
    });


    pyRepl.after(buttonContainer);
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
                    setAddCodeButton(addedNode);
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
