// 설치판 점검: 앱을 인터넷 없이 띄워 스토리 하나를 풀고, 껐다 켜도 진행 기록이 남는지 본다 (Playwright _electron)
//
//   node scripts/smoke.mjs                         개발 모드 (electron .)
//   node scripts/smoke.mjs --exe "release/win-unpacked/Weniv World.exe"   패키징한 앱
//   --shots <폴더>   화면을 찍어 둔다
//
// 인터넷 없음: Chromium에 닿을 수 없는 프록시(127.0.0.1:9)와 '모든 이름 풀이 실패'를 걸고 띄운다.
// 앱은 인터넷 요청을 앱 안 파일(vendor/)로 돌려주므로 그래도 파이썬·글꼴이 돌아야 한다.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { _electron as electron } from 'playwright';

const desktop = fileURLToPath(new URL('../', import.meta.url));
const args = process.argv.slice(2);
const option = (name) => (args.includes(name) ? args[args.indexOf(name) + 1] : null);
const exe = option('--exe');
const shots = option('--shots');
const userData = fs.mkdtempSync(path.join(os.tmpdir(), 'weniv-world-smoke-'));
const OFFLINE = ['--proxy-server=127.0.0.1:9', '--host-resolver-rules=MAP * ~NOTFOUND'];

const STORY_1 = `def fishing():
    move()
    pick()

repeat(4, fishing)
turn_left()
turn_left()
repeat(4, move)
say('hello, world!')
`;

const results = [];
const check = (name, ok, detail = '') => {
    results.push([name, Boolean(ok)]);
    console.log(`${ok ? 'OK  ' : 'FAIL'} ${name}${!ok && detail ? `  (${detail})` : ''}`);
};

async function launch() {
    const options = exe
        ? { executablePath: path.resolve(desktop, exe), args: OFFLINE }
        : { args: [...OFFLINE, path.resolve(desktop)] };
    const app = await electron.launch({ ...options, env: { ...process.env, WENIV_WORLD_USER_DATA: userData } });
    const page = await app.firstWindow();
    const failed = [];
    page.on('requestfailed', (request) => failed.push(request.url()));
    await page.waitForFunction(
        () => window.__wenivDebug?.engine.status === 'ready' && window.__wenivDebug.stories.stories.length === 22,
        null,
        { timeout: 120000 },
    );
    return { app, page, failed };
}

async function shot(page, name) {
    if (!shots) return;
    fs.mkdirSync(shots, { recursive: true });
    await page.screenshot({ path: path.join(shots, `${name}.png`) });
}

const started = Date.now();
let { app, page, failed } = await launch();
check(`파이썬 준비 (인터넷 없이, ${((Date.now() - started) / 1000).toFixed(1)}초)`, true);
check('앱 주소 weniv-world://app/', page.url().startsWith('weniv-world://app/'), page.url());
check('설치판 표시(data-host=desktop)', (await page.evaluate(() => document.documentElement.dataset.host)) === 'desktop');
check('창 제목 위니브월드', (await page.title()) !== '' && (await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0].getTitle())) === '위니브월드');
const python = await page.evaluate(async () => {
    const d = window.__wenivDebug;
    d.notebook.setCodes(['import sys\nprint(sys.version.split()[0])']);
    d.notebook.run(d.notebook.cells[0]);
    await d.engine.chain;
    d.player.skip();
    await d.player.whenIdle();
    return d.world.state.print_data.at(-1);
});
check('파이썬 3.14 실행', String(python).startsWith('3.14'), python);
await page.evaluate(() => document.fonts.ready);
check('Pretendard 글꼴 (앱 안 파일)', await page.evaluate(() => document.fonts.check('16px Pretendard')));
check('Source Code Pro 글꼴 (앱 안 파일)', await page.evaluate(() => document.fonts.check('500 14px "Source Code Pro"')));
await shot(page, '01-start');

// 스토리 1편 풀기
await page.locator('.btn-story').click();
await page.locator('.story-list > li[data-id="1"] .btn-toggle').click();
await page.waitForFunction(() => window.__wenivDebug.world.story?.index === 1);
await page.evaluate((code) => window.__wenivDebug.notebook.setCodes([code]), STORY_1);
await page.locator('.story-list > li[data-id="1"] .story-title .btn-submit').click();
await page.waitForSelector('.result-dialog', { timeout: 120000 });
check('스토리 1편 제출 통과', await page.evaluate(() => document.querySelector('.result-dialog').classList.contains('passed')));
await shot(page, '02-story1-passed');
await page.locator('.result-dialog button.confirm').click();
check('진행 기록 저장', (await page.evaluate(() => localStorage.getItem('1_check'))) === '정답');

// 바깥 링크는 기본 브라우저로 (실제로 열지 않고 넘긴 주소만 본다)
await app.evaluate(({ shell }) => {
    globalThis.__opened = [];
    shell.openExternal = async (url) => {
        globalThis.__opened.push(url);
    };
});
const windowsBefore = (await app.windows()).length;
await page.evaluate(() => window.open('https://weniv.co.kr/', '_blank'));
await page.waitForTimeout(500);
const opened = await app.evaluate(() => globalThis.__opened);
check('새 창 링크는 기본 브라우저로', opened.includes('https://weniv.co.kr/') && (await app.windows()).length === windowsBefore, JSON.stringify(opened));
check('앱 안 파일 요청은 모두 성공 (바깥 요청만 막힘)', failed.every((url) => !url.startsWith('weniv-world:') && !url.includes('/pyodide/') && !url.includes('pretendard') && !url.includes('sourcecodepro')), failed.join(', '));
console.log(`     막힌 바깥 요청 ${failed.length}개: ${[...new Set(failed.map((u) => new URL(u).host))].join(', ') || '없음'}`);
await app.close();

// 다시 켜기 → 진행 기록이 남아 있어야 한다
({ app, page, failed } = await launch());
check('다시 켜도 1편 통과 기록이 남음', (await page.evaluate(() => localStorage.getItem('1_check'))) === '정답');
await page.locator('.btn-story').click();
check('스토리 목록에 1편 완료 표시', await page.locator('.story-list > li[data-id="1"].submit').count() === 1);
await shot(page, '03-restart');
await app.close();

fs.rmSync(userData, { recursive: true, force: true });
const bad = results.filter(([, ok]) => !ok);
console.log(`\n${results.length - bad.length}/${results.length} 통과`);
assert.equal(bad.length, 0);
