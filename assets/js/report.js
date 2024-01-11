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
        if (trimedCode) {
            codeText += '```py\n' + trimedCode + '\n```\n';
        }
    });
    return codeText ? codeText : '```py\n\n```';
};

const getChart = (chartData) => {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        canvas.setAttribute('id', 'chart');
        const ctx = canvas.getContext('2d');
        ctx.canvas.width = 800;

        const myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(chartData),
                datasets: [
                    {
                        label: '점수',
                        data: Object.values(chartData),
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        min: 0,
                        max: 100,
                    },
                },
                responsive: false,
            },
        });

        setTimeout(() => {
            const imgLink = canvas.toDataURL('image/png');
            canvas.remove();
            resolve(imgLink);
        }, 500);
        document.body.appendChild(canvas);
    });
};

const getTable = (chartData) => {
    return new Promise((resolve) => {
        let result = '|항목|진행도|점수|\n|:---:|:---|:---:|\n';
        for (const key of Object.keys(chartData)) {
            result += `|${key} |${
                '◼︎'.repeat(chartData[key] / 10) +
                '◻︎'.repeat(10 - chartData[key] / 10)
            }|${chartData[key]}|\n`;
        }
        return resolve(result);
    });
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
                // evaluation 항목에 따라 점수를 부여한다.
                if (result == 'Y') {
                    for (const key of story['evaluation']) {
                        score[key] += 10;
                    }
                }
                const storyData = `## 문제 ${id}번\n\n* 평가 항목 : ${
                    story['evaluation'] || '-'
                }\n* 제출 시간 : ${
                    localStorage.getItem(`${id}_time`) || '-'
                }\n* 통과 여부 : ${result}\n\n${getCode(id)}\n\n`;

                reportData += storyData;
            }
        });
        'score', score;
        // 표로 가져오기
        getTable(score).then((res) => {
            reportData = `# 학습 보고서\n\n ${res}\n\n` + reportData;

            // TODO: 학번과 이름을 입력받아 파일명을 만들어준다.
            const userName =
                JSON.parse(localStorage.getItem('profile'))?.name || '익명';
            if (!!reportData) {
                const fileName = `보고서`;
                const today = new Date();
                downloadFile({
                    data: reportData,
                    fileName: `${today
                        .toISOString()
                        .slice(2, 10)
                        .replace(/-/g, '')}_${fileName}_${userName}.md`,
                    fileType: 'text/json',
                });
            } else {
                window.alert('다운로드 할 데이터가 없습니다.');
            }
        });
    });
});
