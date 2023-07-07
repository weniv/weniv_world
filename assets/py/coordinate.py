# 캐릭터 좌표는 전역에서 관리
# 0번째는 default 캐릭터
character_data = [
            {
                'character': 'licat',
                'x': 0,
                'y': 0,
                'direction': 0 # 0(동, 오른쪽), 1(북), 2(서, 오른쪽), 3(남)
            }
]

item_data = []

# 맵 크기는 전역에서 관리
map_data = {
    'height': 5,
    'width': 5
}

running_speed = 1
