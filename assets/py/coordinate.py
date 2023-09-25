# 캐릭터 좌표
# 0번째는 default 캐릭터
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

# 맵 전역에 있는 아이템 데이터
# (x, y): {item: 'beeper', count: 1}
item_data = {}

# 맵 크기
map_data = {"height": 5, "width": 5}


# 한 변 길이
map_size = 100
border_size = 1

running_speed = 1

# 맵에 있는 벽 데이터
wall_data = {"world": {}}
blockingWallType = ["wall", "fence"]  # 이동 불가한 벽 종류
wall_type = "wall"  # 현재 선택되어 있는 벽 종류
