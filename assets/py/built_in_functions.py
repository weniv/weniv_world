"""
학습자가 노트북에서 바로 사용할 수 있는 함수 모음

모든 함수는 character 인자를 생략하면 기본 캐릭터(licat)를 움직입니다.
"""

import engine
from actor import DIRECTION_NAME, out_of_world
from character import Character
from mob import Mob
from item import place_item
from coordinate import (
    character_data,
    map_data,
    mob_data,
    item_data,
    valid_items,
    mob_info,
    character_info,
    default_character,
    say_data,
)
from error import (
    CharacterIsNotExist,
    ArgumentsError,
    OutOfWorld,
    InvalidItem,
    InvalidMob,
    InvalidCharacter,
    ObstacleExist,
    MobIsExist,
    CharacterIsExist,
)


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _main_character(character=None):
    """character 인자가 없으면 기본 캐릭터를 돌려줍니다."""
    if character is not None:
        return character
    if not character_data:
        raise CharacterIsNotExist()
    c = character_data[0]
    obj = c.get("character_obj")
    if not isinstance(obj, Character):
        obj = Character(c.get("character"))
        c["character_obj"] = obj
    return obj


# mission_start() / mission_end()는 아무 동작도 하지 않습니다.
# 화면(함수 리스트, 기본 코드, 스토리)에서는 뺐지만, 교안과 이전에 저장한 코드에
# 호출이 남아 있어 오류가 나지 않도록 함수는 남겨 둡니다.
def mission_start():
    """미션 시작 (호출하지 않아도 됩니다)"""


def mission_end():
    """미션 끝 (호출하지 않아도 됩니다)"""


def say(text="", character=None, speech_time=5000):
    """
    캐릭터의 말풍선에 출력
    """
    _main_character(character).say(text, speech_time)


def directions(character=None):
    """
    캐릭터의 방향을 right, top, left, bottom으로 반환
    """
    return DIRECTION_NAME[_main_character(character).directions]


def item(character=None):
    """
    캐릭터가 가지고 있는 아이템을 반환
    """
    return _main_character(character).items


def set_item(x, y, name, count=1, description=None, character=None):
    """
    맵의 (x, y) 칸에 아이템을 count개 놓습니다.
    같은 아이템이 있으면 개수를 더하고, 다른 아이템이 있으면 바꿉니다.
    """
    if not (_is_int(x) and _is_int(y)) or not _is_int(count) or count < 1:
        raise ArgumentsError()
    if out_of_world(x, y):
        raise OutOfWorld()
    if name not in valid_items:
        raise InvalidItem()
    place_item(x, y, name, count, event="set_item")


def move(character=None):
    """
    캐릭터가 바라보는 방향으로 한 칸 이동
    """
    _main_character(character).move()


def turn_left(character=None):
    """
    왼쪽(반시계 방향)으로 회전
    """
    _main_character(character).turn_left()


def pick(character=None):
    """
    발 아래 아이템을 하나 획득
    """
    _main_character(character).pick()


def put(item_name, character=None):
    """
    가지고 있는 아이템을 발 아래에 하나 내려놓음
    """
    _main_character(character).put(item_name)


def repeat(count, f):
    """
    함수 f를 count번 반복합니다. repeat(2, move)
    """
    if _is_int(count) and callable(f):
        times, func = count, f
    elif _is_int(f) and callable(count):
        times, func = f, count
    else:
        raise ArgumentsError()
    for _ in range(times):
        func()


def front_is_clear(character=None):
    return _main_character(character).front_is_clear()


def left_is_clear(character=None):
    return _main_character(character).left_is_clear()


def right_is_clear(character=None):
    return _main_character(character).right_is_clear()


def back_is_clear(character=None):
    return _main_character(character).back_is_clear()


def attack(skill="claw-yellow", character=None):
    """
    스킬을 이용하여 앞에 있는 몬스터를 공격
    """
    _main_character(character).attack(skill)


def open_door(character=None):
    """
    바라보는 방향의 문(door)을 엶
    """
    _main_character(character).open_door()


def typeof_wall(character=None):
    """
    바라보는 방향의 벽 종류를 반환
    """
    return _main_character(character).typeof_wall()


def on_item(character=None):
    """
    발 아래 아이템이 있는지 확인
    """
    c = _main_character(character)
    return (c.x, c.y) in item_data


def eat(item, character=None):
    """
    hp, mp 포션을 먹어 체력과 마나를 회복
    """
    _main_character(character).eat(item)


def mob_exist(x, y):
    return any(m.get("x") == x and m.get("y") == y for m in mob_data)


def character_exist(x, y):
    return any(c.get("x") == x and c.get("y") == y for c in character_data)


def show_modal_alert(message, type="error"):
    """
    화면에 알림창을 띄웁니다.
    """
    engine.emit("alert", message=str(message), level=type)


def add_mob(x, y, mob_type, name, directions=0):
    """
    몬스터를 추가하고 Mob 객체를 반환합니다.
        leo = add_mob(2, 2, 'lion', 'leo')
        leo.move()
    """
    if not (_is_int(x) and _is_int(y)) or not name or not _is_int(directions):
        raise ArgumentsError()
    if out_of_world(x, y):
        raise OutOfWorld()
    if mob_type not in mob_info:
        raise InvalidMob()
    if character_exist(x, y) or mob_exist(x, y):
        raise ObstacleExist()
    name = str(name)
    if any(m.get("name") == name for m in mob_data):
        raise MobIsExist()

    mob = Mob(name)
    data = {
        "name": name,
        "mob": mob_type,
        "mob_obj": mob,
        "x": x,
        "y": y,
        "directions": directions % 4,
        "hp": mob_info[mob_type]["hp"],
    }
    mob_data.append(data)
    engine.emit("add", who=mob._who(), data=_public(data))
    return mob


def add_ch(x, y, name):
    """
    캐릭터를 추가하고 Character 객체를 반환합니다.
    """
    if not (_is_int(x) and _is_int(y)):
        raise ArgumentsError()
    if name not in character_info:
        raise InvalidCharacter()
    if out_of_world(x, y):
        raise OutOfWorld()
    if character_exist(x, y) or mob_exist(x, y):
        raise ObstacleExist()
    if any(c.get("character") == name for c in character_data):
        raise CharacterIsExist()

    char = Character(name)
    data = {
        "character": name,
        "character_obj": char,
        "x": x,
        "y": y,
        "directions": 0,
        "items": {},
        "hp": character_info[name]["hp"],
        "mp": character_info[name]["mp"],
    }
    if name == default_character:
        character_data.insert(0, data)
    else:
        character_data.append(data)
    engine.emit("add", who=char._who(), data=_public(data))
    return char


def _public(data):
    """화면으로 보낼 수 있도록 객체 참조를 뺀 사본"""
    return {k: v for k, v in data.items() if not k.endswith("_obj")}
