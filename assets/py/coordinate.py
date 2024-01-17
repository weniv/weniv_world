#-----------------------#
## 전역에서 사용하는 데이터
map_data = {"height": 5, "width": 5}
map_size = 100
border_size = 1
running_speed = 1

character_data = [
    {
        "character": "licat",
        "character_obj": None,
        "x": 0,
        "y": 0,
        "directions": 0,  # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
        "items": {},
    }
]
default_character = "licat" #character_data[0]
mob_data = []

# 맵 전역 아이템 데이터
# (x, y): {item: 'beeper', count: 1}
item_data = {}

wall_data = {"world": {}}

print_data = []
say_data = []

#-----------------------#
## 시스템 기본 데이터
valid_items = ['fish-1','fish-2','fish-3','diamond','apple','goldbar', 'hp-potion','mp-potion']
edible_items = {'hp-potion':{'hp':20},'mp-potion':{'mp':20}}

wall_blocked = ["wall", "fence"]  # 이동 불가한 벽 종류
wall_types = ["wall", "fence", "door"]  # 벽 종류
wall_type = "wall"  # 현재 선택되어 있는 벽 종류

skill_data={
    'claw-yellow':{'mana':10, 'power':10},
    'claw-white':{'mana':10, 'power':10},
    'beam':{'mana':5, 'power':5},
    'explosion':{'mana':20, 'power':20}}

character_info = {
    'licat':{
        'hp':100,
        'mp':100,
        'skill_data':['claw-yellow','claw-white','beam','explosion']
    }
    }

mob_info = {
    'lion':{
        'hp':250,
        'mp':float("inf"),
    },
    'mob1':{
        'hp':50,
        'mp':float("inf"),
    },
    'mob2':{
        'hp':50,
        'mp':float("inf"),
    },
    'mob3':{
        'hp':50,
        'mp':float("inf"),
    },
    'mob4':{
        'hp':50,
        'mp':float("inf"),
    },
    }
    
# 오류 정보
error_message = {'OutOfWorld': '맵을 벗어납니다.',
    'FrontIsNotClear': '캐릭터 이동 경로에 장애물이 있습니다.',
    'InvalidCharacter': '유효한 캐릭터가 아닙니다.',
    'CharacterIsNotExist': '캐릭터가 존재하지 않습니다.', 
    'CharacterIsNotSelected': '캐릭터가 선택되지 않았습니다.', 
    'CharacterIsNotMovable': '캐릭터가 이동 불가합니다.',
    'CharacterIsNotAttackable': '캐릭터를 공격할 수 없습니다.',
    'ItemIsNotExist': '아이템이 존재하지 않습니다.',
    'AnotherItemIsExist': '다른 아이템이 존재합니다.',
    'InvalidItem': '유효한 아이템이 아닙니다.',
    'InedibleItem': '먹을 수 있는 아이템이 아닙니다.',
    'WallIsExist': '벽이 존재합니다.',
    'CannotOpenWall': '문(door)이 아닌 벽은 열 수 없습니다.',
    'ObstacleExist': '다른 캐릭터 또는 몹이 존재합니다.', 
    'MobIsExist': '해당 이름을 갖는 몹이 이미 맵에 존재합니다.',
    'CharacterIsExist': '해당 캐릭터는 이미 맵에 존재합니다.' ,
    'ArgumentsError':'인수 값이 유효하지 않습니다.',
    'NotEnoughMana':'마나가 부족합니다.',
    'InvalidSkill':'유효한 스킬이 아닙니다.',
    'InvalidCharacter':'유효한 캐릭터가 아닙니다.',
    'InvalidMob':'유효한 몹이 아닙니다.',
    'InvalidSyntax':'잘못된 문법을 사용하였습니다.'
    }
#-----------------------#
## 스토리 데이터

