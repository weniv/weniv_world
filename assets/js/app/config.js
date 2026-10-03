// 앱 전역 설정

// 배포할 때마다 바꾸면 브라우저가 이전 버전의 파이썬 파일을 캐시에서 쓰지 않습니다.
export const APP_VERSION = '2026.10.04.1';

// Pyodide (Python 3.14) — Web Worker에서 실행합니다.
export const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/';

// 워커가 불러올 파이썬 파일 (assets/py/)
export const PY_FILES = [
    'coordinate.py',
    'error.py',
    'engine.py',
    'actor.py',
    'item.py',
    'character.py',
    'mob.py',
    'built_in_functions.py',
    'modules.py',
    'runner.py',
];

// 맵 한 칸의 간격(px): 칸 100px + 칸 사이 간격 2px
export const CELL = 102;

export const DEFAULT_CHARACTER = 'licat';

// assets/py/coordinate.py 의 character_info / mob_info 와 같은 값이어야 합니다.
export const CHARACTER_INFO = { licat: { hp: 100, mp: 100 } };
export const MOB_INFO = {
    lion: { hp: 250 },
    py: { hp: 50 },
    binky: { hp: 50 },
    gary: { hp: 50 },
    wizard: { hp: 50 },
};

export const MAP_MIN = 3;
export const MAP_MAX = 10;
