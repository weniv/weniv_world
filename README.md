# weniv_world

* 실행 URL : https://weniv.github.io/weniv_world/
* 위니브 월드 레파지토리가 2개 있습니다. 스터디인 프로젝트가 이전 이름이 위니브 월드입니다. 이 프로젝트는 Python과 JavaScript를 실행하게 하는 교육용 서비스 제작 repo입니다.(우선
  Python으로만 진행됩니다.)
* 2023년 9월 30일 2D 베타버전 W1 출시
    * 벽 구현(경현)
    * UI 구현(유진)
    * 아이템:(경림, 승주)
        * fish 4개
        * apple
        * gold
        * dia(diamond)
    * 기본 스토리 제공(호준)
        * 캐릭터 스토리 여기서 모두 소화
        * 탄탄한 세계관 구성 필요
    * 배포 코드 난독화
* 2023년 12월 30일 2D 베타버전 W2 출시
    * licat외 추가 캐릭터 구현
    * 몹 구현
    * 마나 구현, 스킬 구현
    * 공격, 체력, 아이템 드랍 구현
    * 아이템 중 섭취 가능한 아이템은 섭취할 수 있도록 구현
    * 사용자 스토리 제작 가능 기능 제공
    * 아이템
        * 포션
            * 마나포션
            * 체력포션
* 2023년 3월 30일 3D 베타버전 W3 출시
    * 3D로 별도출시 할지, 2D를 업데이트할지 논의
        * threejs 반영
            * 지도 화면 구성
            * 모델 불러오기
            * 모델 움직이기 (W 점프, E 이동, R 회전)
    * 번역
* 2026년 10월 실행 환경 전면 개편
    * PyScript(2022.12, 지원 종료) → Pyodide 314(Python 3.14)를 Web Worker에서 실행
        * 무한 반복에 빠져도 화면이 멈추지 않고, `중지` 버튼으로 멈출 수 있음
        * 한 번 실행에 동작이 10,000개를 넘으면 `TooManyActions` 오류로 안내
    * 노트북 에디터를 CodeMirror 6으로 교체 (자동 완성, 오류 줄 표시, 자동 저장)
    * `print()`가 파이썬과 똑같이 동작 (`sep`, `end`, 여러 인자 사이 공백)
    * 오류 메시지에 해결 힌트 추가, `input()` 지원
    * 속도 조절: 가장 빠르게 하면 50배속
    * 월드 편집 되돌리기(Ctrl+Z), 단축키 도움말(`?`), 스토리 진행률 표시
    * 스토리 제출: 셀 전체를 처음부터 다시 실행해서 채점하고, 항목별 결과(✓/✗)를 표시
    * `mission_start()` / `mission_end()`는 화면에서 제외 (호출해도 오류 없음)

## 개발

```bash
npm ci
npm start              # 개발 서버 (http://localhost:5501)
npm test               # 파이썬 엔진 + JavaScript 실행 큐 회귀 테스트
npm run test:js        # JavaScript 테스트만 실행 (Node.js 22)
npm run build          # 배포 파일 생성 → dist/
npm run scss           # assets/css/*.scss 수정 시 style.css 자동 빌드
npm run build:vendor   # CodeMirror 번들(assets/vendor/codemirror.js) 다시 만들기
```

빌드 없이 확인할 때는 저장소 루트를 정적 서버로 열면 됩니다. (예: `python -m http.server`)
`main` 브랜치에 푸시하면 GitHub Actions가 테스트 → 빌드 → `weniv_world_production` 배포를 진행합니다.

### 구조

```
노트북 셀 ──실행──▶ 파이썬 워커 (assets/js/app/py-worker.js, Pyodide)
                      │  assets/py/runner.py가 코드를 실행하고
                      │  '이벤트 목록 + 실행 후 월드 상태'를 돌려줌
                      ▼
            재생기 (assets/js/app/player.js) ──▶ 월드 화면 / 터미널 / 셀 결과
```

| 위치 | 역할 |
| --- | --- |
| `assets/js/app/main.js` | 앱 진입점. 구성 요소 연결 |
| `assets/js/app/engine.js`, `py-worker.js` | 파이썬 워커 실행·중지, `input()` 처리 |
| `assets/js/app/player.js` | 이벤트를 속도에 맞춰 재생 |
| `assets/js/app/view.js`, `world-editor.js`, `world.js`, `state.js` | 월드 상태, 그리기, 편집(벽·아이템·몹, 되돌리기) |
| `assets/js/app/notebook.js` | 코드 셀(CodeMirror), 노트북 내보내기/불러오기 |
| `assets/js/app/story.js` | 스토리 목록, 채점 |
| `assets/py/` | 학습자가 쓰는 파이썬 함수와 게임 규칙 (DOM 없음) |
| `assets/data/story/worlds.json` | 스토리별 맵 (벽, 아이템, 몹, 기본 코드) |
| `assets/data/story/solutions.json` | 스토리별 채점 기준 |
| `tests/` | 파이썬 엔진 단위 테스트 |

* 월드 상태는 화면(JS)이 가지고 있다가 실행할 때마다 워커로 보냅니다. 그래서 중지(워커 재시작)해도 월드는 그대로 남습니다.
* 몹 체력처럼 JS와 파이썬 양쪽에 있는 값은 `assets/js/app/config.js`와 `assets/py/coordinate.py`를 함께 고쳐야 합니다.
* 파이썬 파일을 바꿔 배포할 때는 `assets/js/app/config.js`의 `APP_VERSION`을 올려 브라우저 캐시를 갱신합니다.
* `input()`은 입력값을 모아 같은 셀을 다시 실행합니다. 기존 리스트·딕셔너리·집합과 일반 객체 속성은 복구하지만, 파일 쓰기·모듈 내부 상태·제너레이터 소비 같은 부작용은 되돌릴 수 없으므로 입력 전에 사용하지 마세요.
* 브라우저 회귀 테스트: `python -m pip install playwright` 후 Chrome이 설치된 환경에서 `python tests/browser_smoke.py`를 실행합니다. 로컬 서버를 자동으로 띄우며 Pyodide CDN 연결이 필요합니다.

## LICENSE(라이센스)

### 1. Pyodide License

* Pyodide는 Mozilla Public License 2.0을 따릅니다.
* [Pyodide 라이센스](https://github.com/pyodide/pyodide/blob/main/LICENSE)

### 2. CodeMirror License

* CodeMirror 6(`assets/vendor/codemirror.js`)는 MIT License를 따릅니다.
* [CodeMirror 라이센스](https://github.com/codemirror/dev/blob/main/LICENSE)

```
   Copyright (C) 2018-2021 by Marijn Haverbeke <marijn@haverbeke.berlin> and others

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.
```
