#-----------------------#
## 전역에서 사용하는 데이터
# 화면(JS)이 실행할 때마다 현재 월드 상태를 보내 주고, runner.load_state()가
# 아래 객체들을 "제자리에서" 갱신합니다. 학습자가 변수를 붙잡고 있어도
# 항상 최신 값을 보도록 객체를 새로 만들지 않습니다.
map_data = {"height": 5, "width": 5}

character_data = [
    {
        "character": "licat",
        "character_obj": None,
        "x": 0,
        "y": 0,
        "directions": 0,  # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
        "items": {},
        "hp": 100,
        "mp": 100,
    }
]
default_character = "licat"
mob_data = []

# 맵 전역 아이템 데이터
# (x, y): {'item': 'fish-1', 'count': 1}
item_data = {}

# 벽 데이터 (x, y): 'wall' | 'fence' | 'door'
# 세로벽은 (정수, n.5), 가로벽은 (n.5, 정수) 좌표를 사용합니다.
wall_data = {"world": {}}

print_data = []
say_data = []

#-----------------------#
## 시스템 기본 데이터
valid_items = ['fish-1', 'fish-2', 'fish-3', 'diamond', 'apple', 'goldbar', 'hp-potion', 'mp-potion']
edible_items = {'hp-potion': {'hp': 20}, 'mp-potion': {'mp': 20}}

wall_blocked = ["wall", "fence"]  # 이동 불가한 벽 종류
wall_types = ["wall", "fence", "door"]  # 벽 종류

skill_data = {
    'claw-yellow': {'mana': 10, 'power': 10},
    'claw-white': {'mana': 10, 'power': 10},
    'beam': {'mana': 5, 'power': 5},
    'explosion': {'mana': 20, 'power': 20},
}

character_info = {
    'licat': {
        'hp': 100,
        'mp': 100,
        'skill_data': ['claw-yellow', 'claw-white', 'beam', 'explosion'],
    }
}

mob_info = {
    'lion': {'hp': 250, 'mp': float("inf")},
    'py': {'hp': 50, 'mp': float("inf")},
    'binky': {'hp': 50, 'mp': float("inf")},
    'gary': {'hp': 50, 'mp': float("inf")},
    'wizard': {'hp': 50, 'mp': float("inf")},
}

# 오류 정보
error_message = {
    'OutOfWorld': '맵을 벗어납니다.',
    'FrontIsNotClear': '캐릭터 이동 경로에 장애물이 있습니다.',
    'InvalidCharacter': '유효한 캐릭터가 아닙니다.',
    'CharacterIsNotExist': '캐릭터가 존재하지 않습니다.',
    'CharacterIsNotSelected': '캐릭터가 선택되지 않았습니다.',
    'CharacterIsNotMovable': '캐릭터가 이동 불가합니다.',
    'CharacterIsNotAttackable': '캐릭터를 공격할 수 없습니다.',
    'CharacterIsDead': '캐릭터의 체력이 0이 되었습니다.',
    'ItemIsNotExist': '아이템이 존재하지 않습니다.',
    'AnotherItemIsExist': '다른 아이템이 존재합니다.',
    'InvalidItem': '유효한 아이템이 아닙니다.',
    'InedibleItem': '먹을 수 있는 아이템이 아닙니다.',
    'WallIsExist': '벽이 존재합니다.',
    'CannotOpenWall': '문(door)이 아닌 벽은 열 수 없습니다.',
    'DoorIsNotExist': '앞에 문(door)이 없습니다.',
    'ObstacleExist': '다른 캐릭터 또는 몹이 존재합니다.',
    'MobIsExist': '해당 이름을 갖는 몹이 이미 맵에 존재합니다.',
    'MobIsNotExist': '몹이 존재하지 않습니다.',
    'CharacterIsExist': '해당 캐릭터는 이미 맵에 존재합니다.',
    'ArgumentsError': '인수 값이 유효하지 않습니다.',
    'NotEnoughMana': '마나가 부족합니다.',
    'InvalidSkill': '유효한 스킬이 아닙니다.',
    'InvalidMob': '유효한 몹이 아닙니다.',
    'InvalidSyntax': '잘못된 문법을 사용하였습니다.',
    'TooManyActions': '명령이 너무 많습니다.',
    'InputNotAllowed': '입력이 취소되었습니다.',
}

# 오류 해결 힌트 (학습자에게 오류 메시지 아래 한 줄로 보여 줍니다)
error_hint = {
    'OutOfWorld': '캐릭터가 바라보는 방향과 위치를 확인하세요. front_is_clear()로 앞이 비었는지 먼저 확인할 수 있습니다.',
    'FrontIsNotClear': 'front_is_clear()로 앞이 비어 있는지 먼저 확인하세요.',
    'InvalidCharacter': '사용할 수 있는 캐릭터 이름은 licat입니다.',
    'CharacterIsNotExist': '월드 초기화 버튼을 눌러 캐릭터를 다시 만드세요.',
    'CharacterIsDead': 'eat("hp-potion")으로 체력을 회복하거나, 월드 초기화 버튼을 눌러 다시 시작하세요.',
    'ItemIsNotExist': 'on_item()으로 발 아래 아이템이 있는지, item()으로 가진 아이템을 확인하세요.',
    'AnotherItemIsExist': '같은 칸에는 한 종류의 아이템만 놓을 수 있습니다. 빈 칸에서 put()을 사용하세요.',
    'InvalidItem': "사용할 수 있는 아이템: 'fish-1', 'fish-2', 'fish-3', 'diamond', 'apple', 'goldbar', 'hp-potion', 'mp-potion'",
    'InedibleItem': "먹을 수 있는 아이템은 'hp-potion', 'mp-potion'입니다.",
    'WallIsExist': '앞에 벽이 있습니다. typeof_wall()로 벽의 종류를 확인하고, 문(door)이라면 open_door()로 열 수 있습니다.',
    'CannotOpenWall': 'open_door()는 문(door)에만 사용할 수 있습니다. typeof_wall()로 확인해 보세요.',
    'DoorIsNotExist': 'typeof_wall()이 "door"를 돌려줄 때 open_door()를 사용하세요.',
    'ObstacleExist': '이동하려는 칸에 다른 캐릭터나 몹이 있습니다. 다른 길로 돌아가거나 attack()으로 공격해 보세요.',
    'MobIsExist': '다른 이름을 사용하세요.',
    'MobIsNotExist': '몹이 이미 쓰러졌거나 삭제되었습니다. mob_data로 현재 몹을 확인하세요.',
    'CharacterIsExist': 'licat은 이미 월드에 있습니다.',
    'ArgumentsError': '함수에 넣은 값의 개수와 종류를 확인하세요. 좌표는 정수로 입력합니다.',
    'NotEnoughMana': "eat('mp-potion')으로 마나를 회복하세요.",
    'InvalidSkill': "사용할 수 있는 스킬: 'claw-yellow', 'claw-white', 'beam', 'explosion'",
    'InvalidMob': "사용할 수 있는 몹: 'lion', 'py', 'binky', 'gary', 'wizard'",
    'TooManyActions': '반복문이 끝나지 않는 것은 아닌지 확인하세요. (한 번 실행에 최대 10,000개 동작)',
}
