"""
스토리 모범 답안 실행기 (tests/story-solutions.test.mjs가 호출합니다)

표준 입력: [{"codes": [...], "state": {...}}, ...]  (state는 JS toTransfer 형식)
표준 출력: 각 작업의 runner.run_all 결과 목록 (JSON)
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "assets", "py"))

import runner  # noqa: E402

jobs = json.loads(sys.stdin.buffer.read().decode("utf-8"))
results = [
    json.loads(runner.run_all(json.dumps(job["codes"]), json.dumps(job["state"])))
    for job in jobs
]
sys.stdout.write(json.dumps(results))
