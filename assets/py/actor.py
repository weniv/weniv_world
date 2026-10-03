"""
캐릭터(Character)와 몹(Mob)이 함께 쓰는 이동/회전/판정 로직

Actor 객체는 이름만 기억하는 '손잡이(handle)'입니다. 위치, 방향, 체력 같은 값은
항상 character_data / mob_data에서 읽고 씁니다. 그래서 월드를 초기화하거나
화면에서 몹을 지워도 오래된 값이 남지 않습니다.
"""

import engine
from coordinate import character_data, mob_data, map_data, wall_data, wall_blocked, skill_data, say_data
from error import (
    OutOfWorld,
    WallIsExist,
    ObstacleExist,
    InvalidSkill,
)

# 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
DIRECTION_DELTA = {0: (0, 1), 1: (-1, 0), 2: (0, -1), 3: (1, 0)}
DIRECTION_NAME = {0: "right", 1: "top", 2: "left", 3: "bottom"}


def out_of_world(x, y):
    return not (0 <= x < map_data["height"] and 0 <= y < map_data["width"])


def wall_position(x, y, nx, ny):
    """두 칸 사이에 있는 벽의 좌표"""
    return ((x + nx) / 2, (y + ny) / 2)


def wall_between(x, y, nx, ny):
    return wall_data["world"].get(wall_position(x, y, nx, ny))


def obstacle_at(x, y):
    for obj in list(character_data) + list(mob_data):
        if isinstance(obj, dict) and obj.get("x") == x and obj.get("y") == y:
            return True
    return False


class Actor:
    kind = ""
    not_exist_error = Exception

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<{type(self).__name__} {self.name!r}>"

    # ------------------------------------------------------------------
    # 데이터 접근
    def _data_list(self):
        raise NotImplementedError

    def _name_key(self):
        raise NotImplementedError

    def _data(self):
        for d in self._data_list():
            if isinstance(d, dict) and d.get(self._name_key()) == self.name:
                return d
        raise self.not_exist_error()

    def _who(self):
        return {"kind": self.kind, "name": self.name}

    @property
    def x(self):
        return self._data()["x"]

    @property
    def y(self):
        return self._data()["y"]

    @property
    def directions(self):
        return self._data()["directions"]

    @property
    def hp(self):
        return self._data().get("hp")

    def _front(self, offset=0):
        d = self._data()
        direction = (d["directions"] + offset) % 4
        dx, dy = DIRECTION_DELTA[direction]
        return d["x"], d["y"], d["x"] + dx, d["y"] + dy

    # ------------------------------------------------------------------
    # 동작
    def move(self):
        d = self._data()
        x, y, nx, ny = self._front()
        if out_of_world(nx, ny):
            raise OutOfWorld()
        if wall_between(x, y, nx, ny) in wall_blocked + ["door"]:
            raise WallIsExist()
        if obstacle_at(nx, ny):
            raise ObstacleExist()

        engine.emit("move", who=self._who(), frm=[x, y], to=[nx, ny], dir=d["directions"])
        d["x"], d["y"] = nx, ny

    def turn_left(self):
        d = self._data()
        direction = (d["directions"] + 1) % 4
        engine.emit("turn", who=self._who(), dir=direction)
        d["directions"] = direction

    def _is_clear(self, offset=0):
        x, y, nx, ny = self._front(offset)
        if out_of_world(nx, ny):
            return False
        if wall_between(x, y, nx, ny):
            return False
        if obstacle_at(nx, ny):
            return False
        return True

    def front_is_clear(self):
        """바라보는 방향의 앞이 비어 있는지 확인"""
        return self._is_clear(0)

    def left_is_clear(self):
        """바라보는 방향의 왼쪽이 비어 있는지 확인"""
        return self._is_clear(1)

    def back_is_clear(self):
        """바라보는 방향의 뒤가 비어 있는지 확인"""
        return self._is_clear(2)

    def right_is_clear(self):
        """바라보는 방향의 오른쪽이 비어 있는지 확인"""
        return self._is_clear(3)

    def typeof_wall(self):
        """
        바라보는 방향의 벽 종류('wall', 'fence', 'door')를 반환합니다.
        벽이 없으면 None, 앞이 맵 밖이면 'OutOfWorld'를 반환합니다.
        """
        x, y, nx, ny = self._front()
        if out_of_world(nx, ny):
            return "OutOfWorld"
        return wall_between(x, y, nx, ny)

    def _attack_target(self, skill):
        """공격 대상 칸을 계산하고 공통 조건을 확인합니다."""
        if skill not in skill_data:
            raise InvalidSkill()
        x, y, nx, ny = self._front()
        if out_of_world(nx, ny):
            raise OutOfWorld()
        if wall_between(x, y, nx, ny):
            raise WallIsExist()
        return x, y, nx, ny

    def say(self, text="", speech_time=5000):
        text = str(text)
        say_data.append(text)
        engine.emit("say", who=self._who(), text=text, time=speech_time)

    # 이전 버전과의 호환을 위한 메서드
    def _get_character_data(self, key):
        return self._data().get(key)

    def _set_character_data(self, key, value):
        self._data()[key] = value
