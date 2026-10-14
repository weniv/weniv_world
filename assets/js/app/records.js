// 진행률·학습 보고서·인증서
//
// 단독 사이트(event.js·report.js)와 위니버시티가 함께 씁니다.
// 통과 여부·제출 코드·제출 시각은 부르는 쪽이 넘깁니다(단독 사이트는 이 브라우저 기록, 위니버시티는 계정 기록).

import { asset, store } from './env.js';

// 스토리 목록을 불러오지 못했을 때 쓰는 장 구성
export const DEFAULT_CHAPTERS = {
    입문: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    기초: [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
};

// 학습 보고서의 항목별 만점 (story.json evaluation 항목 수)
const EVALUATION_TOTAL = {
    입문: { '변수와 자료형': 5, 연산: 8, '반복문과 조건문': 3, 함수: 3 },
    기초: {
        '변수와 자료형': 4,
        연산: 4,
        '반복문과 조건문': 1,
        함수: 5,
        클래스: 3,
    },
};

// story.json 목록 → { 장 이름: [스토리 번호] }
export const chaptersOf = (stories) => {
    const chapters = {};
    for (const story of stories || [])
        (chapters[story.chapter] ||= []).push(story.id);
    return Object.keys(chapters).length ? chapters : DEFAULT_CHAPTERS;
};

// 장마다 { chapter, ids, solved, total, done }
export const chapterProgress = (chapters, isSolved) =>
    Object.entries(chapters).map(([chapter, ids]) => {
        const solved = ids.filter((id) => isSolved(id)).length;
        return {
            chapter,
            ids,
            solved,
            total: ids.length,
            done: solved === ids.length,
        };
    });

const pad = (n) => String(n).padStart(2, '0');
export const formatDate = (date = new Date()) =>
    `${date.getFullYear()}.${pad(date.getMonth() + 1)}.${pad(date.getDate())}`;

// ------------------------------------------------------------------
// 이 브라우저에 남은 기록 (단독 사이트, 로그인하지 않은 위니버시티)
export const localRecords = {
    isSolved: (id) => store.get(`${id}_check`) === '정답',
    codes: (id) => {
        const codes = store.getJson(`${id}_code`);
        return Array.isArray(codes) ? codes : null;
    },
    time: (id) => store.get(`${id}_time`),
    certificateDate: (chapter) => store.get(`${chapter}_certif_time`),
    name: () => store.getJson('profile')?.name || '',
};

// ------------------------------------------------------------------
// 학습 보고서 (마크다운). 제출한 적이 있는 스토리만 넣습니다. 넣을 것이 없으면 ''.
const codeBlock = (codes) => {
    const text = (codes || [])
        .map((code) => code.trim())
        .filter(Boolean)
        .map((code) => '```py\n' + code + '\n```\n')
        .join('');
    return text || '```py\n\n```';
};

const scoreTable = (total, score) => {
    let result = '|항목|진행도|성취도|\n|:---:|:---|:---:|\n';
    for (const key of Object.keys(score)) {
        const fulfilled = Math.floor((score[key] / total[key]) * 10);
        const unfulfilled = Math.floor(
            ((total[key] - score[key]) / total[key]) * 10,
        );
        result += `|${key} |${'◼︎'.repeat(fulfilled) + '◻︎'.repeat(unfulfilled)}|${fulfilled * 10}%|\n`;
    }
    return result;
};

export function buildReport({ stories, isSolved, codes, time }) {
    const chapters = chaptersOf(stories);
    let report = '';
    let hasSubmission = false;
    for (const [chapter, ids] of Object.entries(chapters)) {
        const total = EVALUATION_TOTAL[chapter];
        const score = total
            ? Object.fromEntries(Object.keys(total).map((k) => [k, 0]))
            : {};
        let body = '';
        for (const id of ids) {
            const submitted = codes(id);
            const solved = isSolved(id);
            if (!submitted && !solved) continue;
            hasSubmission = true;
            if (solved) {
                const evaluation =
                    stories?.find((story) => story.id === id)?.evaluation || [];
                for (const item of evaluation)
                    if (item in score) score[item] += 1;
            }
            body += `## 문제 ${id}번\n\n* 제출 시간 : ${time(id) || '-'}\n* 통과 여부 : ${solved ? 'Y' : 'N'}\n\n${codeBlock(submitted)}\n\n`;
        }
        report +=
            `# ${chapter} 학습 성취도\n\n ${total ? scoreTable(total, score) : ''}\n\n` +
            body +
            '---\n\n';
    }
    return hasSubmission ? report : '';
}

export const reportFileName = (name, date = new Date()) =>
    `${date.toISOString().slice(2, 10).replace(/-/g, '')}_보고서_${name || '[이름]'}.md`;

// ------------------------------------------------------------------
// 인증서 그림 (PNG data URL)
const loadImage = (src) =>
    new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () =>
            reject(new Error('인증서 그림을 불러오지 못했습니다.'));
        img.src = src;
    });

export async function drawCertificate({ chapter, name, date }) {
    const nameText = name || '-';
    const dateText = date || formatDate();
    try {
        // 글꼴을 글자 구간별로 나눠 받는 사이트(unicode-range)에서도 그릴 글자가 담긴 조각을 받도록 글자를 넘깁니다.
        await Promise.all([
            document.fonts.load('400 74px Pretendard', nameText),
            document.fonts.load('400 36px Pretendard', dateText),
        ]);
    } catch (e) {
        // 글꼴을 못 불러와도 기본 글꼴로 그립니다.
    }
    const img = await loadImage(asset(`img/certif-${chapter}.jpg`));
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);

    // 이름이 비어 있으면 하이픈
    ctx.font = '400 74px Pretendard';
    ctx.fillStyle = '#3a72ff';
    ctx.textAlign = 'center';
    ctx.fillText(nameText, canvas.width / 2, 570);

    ctx.font = '400 36px Pretendard';
    ctx.fillStyle = 'black';
    ctx.fillText(dateText, 1340, 1000);
    return canvas.toDataURL('image/png');
}

// ------------------------------------------------------------------
// 내려받기
export const downloadUrl = (url, fileName) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.click();
};

export const downloadText = (text, fileName, type = 'text/plain') => {
    const url = URL.createObjectURL(new Blob([text], { type }));
    downloadUrl(url, fileName);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
};
