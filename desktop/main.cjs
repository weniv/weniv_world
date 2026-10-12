// 위니브월드 설치판 (Electron 메인 프로세스)
//
// - 화면: 빌드한 위니브월드(app/, 사이트와 같은 파일)를 앱 전용 주소 weniv-world://app/ 로 연다.
//   file:// 이 아니라 표준·보안 주소(privileged scheme)라 모듈 Worker(파이썬 실행)·wasm·fetch가 사이트와 똑같이 돈다.
//   주소의 출처가 늘 같아서 진행 기록(localStorage)이 앱을 다시 켜도 남는다(사용자 데이터 폴더).
// - 인터넷 없이: 위니브월드가 인터넷에서 받는 것(Pyodide, 글꼴)은 앱에 넣어 두고(vendor/), 같은 주소로 오는 요청을
//   앱 안 파일로 돌려준다(vendor/offline.json). 그 밖의 인터넷 요청은 보내지 않는다(통계 등).
// - 링크: 새 창으로 여는 링크·바깥 주소는 기본 브라우저로 연다.
'use strict';

const { app, BrowserWindow, Menu, protocol, shell } = require('electron');
const path = require('node:path');
const { appResponse, loadOfflineRoutes, offlineResponse } = require('./protocol.cjs');

const SCHEME = 'weniv-world';
const ORIGIN = `${SCHEME}://app`;
const APP_DIR = path.join(__dirname, 'app');
const VENDOR_DIR = path.join(__dirname, 'vendor');

// 자동 점검(scripts/smoke.mjs)이 진행 기록을 따로 두려고 쓴다
if (process.env.WENIV_WORLD_USER_DATA) app.setPath('userData', process.env.WENIV_WORLD_USER_DATA);

protocol.registerSchemesAsPrivileged([
    {
        scheme: SCHEME,
        privileges: { standard: true, secure: true, supportFetchAPI: true, corsEnabled: true, stream: true, codeCache: true },
    },
]);

// 같은 앱을 두 번 켜면 이미 열린 창을 앞으로 가져온다 (진행 기록을 두 창이 함께 쓰지 않게)
if (!app.requestSingleInstanceLock()) {
    app.quit();
}

function registerProtocols() {
    const routes = loadOfflineRoutes(VENDOR_DIR);
    protocol.handle(SCHEME, (request) => appResponse(APP_DIR, request.url));
    // 인터넷 요청: 앱에 넣어 둔 것만 돌려주고 나머지는 보내지 않는다 (인터넷이 없어도 똑같이 돈다)
    for (const scheme of ['https', 'http']) {
        protocol.handle(scheme, (request) => offlineResponse(VENDOR_DIR, routes, request.url) || Response.error());
    }
}

function isAppUrl(url) {
    return url.startsWith(`${ORIGIN}/`) || url === ORIGIN;
}

function openOutside(url) {
    if (/^(https?:|mailto:)/i.test(url)) shell.openExternal(url).catch(() => {});
}

let mainWindow = null;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1440,
        height: 900,
        minWidth: 1024,
        minHeight: 640,
        title: '위니브월드',
        backgroundColor: '#ffffff',
        icon: path.join(__dirname, 'resources', 'icon.png'),
        show: false,
        webPreferences: {
            contextIsolation: true,
            nodeIntegration: false,
            sandbox: true,
            spellcheck: false,
        },
    });
    mainWindow.once('ready-to-show', () => mainWindow.show());
    // 창 제목은 늘 '위니브월드' (사이트 제목 'Weniv World Beta' 대신)
    mainWindow.on('page-title-updated', (event) => event.preventDefault());

    const { webContents } = mainWindow;
    webContents.setWindowOpenHandler(({ url }) => {
        if (!isAppUrl(url)) openOutside(url);
        return { action: 'deny' };
    });
    webContents.on('will-navigate', (event, url) => {
        if (isAppUrl(url)) return;
        event.preventDefault();
        openOutside(url);
    });

    mainWindow.loadURL(`${ORIGIN}/index.html`);
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.on('second-instance', () => {
    if (!mainWindow) return;
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
});

app.whenReady().then(() => {
    Menu.setApplicationMenu(process.platform === 'darwin' ? Menu.buildFromTemplate(macMenu()) : null);
    registerProtocols();
    createWindow();
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

// Mac은 메뉴 막대가 늘 있으므로 기본 편집(복사·붙여넣기 단축키)과 끝내기만 둔다
function macMenu() {
    return [
        { label: '위니브월드', submenu: [{ role: 'about', label: '위니브월드 정보' }, { type: 'separator' }, { role: 'quit', label: '위니브월드 끝내기' }] },
        {
            label: '편집',
            submenu: [
                { role: 'undo', label: '실행 취소' },
                { role: 'redo', label: '다시 실행' },
                { type: 'separator' },
                { role: 'cut', label: '오려 두기' },
                { role: 'copy', label: '복사' },
                { role: 'paste', label: '붙여넣기' },
                { role: 'selectAll', label: '모두 선택' },
            ],
        },
        { label: '보기', submenu: [{ role: 'resetZoom', label: '실제 크기' }, { role: 'zoomIn', label: '확대' }, { role: 'zoomOut', label: '축소' }, { type: 'separator' }, { role: 'togglefullscreen', label: '전체 화면' }] },
        { role: 'windowMenu', label: '윈도우' },
    ];
}

