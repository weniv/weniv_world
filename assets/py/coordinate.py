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
    'py':{
        'hp':50,
        'mp':float("inf"),
    },
    'binky':{
        'hp':50,
        'mp':float("inf"),
    },
    'gary':{
        'hp':50,
        'mp':float("inf"),
    },
    'wizard':{
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
        "wall": {  # (x, y): "wall", 'fence', 'door'
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
        "wall": {  # (x, y): "wall", 'fence', 'door'
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
        "wall": {  # (x, y): "wall", 'fence', 'door'
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
        "wall": {  # (x, y): "wall", 'fence', 'door'
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
        "wall": {  # (x, y): "wall", 'fence', 'door'
        },
        "item": {},
        "basic_code":"공지문 = '대표 라이캣, 팀장 뮤라, 팀 리더 하티'"
    },
    # 6번 스토리
    6: {
        "map_width": 5,
        "map_height": 1,
        "wall": {  # (x, y): "wall", 'fence', 'door'
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
        "wall": {  # (x, y): "wall", 'fence', 'door'
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
        "wall": {  # (x, y): "wall", 'fence', 'door'
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
        "wall": {  # (x, y): "wall", 'fence', 'door'
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
        "wall": {  # (x, y): "wall", 'fence', 'door'
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
        "wall": {  # (x, y): "wall", 'fence', 'door'
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
    # 12번 스토리
    12: {
        "map_width": 5,
        "map_height": 5,
        "wall": {  
            (0.0, 0.5):	"wall",
            (0.0, 2.5):	"wall",
            (1.0, 0.5):	"wall",
            (1.0, 1.5):	"wall",
            (1.0, 2.5):	"wall",
            (1.0, 3.5):	"wall",
            (2.0, 0.5):	"wall",
            (2.0, 1.5):	"wall",
            (2.0, 2.5):	"wall",
            (2.0, 3.5):	"wall",
            (3.0, 0.5):	"wall",
            (3.0, 1.5):	"wall",
            (3.0, 2.5):	"wall",
            (3.0, 3.5):	"wall",
            (4.0, 1.5):	"wall",
            (4.0, 3.5):	"wall"
        },
        "item": {
                (1, 0): { "item": "fish-2", "count": 1 },
                (3, 1): { "item": "fish-2", "count": 1 },
                (2, 4): { "item": "fish-2", "count": 1 },
                (4, 0): { "item": "hp-potion", "count": 1 },
                (1, 3): { "item": "hp-potion", "count": 1 },
                (0, 3): { "item": "diamond", "count": 1 },
                (2, 2): { "item": "diamond", "count": 1 },
                (3, 4): { "item": "fish-3", "count": 1 },
                (4, 4): { "item": "goldbar", "count": 1 },
                (2, 1): { "item": "goldbar", "count": 1 },
                (5, 0): { "item": "fish-3", "count": 3 }
        },
    },
    13: {
        "map_width": 1,
        "map_height": 1,
        "wall": {  # (x, y): "wall", 'fence', 'door'
        },
        "item": {
        },
        "basic_code":'''
        s = [
            '   + -- + - + -   ',
            '   + --- + - +   ',
            '   + -- + - + -   ',
            '   + - + - + - +   '
        ]
        '''
    },
    14: {
        "map_width": 1,
        "map_height": 1,
        "wall": {  # (x, y): "wall", 'fence', 'door'
        },
        "item": {
        },
        "basic_code":'''
        # 튜플로 구성된 동료 정보
        crew_info = [
            ('자바독', 95, 'Python이 궁금한 평생 JAVA만 해온 JAVA독. Python을 무기로 가지고 있는 라이캣이 동료가 되라는 말에 호기심을 느껴 작은 시험을 냈고 라이캣이 지혜를 발휘하여 문제를 풀자 라이캣의 동료가 됨. Python으로 여러가지를 해보고자 함.'),
            ('개리', 85, '알고리즘 보물을 찾으러가는 배에서 만난 개리. 남는 자리에 누가 앉을 것인지에 대해 논의하던 중 페이지 교체 알고리즘으로 약자를 배려하는 아이디어를 낸 라이캣에 감복하여 동료가 되었음.'),
            ('소울곰', 1, '파이와 썬의 심복인 소울곰. NPC로 무한 동력으로 움직이는 특징을 가지고 있다. 성산일출봉에서 파이와 썬의 마지막 관문을 지키는 지킴이. 카페 주인으로 위장하고 있으나 단번에 NPC인 것을 알아봄.')
        ]
        '''
    },
    15: {
        "map_width": 5,
        "map_height": 5,
        "wall": { 
            (0.5, 0.0): "wall",
            (0.5, 2.0): "wall",
            (1.0, 0.5): "wall",
            (1.0, 1.5): "wall",
            (1.0, 3.5): "wall",
            (1.5, 0.0): "wall",
            (1.5, 3.0): "wall",
            (1.5, 4.0): "wall",
            (2.0, 1.5): "wall",
            (2.0, 3.5): "wall",
            (2.5, 2.0): "wall",
            (2.5, 3.0): "wall",
            (3.0, 0.5): "wall",
            (3.5, 0.0): "wall",
            (3.5, 2.0): "wall",
            (3.5, 3.0): "wall",
            (4.0, 1.5): "wall",
            (4.0, 3.5): "wall"
        },
        "item": {
            (1, 1): { "item": "hp-potion", "count": 4 },
            (0, 2): { "item": "hp-potion", "count": 3 },
            (1, 3): { "item": "hp-potion", "count": 2 },
            (0, 4): { "item": "hp-potion", "count": 1 },
            (2, 0): { "item": "hp-potion", "count": 4 },
            (3, 1): { "item": "hp-potion", "count": 6 },
            (3, 0): { "item": "mp-potion", "count": 3 },
            (4, 1): { "item": "hp-potion", "count": 4 },
            (3, 2): { "item": "hp-potion", "count": 7 },
            (2, 4): { "item": "hp-potion", "count": 5 },
            (4, 4): { "item": "hp-potion", "count": 4 },
            (2, 3): { "item": "mp-potion", "count": 2 },
            (5, 0): { "item": "hp-potion", "count": 9 }
            },
        "basic_code":"# 라이캣이 먹은 포션의 수\npotion_counts = [0, 0, 0, 0]"
    },
    16: {
        "map_width": 1,
        "map_height": 1,
        "wall": { 
        },
        "item": {
        },
        "basic_code":'''
        character = ['라이캣', '개리', '자바독', '빙키', '뮤라', '소울곰', '대리인 No.1']
        stone = ['피스 스톤', '스페이스 스톤', '마인드 스톤', '리얼리티 스톤', '타임 스톤', '소울 스톤', '파워 스톤']
        '''
    },
    17: {
        "map_width": 4,
        "map_height": 3,
        "wall": {  # (x, y): "wall", 'fence', 'door'
            (0.5, 0): "wall",
            (0.5, 1): "wall",
            (0.5, 2): "wall",
            (1.5, 1): "wall",
            (1.5, 2): "wall",
            (1.5, 3): "wall"
        },
        "item": {
            (2, 0): { "item": "fish-1", "count": 3 },
            (0, 2): { "item": "fish-2", "count": 1 },
            (1, 3): { "item": "fish-2", "count": 2 },
            (2, 2): { "item": "fish-3", "count": 3 },
            (1, 0): { "item": "fish-1", "count": 4 },
            (0, 3): { "item": "fish-3", "count": 2 }
            }
    },
    18: {
        "map_width": 1,
        "map_height": 1,
        "wall": {},
        "item": {},
        "basic_code":"items = [['당근', 3], ['사과', 5], ['당근', 6], ['포도', 4], ['당근', 7]]"
    },
    19: {
        "map_width": 1,
        "map_height": 1,
        "wall": {},
        "item": {},
        "basic_code":'''
        # 요리에 필요한 재료의 조건 확인
        required_ingredient = ["당근", "양상추", "양파", "방울토마토"]
        required_freshness = 5
        required = [False, False, False, False]

        items = [{"name": "당근", "freshness": 7},
            {"name": "사과", "freshness": 5},
            {"name": "당근", "freshness": 6},
            {"name": "포도", "freshness": 4}, 
            {"name": "당근", "freshness": 8}, 
            {"name": "양상추", "freshness": 8},
            {"name": "양파", "freshness": 2}, 
            {"name": "방울토마토", "freshness": 5}]
    '''
    },
    20: {
        "map_width": 4,
        "map_height": 4,
        "wall": {
                (0.5, 1.0): "wall",
                (0.5, 2.0): "wall",
                (1.0, 0.5): "wall",
                (1.0, 2.5): "wall",
                (2.0, 0.5): "wall",
                (2.0, 2.5): "wall",
                (2.5, 1.0): "wall",
                (2.5, 2.0): "wall"},
        "item": {
            (0, 3): { "item": "diamond", "count": 6 },
            (0, 1): { "item": "goldbar", "count": 2 },
            (1, 0): { "item": "diamond", "count": 1 },
            (1, 3): { "item": "goldbar", "count": 7 },
            (2, 0): { "item": "goldbar", "count": 1 },
            (3, 2): { "item": "diamond", "count": 4 },
            (3, 3): { "item": "diamond", "count": 9 }
        },
        "basic_code":'''
        class Treasure:
            # 클래스 정의
            pass

        # 인스턴스 생성
        gold = Treasure('gold', 0)
        diamond = Treasure('diamond', 0)

        # 인스턴스 리스트
        treasure_list = [gold, diamond]

        # 각 인스턴스 출력
        for treasure in treasure_list:
            print(treasure)
        '''
    },
    21: {
        "map_width": 1,
        "map_height": 1,
        "wall": {},
        "item": {},
        "basic_code":'''
        class TribeMember:
            pass

        class PortalQueue:
            pass

        tribe_members = [
            TribeMember('member1'), 
            TribeMember('member2'),
            TribeMember('member3'),
            TribeMember('member4'),
            TribeMember('member5')
        ]
        portal_queue = PortalQueue()

        # 부족원 인스턴스 생성 및 큐에 추가
        for member in tribe_members:
            portal_queue.enter_portal(member)

        # 모든 부족원 이동
        result = portal_queue.transport_all()
        print(result)
        '''
    },
    22: {
        "map_width": 7,
        "map_height": 5,
        "wall": {
            (0.5, 0): "wall",
            (0.5, 1): "wall",
            (0.5, 4): "wall",
            (0.5, 6): "wall",
            (1.0, 2.5) : "wall",
            (1.0, 4.5) : "wall",
            (1.0, 5.5) : "wall",
            (1.5, 1): "wall",
            (1.5, 2): "wall",
            (1.5, 5): "wall",
            (2.0, 1.5) : "wall",
            (2.0, 4.5) : "wall",
            (3.0, 0.5) : "wall",
            (3.0, 2.5) : "wall",
            (3.0, 4.5) : "wall",
            (3.5, 1): "wall",
            (3.5, 4): "wall",
            (4.0, 1.5) : "wall",
            (4.0, 5.5) : "wall"
            },
        "item": {
            (4, 6): { "item": "diamond", "count": 1 },
        },
        "basic_code":'''
        class PathRecorder:
            # 클래스 정의
            pass
        path_recorder = PathRecorder()
        ''',
        "mob_data": [
            {
            "name": "wizard",
            "mob": "wizard",
            "x": 2,
            "y": 3,
            "directions": 3,
            },
            {
            "name": "binky1",
            "mob": "binky",
            "x": 4,
            "y": 0,
            "directions": 0,
            },
            {
            "name": "py1",
            "mob": "py",
            "x": 1,
            "y": 5,
            "directions": 0,
            "hp": 50,
            "power": 10
            },
            {
            "name": "gary1",
            "mob": "gary",
            "x": 2,
            "y": 6,
            "directions": 0,
            "hp": 50,
            }
        ]
    }
}
