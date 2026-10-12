// 스토어 이미지에 쓸 실제 앱 화면을 찍는다 (패키징한 앱, 인터넷 없이, 새 진행 기록으로)
//   node store/capture.mjs ["release/win-unpacked/Weniv World.exe"]   → store/raw/*.png (2배 해상도)
// 스토리 1편은 화면에서 직접 코드를 넣어 실행·제출하고, 진행률·인증서 장면을 위해 입문 2~11편은
// 저장소의 모범 답안(tests/story_solutions)을 실제 채점으로 제출한다.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { _electron as electron } from 'playwright';

const desktop = fileURLToPath(new URL('../', import.meta.url));
const repo = path.resolve(desktop, '..');
const exe = path.resolve(desktop, process.argv[2] || 'release/win-unpacked/Weniv World.exe');
const out = path.join(desktop, 'store/raw');
const userData = fs.mkdtempSync(path.join(os.tmpdir(), 'weniv-world-store-'));
fs.mkdirSync(out, { recursive: true });

const app = await electron.launch({
    executablePath: exe,
    args: ['--force-device-scale-factor=2', '--proxy-server=127.0.0.1:9', '--host-resolver-rules=MAP * ~NOTFOUND'],
    env: { ...process.env, WENIV_WORLD_USER_DATA: userData },
});
const page = await app.firstWindow();
await app.evaluate(({ BrowserWindow }) => {
    const win = BrowserWindow.getAllWindows()[0];
    win.setContentSize(1680, 1050);
    win.center();
});
await page.waitForFunction(() => window.__wenivDebug?.engine.status === 'ready' && window.__wenivDebug.stories.stories.length === 22, null, { timeout: 120000 });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(800);
const shot = async (name) => {
    await page.evaluate(() => {
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    });
    await page.waitForTimeout(400);
    await page.screenshot({ path: path.join(out, `${name}.png`) });
    console.log(name);
};
const read = (file) => fs.readFileSync(path.join(repo, 'tests/story_solutions', file), 'utf8');
const worlds = JSON.parse(fs.readFileSync(path.join(repo, 'assets/data/story/worlds.json'), 'utf8'));
const prelude = read('_prelude.py');
const answer = (id) => read(`${id}.py`).replace('# {basic_code}', worlds[id]?.basic_code ?? '');

const showStory = (id) =>
    page.evaluate((n) => {
        // 문서 전체가 아니라 스토리 목록만 내린다 (scrollIntoView는 머리 줄까지 밀어 올린다)
        const li = document.querySelector(`.story-list > li[data-id="${n}"]`);
        let box = li.parentElement;
        while (box && box.scrollHeight <= box.clientHeight) box = box.parentElement;
        if (box) box.scrollTop += li.getBoundingClientRect().top - box.getBoundingClientRect().top;
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    }, id);

await shot('01-start');

// 스토리 1편 열기 → 코드 쓰기 → 실행 → 제출
await page.locator('.btn-story').click();
await page.locator('.story-list > li[data-id="1"] .btn-toggle').click();
await page.waitForFunction(() => window.__wenivDebug.world.story?.index === 1);
await showStory(1);
await shot('02-story1-open');

await page.evaluate((code) => window.__wenivDebug.notebook.setCodes([code]), answer(1));
await page.evaluate(() => {
    const slider = document.querySelector('#speed-range');
    slider.value = '80';
    slider.dispatchEvent(new Event('input'));
});
await page.locator('.cell-run-button').first().click();
await page.waitForFunction(() => window.__wenivDebug.player.busy, null, { timeout: 60000 });
await page.waitForTimeout(1600);
await shot('03-running');
await page.waitForFunction(() => !window.__wenivDebug.isBusy(), null, { timeout: 60000 });
await shot('04-ran');

await page.locator('.story-list > li[data-id="1"] .story-title .btn-submit').click();
await page.waitForSelector('.result-dialog.passed', { timeout: 60000 });
await shot('05-passed');
await page.locator('.result-dialog button.confirm').click();

// 입문 2~11편: 모범 답안을 실제로 제출 (인증서 장면)
for (let id = 2; id <= 11; id += 1) {
    await page.locator(`.story-list > li[data-id="${id}"] .btn-toggle`).click();
    await page.waitForFunction((n) => window.__wenivDebug.world.story?.index === n, id);
    await page.evaluate((codes) => window.__wenivDebug.notebook.setCodes(codes), [prelude, answer(id)]);
    await page.locator(`.story-list > li[data-id="${id}"] .story-title .btn-submit`).click();
    await page.waitForSelector('.result-dialog', { timeout: 60000 });
    const passed = await page.evaluate(() => document.querySelector('.result-dialog').classList.contains('passed'));
    if (!passed) throw new Error(`${id}편 통과하지 못함`);
    await page.locator('.result-dialog button.confirm').click();
}

// 12편(기초) 열어 두고 진행률
await page.locator('.story-list > li[data-id="12"] .btn-toggle').click();
await page.waitForFunction(() => window.__wenivDebug.world.story?.index === 12);
await page.evaluate((code) => window.__wenivDebug.notebook.setCodes([code]), worlds[12]?.basic_code ? `${worlds[12].basic_code}\n` : '# 12편\n');
await showStory(12);
await shot('06-progress');

await page.locator('.btn-certif').click();
await shot('07-certif');
await page.mouse.click(800, 700);

await page.locator('.btn-kebab').click();
await shot('08-menu');
await page.mouse.click(800, 700);

await page.locator('.btn-dark-mode').click();
await page.mouse.move(800, 700);
await page.waitForTimeout(600);
await shot('09-dark');

await app.close();
fs.rmSync(userData, { recursive: true, force: true });
