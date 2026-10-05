"""
실행 중 발생한 일을 '이벤트'로 기록합니다.

파이썬 코드는 Web Worker 안에서 즉시 끝까지 실행되고, 화면(JS)은 기록된 이벤트를
순서대로 재생하며 애니메이션을 보여 줍니다. 그래서 파이썬 쪽 상태(위치, 아이템 등)는
항상 바로 갱신되고, 애니메이션만 속도 설정에 따라 나중에 보입니다.
"""

from error import TooManyActions

# 한 번 실행에서 허용하는 최대 이벤트 수 (무한 반복으로 브라우저가 멈추는 것을 막습니다)
MAX_EVENTS = 10000

# 한 번 실행에서 허용하는 월드 함수 호출 수
# 벽에 막혀 실패한 move()나 front_is_clear() 같은 확인 함수는 이벤트를 남기지 않으므로 따로 셉니다.
# (예: while True: try: move() except Exception: pass)
MAX_CALLS = 100000

events = []
calls = 0


def reset():
    global calls
    events.clear()
    calls = 0


def tick():
    """월드 함수가 호출될 때마다 셉니다."""
    global calls
    calls += 1
    if calls > MAX_CALLS:
        raise TooManyActions()


def emit(t, **data):
    if len(events) >= MAX_EVENTS:
        raise TooManyActions()
    data["t"] = t
    events.append(data)
