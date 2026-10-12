// 태그로 설치 파일을 만들 때: 태그(weniv-world-v<버전>)·package.json·package-lock·릴리스 노트의 판이 맞는지 확인한다
import fs from 'node:fs';

const pkg = JSON.parse(fs.readFileSync(new URL('../package.json', import.meta.url), 'utf8'));
const lock = JSON.parse(fs.readFileSync(new URL('../package-lock.json', import.meta.url), 'utf8'));
const tag = process.env.RELEASE_TAG || '';
if (lock.version !== pkg.version || lock.packages?.[''].version !== pkg.version) {
    throw new Error('desktop/package.json과 package-lock.json의 버전이 달라요');
}
if (tag && tag !== `weniv-world-v${pkg.version}`) throw new Error(`태그 ${tag}가 weniv-world-v${pkg.version}와 달라요`);
if (tag && !fs.existsSync(new URL(`../release-notes/${pkg.version}.md`, import.meta.url))) {
    throw new Error(`release-notes/${pkg.version}.md가 없어요`);
}
console.log(`버전 확인: ${pkg.version}${tag ? ` (태그 ${tag})` : ''}`);
