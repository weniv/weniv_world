"""
Django 환경에서 사용할 게임 함수들
기존 built_in_functions.py를 Django 서버 환경에 맞게 수정
"""

# 게임 상태를 위한 전역 변수들
current_executor = None

def set_executor(executor):
    """현재 실행기 설정"""
    global current_executor
    current_executor = executor

def get_coordinate():
    """현재 coordinate 모듈 반환"""
    if current_executor and current_executor.coordinate:
        return current_executor.coordinate
    return None

def mission_start():
    """미션 시작"""
    print("미션을 시작합니다!")
    return True

def mission_end():
    """미션 완료"""
    print("미션을 완료했습니다!")
    return True

def move():
    """캐릭터 이동"""
    coordinate = get_coordinate()
    if not coordinate or not coordinate.character_data:
        return False
    
    char = coordinate.character_data[0]
    x, y, direction = char['x'], char['y'], char['directions']
    
    # 방향에 따른 이동
    if direction == 0:  # 동쪽 (오른쪽)
        new_x = x + 1
        new_y = y
    elif direction == 1:  # 북쪽 (위쪽)
        new_x = x
        new_y = y - 1
    elif direction == 2:  # 서쪽 (왼쪽)
        new_x = x - 1
        new_y = y
    elif direction == 3:  # 남쪽 (아래쪽)
        new_x = x
        new_y = y + 1
    else:
        return False
    
    # 맵 경계 체크
    if (0 <= new_x < coordinate.map_data.get('width', 5) and 
        0 <= new_y < coordinate.map_data.get('height', 5)):
        char['x'] = new_x
        char['y'] = new_y
        print(f"캐릭터가 ({new_x}, {new_y})로 이동했습니다.")
        return True
    else:
        print("맵을 벗어날 수 없습니다!")
        return False

def turn_left():
    """왼쪽으로 회전"""
    coordinate = get_coordinate()
    if not coordinate or not coordinate.character_data:
        return False
    
    char = coordinate.character_data[0]
    char['directions'] = (char['directions'] + 1) % 4
    
    directions = ['동쪽', '북쪽', '서쪽', '남쪽']
    print(f"캐릭터가 {directions[char['directions']]}로 회전했습니다.")
    return True

def turn_right():
    """오른쪽으로 회전"""
    coordinate = get_coordinate()
    if not coordinate or not coordinate.character_data:
        return False
    
    char = coordinate.character_data[0]
    char['directions'] = (char['directions'] - 1) % 4
    
    directions = ['동쪽', '북쪽', '서쪽', '남쪽']
    print(f"캐릭터가 {directions[char['directions']]}로 회전했습니다.")
    return True

def pick():
    """아이템 줍기"""
    coordinate = get_coordinate()
    if not coordinate or not coordinate.character_data:
        return False
    
    char = coordinate.character_data[0]
    pos_key = f"({char['x']}, {char['y']})"
    
    if pos_key in coordinate.item_data:
        item_info = coordinate.item_data[pos_key]
        item_name = item_info['item']
        count = item_info.get('count', 1)
        
        # 캐릭터 인벤토리에 아이템 추가
        if item_name in char['items']:
            char['items'][item_name] += count
        else:
            char['items'][item_name] = count
        
        # 맵에서 아이템 제거
        del coordinate.item_data[pos_key]
        
        print(f"{item_name} {count}개를 주웠습니다!")
        return True
    else:
        print("여기에는 주울 아이템이 없습니다.")
        return False

def put(item_name):
    """아이템 놓기"""
    coordinate = get_coordinate()
    if not coordinate or not coordinate.character_data:
        return False
    
    char = coordinate.character_data[0]
    
    if item_name in char['items'] and char['items'][item_name] > 0:
        pos_key = f"({char['x']}, {char['y']})"
        
        # 아이템을 맵에 놓기
        coordinate.item_data[pos_key] = {
            'item': item_name,
            'count': 1
        }
        
        # 캐릭터 인벤토리에서 아이템 제거
        char['items'][item_name] -= 1
        if char['items'][item_name] == 0:
            del char['items'][item_name]
        
        print(f"{item_name}을(를) 놓았습니다!")
        return True
    else:
        print(f"{item_name}을(를) 가지고 있지 않습니다.")
        return False

