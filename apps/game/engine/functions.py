"""
Django 환경에 맞게 변환된 내장 함수들
기존 built_in_functions.py를 Django 환경에 맞게 변환
"""
from typing import Dict, Any, Optional
import sys
import io

# 전역 게임 상태 (Django 세션에서 관리됨)
_current_executor = None

def set_executor(executor):
    """현재 실행 엔진 설정"""
    global _current_executor
    _current_executor = executor

def get_executor():
    """현재 실행 엔진 반환"""
    return _current_executor

# 기본 캐릭터 함수들
def move():
    """캐릭터 이동"""
    executor = get_executor()
    if executor and executor.character:
        result = executor.character.move()
        executor.add_action('move', result)
        return result
    else:
        raise RuntimeError("Character not available")

def turn_left():
    """왼쪽으로 회전"""
    executor = get_executor()
    if executor and executor.character:
        result = executor.character.turn_left()
        executor.add_action('turn_left', result)
        return result
    else:
        raise RuntimeError("Character not available")

def pick():
    """아이템 줍기"""
    executor = get_executor()
    if executor and executor.character:
        result = executor.character.pick()
        executor.add_action('pick', result)
        return result
    else:
        raise RuntimeError("Character not available")

def put(item_name: str):
    """아이템 내려놓기"""
    executor = get_executor()
    if executor and executor.character:
        result = executor.character.put(item_name)
        executor.add_action('put', result)
        return result
    else:
        raise RuntimeError("Character not available")

def attack(skill: str = "claw-yellow"):
    """공격"""
    executor = get_executor()
    if executor and executor.character:
        result = executor.character.attack(skill)
        executor.add_action('attack', result)
        return result
    else:
        raise RuntimeError("Character not available")

def eat(item_name: str):
    """아이템 먹기"""
    executor = get_executor()
    if executor and executor.character:
        result = executor.character.eat(item_name)
        executor.add_action('eat', result)
        return result
    else:
        raise RuntimeError("Character not available")

# 상태 확인 함수들
def front_is_clear() -> bool:
    """앞이 비어있는지 확인"""
    executor = get_executor()
    if executor and executor.character:
        return executor.character.front_is_clear()
    return False

def left_is_clear() -> bool:
    """왼쪽이 비어있는지 확인"""
    executor = get_executor()
    if executor and executor.character:
        return executor.character.left_is_clear()
    return False

def right_is_clear() -> bool:
    """오른쪽이 비어있는지 확인"""
    executor = get_executor()
    if executor and executor.character:
        return executor.character.right_is_clear()
    return False

def back_is_clear() -> bool:
    """뒤가 비어있는지 확인"""
    executor = get_executor()
    if executor and executor.character:
        return executor.character.back_is_clear()
    return False

def check_bottom() -> bool:
    """발 아래 아이템이 있는지 확인"""
    executor = get_executor()
    if executor and executor.character:
        return executor.character.check_bottom()
    return False

def typeof_wall() -> str:
    """앞에 있는 벽의 타입"""
    executor = get_executor()
    if executor and executor.character:
        return executor.character.typeof_wall()
    return ""

def open_door():
    """문 열기"""
    executor = get_executor()
    if executor and executor.character:
        result = executor.character.open_door()
        executor.add_action('open_door', result)
        return result
    else:
        raise RuntimeError("Character not available")

# 미션 관련 함수들
def mission_start():
    """미션 시작"""
    executor = get_executor()
    if executor and executor.world_map:
        executor.world_map.mission_start()
        executor.add_action('mission_start', {'success': True})

def mission_end():
    """미션 종료"""
    executor = get_executor()
    if executor and executor.world_map:
        executor.world_map.mission_end()
        executor.add_action('mission_end', {'success': True})

# 출력 함수들
def say(message: str):
    """말하기"""
    executor = get_executor()
    print(f"💬 {message}")
    if executor:
        executor.add_action('say', {'message': message})

def show_modal_alert(message: str):
    """모달 알림"""
    executor = get_executor()
    print(f"⚠️ {message}")
    if executor:
        executor.add_action('alert', {'message': message})

# 유틸리티 함수들
def get_character_position() -> Dict[str, int]:
    """캐릭터 위치 반환"""
    executor = get_executor()
    if executor and executor.character:
        return {'x': executor.character.x, 'y': executor.character.y}
    return {'x': 0, 'y': 0}

def get_character_direction() -> int:
    """캐릭터 방향 반환"""
    executor = get_executor()
    if executor and executor.character:
        return executor.character.directions
    return 0

def get_character_items() -> Dict[str, int]:
    """캐릭터 아이템 목록 반환"""
    executor = get_executor()
    if executor and executor.character:
        return executor.character.items.copy()
    return {}

def get_character_hp() -> int:
    """캐릭터 HP 반환"""
    executor = get_executor()
    if executor and executor.character:
        return executor.character.hp
    return 0

def get_character_mp() -> int:
    """캐릭터 MP 반환"""
    executor = get_executor()
    if executor and executor.character:
        return executor.character.mp
    return 0

# 게임 상태 함수들
def get_world_size() -> Dict[str, int]:
    """월드 크기 반환"""
    executor = get_executor()
    if executor and executor.world_map:
        return {'width': executor.world_map.width, 'height': executor.world_map.height}
    return {'width': 5, 'height': 5}

def get_item_at(x: int, y: int) -> Optional[Dict[str, Any]]:
    """특정 위치의 아이템 반환"""
    executor = get_executor()
    if executor and executor.world_map:
        return executor.world_map.get_item_at(x, y)
    return None

# 게임 제어 함수들  
def reset_game():
    """게임 초기화"""
    executor = get_executor()
    if executor:
        executor.reset()
        executor.add_action('reset', {'success': True})

def set_speed(speed: float):
    """게임 속도 설정"""
    executor = get_executor()
    if executor:
        executor.set_speed(speed)
        executor.add_action('set_speed', {'speed': speed})