// 단독 사이트 프로필 창의 '보고서 다운로드' (이 브라우저에 남은 제출 기록으로 만듭니다)

import { asset } from './app/env.js';
import {
    buildReport,
    downloadText,
    localRecords,
    reportFileName,
} from './app/records.js';
import { toast } from './app/ui.js';

document.querySelector('.btn-report').addEventListener('click', async () => {
    let stories = [];
    try {
        stories = await (await fetch(asset('data/story/story.json'))).json();
    } catch (e) {
        // 스토리 목록 없이 기본 장 구성으로 만듭니다.
    }
    const report = buildReport({
        stories,
        isSolved: localRecords.isSolved,
        codes: localRecords.codes,
        time: localRecords.time,
    });
    if (!report) {
        toast('다운로드 할 데이터가 없습니다.');
        return;
    }
    downloadText(report, reportFileName(localRecords.name()), 'text/markdown');
});
