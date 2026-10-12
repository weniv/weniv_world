// 설치 파일을 배포 저장소(weniv/wenote-releases)의 릴리스에 올린다 (위노트 앱들과 같은 방식).
// 태그 weniv-world-v<버전>, 이름 '위니브월드 <버전>', 본문은 release-notes/<버전>.md.
// 스토어 상품은 GitHub 칸(저장소 weniv/wenote-releases, 태그 앞부분 weniv-world-v)으로 이 릴리스를 읽는다.
//
//   node scripts/publish-release.mjs                 release/의 설치 파일(.exe, .dmg)을 올린다
//   node scripts/publish-release.mjs --dir <폴더>     그 폴더(하위 폴더 포함)에서 찾는다 (GitHub Actions)
//   --draft   초안으로 만든다      --replace   같은 이름의 파일이 이미 있으면 바꾼다      --dry-run 올릴 것만 보여 준다
// 토큰: GH_TOKEN 또는 GITHUB_TOKEN (weniv/wenote-releases에 contents 쓰기 권한), 없으면 git credential에 저장된 GitHub 토큰.
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const REPO = process.env.RELEASES_REPO || 'weniv/wenote-releases';
export const TAG_PREFIX = 'weniv-world-v';
const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const version = pkg.version;
const tag = `${TAG_PREFIX}${version}`;
const args = process.argv.slice(2);
const flag = (name) => args.includes(name);
const dirIndex = args.indexOf('--dir');
const dir = dirIndex >= 0 ? path.resolve(args[dirIndex + 1]) : path.join(root, 'release');

/** 올릴 설치 파일 이름인지 (weniv-world-<버전>-windows-x64-setup.exe 등) */
export const isInstaller = (name, wanted = version) =>
    new RegExp(`^weniv-world-${wanted.replace(/\./g, '\.')}-.*\.(exe|dmg)$`, 'i').test(name) && !name.includes('__uninstaller');

const findFiles = (folder) => {
    const found = [];
    const visit = (current) => {
        for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
            const full = path.join(current, entry.name);
            if (entry.isDirectory()) visit(full);
            else if (isInstaller(entry.name)) found.push(full);
        }
    };
    if (fs.existsSync(folder)) visit(folder);
    return found;
};

const token = () => {
    if (process.env.GH_TOKEN || process.env.GITHUB_TOKEN) return process.env.GH_TOKEN || process.env.GITHUB_TOKEN;
    try {
        const out = execFileSync('git', ['credential', 'fill'], { input: 'protocol=https\nhost=github.com\n\n', encoding: 'utf8' });
        return out.match(/^password=(.*)$/m)?.[1] || '';
    } catch {
        return '';
    }
};

let auth = '';
const api = async (url, options = {}) => {
    const response = await fetch(url.startsWith('http') ? url : `https://api.github.com${url}`, {
        ...options,
        headers: { Authorization: `Bearer ${auth}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', ...(options.headers || {}) },
    });
    if (response.status === 404 && options.allow404) return null;
    if (!response.ok) throw new Error(`GitHub ${options.method || 'GET'} ${url} → ${response.status} ${await response.text()}`);
    return response.status === 204 ? null : response.json();
};

const main = async () => {
    const installers = findFiles(dir);
    const notesFile = path.join(root, 'release-notes', `${version}.md`);
    if (!fs.existsSync(notesFile)) throw new Error(`release-notes/${version}.md가 없어요.`);
    const notes = fs.readFileSync(notesFile, 'utf8').trim();
    if (!installers.length) throw new Error(`${dir}에 올릴 설치 파일(weniv-world-${version}-*.exe/.dmg)이 없어요.`);
    const list = installers.map((file) => `- ${path.basename(file)} (${(fs.statSync(file).size / 1024 / 1024).toFixed(1)}MB)`).join('\n');
    console.log(`${REPO} 릴리스 ${tag}\n설치 파일:\n${list}\n\n${notes}\n`);
    if (flag('--dry-run')) return;
    auth = token();
    if (!auth) throw new Error('GitHub 토큰이 없어요. GH_TOKEN을 주세요.');

    let release = await api(`/repos/${REPO}/releases/tags/${tag}`, { allow404: true });
    if (!release) {
        release = await api(`/repos/${REPO}/releases`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tag_name: tag, name: `위니브월드 ${version}`, body: notes, draft: flag('--draft'), prerelease: false }),
        });
        console.log(`릴리스를 만들었어요: ${release.html_url}`);
    }
    for (const file of installers) {
        const name = path.basename(file);
        const existing = release.assets.find((asset) => asset.name === name);
        if (existing) {
            if (!flag('--replace')) {
                console.log(`건너뜀 (이미 있음): ${name}`);
                continue;
            }
            await api(`/repos/${REPO}/releases/assets/${existing.id}`, { method: 'DELETE' });
        }
        const target = release.upload_url.replace(/\{.*\}$/, `?name=${encodeURIComponent(name)}`);
        await api(target, { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: fs.readFileSync(file), duplex: 'half' });
        console.log(`올렸어요: ${name}`);
    }
    console.log(`끝: https://github.com/${REPO}/releases/tag/${tag}`);
};

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
    main().catch((error) => {
        console.error(error.message);
        process.exit(1);
    });
}
