# 모범 답안 공통 도우미 (테스트 전용, 채점의 '요구 문법' 검사에는 포함하지 않음)
# 벽을 피해 목표 칸까지 최단 경로로 이동합니다. 문(door)은 열고 지나가고, 몹이 있는 칸은 피합니다.
from collections import deque

_DELTA = {0: (0, 1), 1: (-1, 0), 2: (0, -1), 3: (1, 0)}


def _me():
    return character_data[0]


def goto(tx, ty):
    me = _me()
    start = (me['x'], me['y'])
    prev = {start: None}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        if (x, y) == (tx, ty):
            break
        for dx, dy in _DELTA.values():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < map_data['height'] and 0 <= ny < map_data['width']):
                continue
            if wall_data['world'].get(((x + nx) / 2, (y + ny) / 2)) not in (None, 'door'):
                continue
            if (nx, ny) in prev or any(m['x'] == nx and m['y'] == ny for m in mob_data):
                continue
            prev[(nx, ny)] = (x, y)
            queue.append((nx, ny))
    if (tx, ty) not in prev:
        raise RuntimeError(f'{(tx, ty)}(으)로 갈 수 있는 길이 없습니다.')

    path = []
    cur = (tx, ty)
    while cur != start:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    for nx, ny in path:
        me = _me()
        d = next(k for k, (dx, dy) in _DELTA.items() if (me['x'] + dx, me['y'] + dy) == (nx, ny))
        while _me()['directions'] != d:
            turn_left()
        if typeof_wall() == 'door':
            open_door()
        move()
    return path


def pick_all():
    n = 0
    while on_item():
        pick()
        n += 1
    return n
