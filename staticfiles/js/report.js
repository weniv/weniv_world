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

// const getChart = (chartData) => {
//     return new Promise((resolve) => {
//         const canvas = document.createElement('canvas');
//         canvas.setAttribute('id', 'chart');
//         const ctx = canvas.getContext('2d');
//         ctx.canvas.width = 800;

//         const myChart = new Chart(ctx, {
//             type: 'bar',
//             data: {
//                 labels: Object.keys(chartData),
//                 datasets: [
//                     {
//                         label: '점수',
//                         data: Object.values(chartData),
//                         borderWidth: 1,
//                     },
//                 ],
//             },
//             options: {
//                 scales: {
//                     y: {
//                         beginAtZero: true,
//                         min: 0,
//                         max: 100,
//                     },
//                 },
//                 responsive: false,
//             },
//         });

//         setTimeout(() => {
//             const imgLink = canvas.toDataURL('image/png');
//             canvas.remove();
//             resolve(imgLink);
//         }, 500);
//         document.body.appendChild(canvas);
//     });
// };

const getTable = (evalData, chartData) => {
    let result = '|항목|진행도|성취도|\n|:---:|:---|:---:|\n';
    for (const key of Object.keys(chartData)) {
        const fulfilled = Math.floor((chartData[key] / evalData[key]) * 10);
        const unfulfilled = Math.floor(
            ((evalData[key] - chartData[key]) / evalData[key]) * 10,
        );

        result += `|${key} |${
            '◼︎'.repeat(fulfilled) + '◻︎'.repeat(unfulfilled)
        }|${fulfilled * 10}%|\n`;
    }
    return result;
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
        입문: {
            '변수와 자료형': 0,
            연산: 0,
            '반복문과 조건문': 0,
            함수: 0,
        },
        기초: {
            '변수와 자료형': 0,
            연산: 0,
            '반복문과 조건문': 0,
            함수: 0,
            클래스: 0,
        },
    };
    const evaluate_score = {
        입문: {
            '변수와 자료형': 5,
            연산: 8,
            '반복문과 조건문': 3,
            함수: 3,
        },
        기초: {
            '변수와 자료형': 4,
            연산: 4,
            '반복문과 조건문': 1,
            함수: 5,
            클래스: 3,
        },
    };

    const questionData = fetchQuestionInfo();
    questionData.then((data) => {
        let reportData = '';
        Object.keys(storyChapter).forEach((chap) => {
            let chapterData = '';
            const storyList = storyChapter[chap];
            // storyList를 순회
            storyList.forEach((id) => {
                if (localStorage.getItem(`${id}_code`)) {
                    const result =
                        localStorage.getItem(`${id}_check`) === '정답'
                            ? 'Y'
                            : 'N';
                    if (result == 'Y') {
                        const evaluation = data.find(
                            (el) => el.id === id,
                        ).evaluation;
                        for (const evl of evaluation) {
                            score[chap][evl] += 1;
                        }
                    }
                    const storyData = `## 문제 ${id}번\n\n* 제출 시간 : ${
                        localStorage.getItem(`${id}_time`) || '-'
                    }\n* 통과 여부 : ${result}\n\n${getCode(id)}\n\n`;

                    chapterData += storyData;
                }
            });

            // 표로 가져오기
            reportData +=
                `# ${chap} 학습 성취도\n\n ${getTable(
                    evaluate_score[chap],
                    score[chap],
                )}\n\n` +
                chapterData +
                '---\n\n';
        });

        // TODO: 학번과 이름을 입력받아 파일명을 만들어준다.
        const userName =
            JSON.parse(localStorage.getItem('profile'))?.name || '[이름]';
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
