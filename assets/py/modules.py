"""
from modules import turn_right 처럼 가져와서 사용하는 확장 함수
"""

import engine
from actor import DIRECTION_DELTA, out_of_world, obstacle_at
from built_in_functions import move, turn_left, front_is_clear, _main_character
from error import OutOfWorld, ObstacleExist, WorldError


def turn_right(character=None):
    """오른쪽으로 회전"""
    turn_left(character)
    turn_left(character)
    turn_left(character)


def turn_around(character=None):
    """뒤로 회전"""
    turn_left(character)
    turn_left(character)


def move_to_wall(character=None):
    """장애물이 있기 전까지 이동"""
    while front_is_clear(character):
        move(character)


def turn_left_until_clear(character=None):
    """앞이 비어 있을 때까지 왼쪽으로 회전"""
    for _ in range(4):
        if front_is_clear(character):
            return
        turn_left(character)
    raise WorldError("사방이 막혀있습니다.")


def jump(character=None):
    """
    바라보는 방향으로 장애물 한 칸을 뛰어넘어 두 칸 이동합니다.
    """
    ch = _main_character(character)
    d = ch._data()
    x, y, direction = d["x"], d["y"], d["directions"]
    dx, dy = DIRECTION_DELTA[direction]
    nx, ny = x + dx * 2, y + dy * 2

    if out_of_world(nx, ny):
        raise OutOfWorld()
    if obstacle_at(nx, ny):
        raise ObstacleExist()

    engine.emit("jump", who=ch._who(), frm=[x, y], to=[nx, ny], dir=direction)
    d["x"], d["y"] = nx, ny
