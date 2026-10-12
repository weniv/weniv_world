// 위니브월드가 붙는 곳에 따라 달라지는 값
//
// 단독 사이트(world.weniv.co.kr)·설치판은 기본값 그대로 씁니다.
// 위니버시티(/tools/world)는 앱을 만들기 전에 configure()로 바꿉니다.
//   assetBase      이미지·스토리·파이썬 파일이 있는 곳 (끝에 / )
//   workerUrl      파이썬 Worker 스크립트 주소 (없으면 이 폴더의 py-worker.js)
//   storagePrefix  localStorage 키 앞에 붙일 글자 (같은 사이트의 다른 기능과 키가 겹치지 않게)
//   root           앱 화면이 들어 있는 곳 (document 또는 요소) — 알림·결과 창도 여기에 붙입니다

export const env = {
    assetBase: './assets/',
    workerUrl: null,
    storagePrefix: '',
    root: typeof document === 'undefined' ? null : document,
};

export const configure = (values) => Object.assign(env, values);

// 'img/item/apple.png' → './assets/img/item/apple.png'
export const asset = (path) => `${env.assetBase}${path}`;

// story.json의 './assets/…' 주소를 assetBase 기준으로 바꿉니다.
export const resolveAsset = (url) =>
    String(url).replace(/^(\.\/)?assets\//, env.assetBase);

// 앱 화면을 담은 요소 (document이면 body) — 실행 중 표시(is-busy)·알림창을 붙이는 곳
export const hostElement = () =>
    !env.root || env.root === document ? document.body : env.root;

export const query = (selector) => env.root?.querySelector(selector) ?? null;
export const queryAll = (selector) =>
    env.root ? [...env.root.querySelectorAll(selector)] : [];

// localStorage (쓸 수 없는 환경에서도 오류 없이)
export const store = {
    key: (key) => `${env.storagePrefix}${key}`,
    get(key) {
        try {
            return localStorage.getItem(store.key(key));
        } catch (e) {
            return null;
        }
    },
    set(key, value) {
        try {
            localStorage.setItem(store.key(key), value);
            return true;
        } catch (e) {
            return false;
        }
    },
    remove(key) {
        try {
            localStorage.removeItem(store.key(key));
        } catch (e) {
            /* 무시 */
        }
    },
    getJson(key) {
        try {
            return JSON.parse(store.get(key));
        } catch (e) {
            return null;
        }
    },
};
