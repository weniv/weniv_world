const btnDownload = document.querySelector('.btn-report');

const fetchQuestionInfo = async () => {
    const response = await fetch(
        `${window.location.origin}/assets/data/story/story.json`,
    );
    const jsonData = await response.json();
    return jsonData;
};

const getCode = (id) => {
    const codes = JSON.parse(localStorage.getItem(`${id}_code`));
    let codeText = '';
    // code를 순회하면서 요소를 추가
    codes.forEach((code) => {
        const trimedCode = code.trim();
        console.log('trimedCode', trimedCode);
        if (trimedCode) {
            codeText += '```py\n' + trimedCode + '\n```\n';
        }
    });
    return codeText ? codeText : '```py\n\n```';
};

const submitCheck = () => {
    const score = {
        '변수와 자료형': 0,
        연산: 0,
        '반복문과 조건문': 0,
        함수: 0,
        클래스: 0,
    };
    let reportData = '';
    const questionData = fetchQuestionInfo();
    questionData.then((data) => {
        data.forEach((story) => {
            id = story['id'];
            if (localStorage.getItem(`${id}_code`)) {
                console.log(
                    'result',
                    localStorage.getItem(`${id}_check`) == '정답' ? 'Y' : 'N',
                );
                const result =
                    localStorage.getItem(`${id}_check`) == '정답' ? 'Y' : 'N';

                const storyData = `# 문제 ${id}번\n\n* 목표 : ${
                    story['goals'] || '-'
                }\n* 평가 항목 : ${
                    story['evaluation'] || '-'
                }\n* 통과 여부 : ${result}\n\n${getCode(id)}\n\n`;

                reportData += storyData;
            }
        });
    });
    return reportData;
};

const downloadFile = async ({ data, fileName, fileType }) => {
    const blob = new Blob([data], { type: fileType });
    const link = document.createElement('a');

    link.download = fileName;
    link.href = await URL.createObjectURL(blob);

    const clickEvt = new MouseEvent('click', {
        view: window,
        bubbles: true,
        cancelable: true,
    });
    link.dispatchEvent(clickEvt);
    link.remove();
};

btnDownload.addEventListener('click', (e) => {
    const score = {
        '변수와 자료형': 0,
        연산: 0,
        '반복문과 조건문': 0,
        함수: 0,
        클래스: 0,
    };
    let reportData = '';
    const questionData = fetchQuestionInfo();
    questionData.then((data) => {
        data.forEach((story) => {
            id = story['id'];
            if (localStorage.getItem(`${id}_code`)) {
                const result =
                    localStorage.getItem(`${id}_check`) === '정답' ? 'Y' : 'N';

                const storyData = `# 문제 ${id}번\n\n* 목표 : ${
                    story['goals'] || '-'
                }\n* 평가 항목 : ${
                    story['evaluation'] || '-'
                }\n* 통과 여부 : ${result}\n\n${getCode(id)}\n\n`;

                reportData += storyData;
            }
        });

        // TODO: 학번과 이름을 입력받아 파일명을 만들어준다.
        if (!!reportData) {
            const name = `보고서`;
            const today = new Date();
            downloadFile({
                data: reportData,
                fileName: `${today
                    .toISOString()
                    .slice(2, 10)
                    .replace(/-/g, '')}_${name}_.md`,
                fileType: 'text/json',
            });
        } else {
            window.alert('다운로드 할 데이터가 없습니다.');
        }
    });
});