story_data = {
    # 1번 스토리
    1: {
        "map_width": 5,
        "map_height": 1,
        "wall": {  # (x, y): 'wall', 'fence', 'door'
        },
        "item": {
            (0, 1): {"item": "fish-1", "count": 1},
            (0, 2): {"item": "fish-1", "count": 1},
            (0, 3): {"item": "fish-1", "count": 1},
            (0, 4): {"item": "fish-1", "count": 1},
        },
    },
    # 2번 스토리
    2: {
        "map_width": 5,
        "map_height": 5,
        "wall": {  # (x, y): 'wall', 'fence', 'door'
            (0.5, 0): "wall",
            (1.5, 2): "wall",
            (2.0, 0.5): "wall",
            (2.0, 1.5): "wall",
            (2.0, 2.5): "door",
            (2.0, 3.5): "wall",
            (2.5, 1): "wall",
            (2.5, 3): "wall",
        },
        "item": {
            (2, 2): {"item": "diamond", "count": 1},
        },
    },
    # 3번 스토리
    3: {
        "map_width": 5,
        "map_height": 5,
        "wall": {  # (x, y): 'wall', 'fence', 'door'
            (0.5, 1): "wall",
            (0.5, 2): "wall",
            (0.5, 3): "wall",
            (1.0, 0.5): "wall",
            (1.0, 3.5): "wall",
            (2.0, 0.5): "wall",
            (2.0, 3.5): "wall",
            (3.0, 0.5): "wall",
            (3.0, 3.5): "wall",
            (3.5, 1): "wall",
            (3.5, 2): "wall",
            (3.5, 3): "wall",
        },
        "item": {
            (0, 1): {"item": "fish-1", "count": 1},
            (0, 3): {"item": "fish-1", "count": 1},
            (2, 4): {"item": "fish-1", "count": 1},
            (4, 1): {"item": "fish-1", "count": 1},
            (4, 0): {"item": "fish-1", "count": 1},
            (2, 0): {"item": "fish-1", "count": 1},
        },
    },
    # 4번 스토리
    4: {
        "map_width": 5,
        "map_height": 1,
        "wall": {  # (x, y): 'wall', 'fence', 'door'
        },
        "item": {
            (0, 1): {"item": "fish-1", "count": 2},
            (0, 2): {"item": "fish-2", "count": 5},
            (0, 3): {"item": "fish-3", "count": 10},
        },
    },
    # 5번 스토리
    5: {
        "map_width": 1,
        "map_height": 1,
        "wall": {  # (x, y): 'wall', 'fence', 'door'
        },
        "item": {},
        "basic_code":"공지문 = '대표 라이캣, 팀장 뮤라, 팀 리더 하티'"
    },
    # 6번 스토리
    6: {
        "map_width": 5,
        "map_height": 1,
        "wall": {  # (x, y): 'wall', 'fence', 'door'
        },
        "item": {
            (0, 0): {"item": "goldbar", "count": 2},
            (0, 1): {"item": "goldbar", "count": 2},
            (0, 2): {"item": "goldbar", "count": 5},
            (0, 3): {"item": "goldbar", "count": 1},
            (0, 4): {"item": "fish-3", "count": 15},
        },
    },
    # 7번 스토리
    7: {
        "map_width": 5,
        "map_height": 2,
        "wall": {  # (x, y): 'wall', 'fence', 'door'
            (0.5, 4): "wall",
            (1.0, 3.5): "door",
        },
        "item": {
            (0, 1): {"item": "fish-1", "count": 12},
            (0, 2): {"item": "goldbar", "count": 15},
        },
    },
    # 8번 스토리
    8: {
        "map_width": 5,
        "map_height": 5,
        "wall": {  # (x, y): 'wall', 'fence', 'door'
            (0.5, 1): "wall",
            (0.5, 2): "wall",
            (0.5, 3): "wall",
            (0.5, 4): "wall",
            (1.5, 1): "wall",
            (1.5, 2): "wall",
            (1.5, 3): "wall",
            (1.5, 4): "wall",
            (2.5, 1): "wall",
            (2.5, 2): "wall",
            (2.5, 3): "wall",
            (2.5, 4): "wall",
            (3.5, 1): "wall",
            (3.5, 2): "wall",
            (3.5, 3): "wall",
            (3.5, 4): "wall",
        },
        "item": {
            (0, 3): {"item": "fish-1", "count": 1},
            (0, 4): {"item": "fish-1", "count": 1},
            (1, 3): {"item": "fish-1", "count": 2},
            (1, 4): {"item": "fish-1", "count": 3},
            (2, 3): {"item": "fish-1", "count": 3},
            (2, 4): {"item": "fish-1", "count": 1},
            (3, 3): {"item": "fish-1", "count": 8},
            (3, 4): {"item": "fish-1", "count": 1},
            (4, 2): {"item": "fish-1", "count": 1},
            (4, 3): {"item": "fish-1", "count": 2},
            (4, 4): {"item": "fish-1", "count": 1},
        },
    },
    # 9번 스토리
    9: {
        "map_width": 5,
        "map_height": 5,
        "wall": {  # (x, y): 'wall', 'fence', 'door'
            (1.0, 0.5): "wall",
            (1.0, 1.5): "wall",
            (1.0, 2.5): "wall",
            (1.0, 3.5): "wall",
            (2.0, 0.5): "wall",
            (2.0, 1.5): "wall",
            (2.0, 2.5): "wall",
            (2.0, 3.5): "wall",
            (3.0, 0.5): "wall",
            (3.0, 1.5): "wall",
            (3.0, 2.5): "wall",
            (3.0, 3.5): "wall",
            (4.0, 0.5): "wall",
            (4.0, 1.5): "wall",
            (4.0, 2.5): "wall",
            (4.0, 3.5): "wall",
        },
        "item": {
            (4, 0): {"item": "fish-1", "count": 1},
            (3, 1): {"item": "fish-1", "count": 3},
            (4, 2): {"item": "fish-1", "count": 1},
            (2, 3): {"item": "fish-1", "count": 5},
            (3, 4): {"item": "fish-1", "count": 7},
        },
    },
    # 10번 스토리
    10: {
        "map_width": 2,
        "map_height": 5,
        "wall": {  # (x, y): 'wall', 'fence', 'door'
            (0.5, 0): "wall",
            (1.5, 1): "wall",
            (2.5, 0): "wall",
            (3.5, 1): "wall",
        },
        "item": {
            (1, 0): {"item": "goldbar", "count": 1},
            (1, 1): {"item": "fish-2", "count": 1},
            (2, 0): {"item": "goldbar", "count": 1},
            (2, 1): {"item": "fish-3", "count": 1},
            (3, 0): {"item": "goldbar", "count": 1},
            (3, 1): {"item": "fish-1", "count": 1},
            (4, 0): {"item": "fish-3", "count": 1},
            (4, 1): {"item": "fish-1", "count": 1},
        },
    },
    # 11번 스토리
    11: {
        "map_width": 5,
        "map_height": 5,
        "wall": {  # (x, y): 'wall', 'fence', 'door'
            (0.5, 0): "wall",
            (0.5, 2): "wall",
            (1.5, 1): "wall",
            (1.5, 2): "wall",
            (1.5, 3): "wall",
            (2.5, 0): "wall",
            (2.5, 1): "wall",
            (2.5, 3): "wall",
            (3.5, 1): "wall",
            (3.5, 3): "wall",
            (4.0, 0.5): "wall",
            (4.0, 2.5): "wall",
        },
        "item": {
            (0, 1): {"item": "diamond", "count": 1},
            (1, 0): {"item": "diamond", "count": 2},
            (1, 1): {"item": "diamond", "count": 3},
            (2, 0): {"item": "diamond", "count": 3},
            (2, 1): {"item": "diamond", "count": 1},
            (3, 4): {"item": "diamond", "count": 1},
            (4, 2): {"item": "diamond", "count": 1},
            (4, 4): {"item": "goldbar", "count": 1},
        },
    },
}