def say(message):
    """메시지 출력"""
    print(f"[말하기] {message}")

def front_is_clear():
    """앞이 비어있는지 확인"""
    coordinate = get_coordinate()
    if not coordinate or not coordinate.character_data:
        return True
    
    char = coordinate.character_data[0]
    x, y, direction = char['x'], char['y'], char['directions']
    
    # 앞 위치 계산
    if direction == 0:  # 동쪽
        front_x, front_y = x + 1, y
    elif direction == 1:  # 북쪽
        front_x, front_y = x, y - 1
    elif direction == 2:  # 서쪽
        front_x, front_y = x - 1, y
    elif direction == 3:  # 남쪽
        front_x, front_y = x, y + 1
    else:
        return True
    
    # 맵 경계 체크
    if (front_x < 0 or front_x >= coordinate.map_data.get('width', 5) or
        front_y < 0 or front_y >= coordinate.map_data.get('height', 5)):
        return False
    
    # 벽 체크 (추후 구현)
    return True

def on_item():
    """현재 위치에 아이템이 있는지 확인"""
    coordinate = get_coordinate()
    if not coordinate or not coordinate.character_data:
        return False
    
    char = coordinate.character_data[0]
    pos_key = f"({char['x']}, {char['y']})"
    
    return pos_key in coordinate.item_data

def item():
    """현재 캐릭터가 가진 아이템들 반환"""
    coordinate = get_coordinate()
    if not coordinate or not coordinate.character_data:
        return {}
    
    return coordinate.character_data[0]['items'].copy()

def directions():
    """현재 캐릭터가 바라보는 방향 반환"""
    coordinate = get_coordinate()
    if not coordinate or not coordinate.character_data:
        return 0
    
    return coordinate.character_data[0]['directions']

def set_item(x, y, item_name, count=1):
    """맵에 아이템 설정"""
    coordinate = get_coordinate()
    if not coordinate:
        return False
    
    pos_key = f"({x}, {y})"
    coordinate.item_data[pos_key] = {
        'item': item_name,
        'count': count
    }
    print(f"({x}, {y})에 {item_name} {count}개를 설정했습니다.")
    return True

def repeat(count, func):
    """함수를 count번 반복 실행"""
    for i in range(count):
        result = func()
        if result is False:  # 함수가 False를 반환하면 중단
            break
    return True

# modules.py의 함수들도 포함
def turn_around():
    """뒤로 회전 (180도)"""
    turn_left()
    turn_left()

def move_to_wall():
    """벽에 닿을 때까지 이동"""
    while front_is_clear():
        if not move():
            break

def turn_left_until_clear():
    """앞이 비어있을 때까지 왼쪽으로 회전"""
    while not front_is_clear():
        turn_left()

# 추가 게임 함수들
def character_data():
    """현재 캐릭터 데이터 반환"""
    coordinate = get_coordinate()
    if coordinate and coordinate.character_data:
        return coordinate.character_data[0].copy()
    return {}

def map_data():
    """현재 맵 데이터 반환"""
    coordinate = get_coordinate()
    if coordinate:
        return coordinate.map_data.copy()
    return {}

def item_data():
    """현재 아이템 데이터 반환"""
    coordinate = get_coordinate()
    if coordinate:
        return coordinate.item_data.copy()
    return {}

def reset():
    """게임 상태 초기화"""
    coordinate = get_coordinate()
    if coordinate and coordinate.character_data:
        char = coordinate.character_data[0]
        char['x'] = 0
        char['y'] = 0
        char['directions'] = 0
        char['items'] = {}
        print("게임이 초기화되었습니다!")
        return True
    return False