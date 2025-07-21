#!/usr/bin/env python
"""
게임 엔진 종합 테스트 스크립트
"""
import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.game.engine.executor import PythonExecutor

def test_basic_game_functions():
    """기본 게임 함수 테스트"""
    print("=== 기본 게임 함수 테스트 ===")
    
    executor = PythonExecutor()
    
    # 1. 캐릭터 이동 테스트
    print("\n1. 캐릭터 이동 테스트")
    test_code = """
# 초기 위치 확인
print(f"시작 위치: ({character_data[0]['x']}, {character_data[0]['y']})")

# 이동 테스트
move()
print(f"이동 후 위치: ({character_data[0]['x']}, {character_data[0]['y']})")

# 회전 테스트  
turn_left()
print(f"회전 후 방향: {character_data[0]['directions']}")
"""
    
    result = executor.execute(test_code, "test_session_1")
    print(f"실행 결과: {result['success']}")
    print(f"출력:\n{result.get('output', '')}")
    
    # 2. 아이템 테스트
    print("\n2. 아이템 테스트")
    test_code = """
# 아이템 설정
set_item(0, 0, "beeper", 3)
print(f"아이템 설정됨: {item_data}")

# 아이템 확인
if on_item():
    print("아이템이 있습니다!")
    pick()
    print(f"아이템 획득 후 인벤토리: {character_data[0]['items']}")
else:
    print("아이템이 없습니다.")
"""
    
    result = executor.execute(test_code, "test_session_2")
    print(f"실행 결과: {result['success']}")
    print(f"출력:\n{result.get('output', '')}")

def test_complex_scenarios():
    """복잡한 시나리오 테스트"""
    print("\n=== 복잡한 시나리오 테스트 ===")
    
    executor = PythonExecutor()
    
    # 미로 탐색 시뮬레이션
    print("\n1. 미로 탐색 시뮬레이션")
    test_code = """
def turn_around():
    turn_left()
    turn_left()

def explore_maze():
    steps = 0
    max_steps = 10
    
    while steps < max_steps:
        if front_is_clear():
            move()
            print(f"앞으로 이동: ({character_data[0]['x']}, {character_data[0]['y']})")
        else:
            turn_left()
            print(f"좌회전: 방향 {character_data[0]['directions']}")
        
        steps += 1
        
        # 경계 체크
        if character_data[0]['x'] >= 4 or character_data[0]['y'] >= 4:
            print("맵 끝에 도달!")
            break
    
    print(f"탐색 완료! 최종 위치: ({character_data[0]['x']}, {character_data[0]['y']})")

explore_maze()
"""
    
    result = executor.execute(test_code, "test_session_3")
    print(f"실행 결과: {result['success']}")
    print(f"출력:\n{result.get('output', '')}")

def test_story_integration():
    """스토리 통합 테스트"""
    print("\n=== 스토리 통합 테스트 ===")
    
    executor = PythonExecutor()
    
    # 스토리 1번과 함께 테스트
    print("\n1. 스토리 1번 로드 테스트")
    test_code = """
mission_start()
print(f"맵 크기: {map_data}")
print(f"초기 캐릭터 위치: ({character_data[0]['x']}, {character_data[0]['y']})")

# 간단한 미션 수행
for i in range(3):
    if front_is_clear():
        move()
        print(f"이동 {i+1}: ({character_data[0]['x']}, {character_data[0]['y']})")
    else:
        print("앞이 막혀있습니다!")
        break

mission_end()
"""
    
    result = executor.execute(test_code, "test_session_4", story_id=1)
    print(f"실행 결과: {result['success']}")
    print(f"출력:\n{result.get('output', '')}")
    
    if result['success']:
        world_state = result.get('world_state', {})
        character_state = result.get('character_state', {})
        print(f"최종 월드 상태: {world_state}")
        print(f"최종 캐릭터 상태: {character_state}")

def test_error_handling():
    """에러 처리 테스트"""
    print("\n=== 에러 처리 테스트 ===")
    
    executor = PythonExecutor()
    
    # 1. 문법 오류 테스트
    print("\n1. 문법 오류 테스트")
    invalid_code = """
print("Hello"
move(
"""
    
    result = executor.execute(invalid_code, "test_session_5")
    print(f"실행 결과: {result['success']}")
    if not result['success']:
        print(f"예상된 오류: {result.get('error', '')}")
    
    # 2. 경계 벗어나기 테스트
    print("\n2. 경계 벗어나기 테스트")
    boundary_test = """
# 맵 경계 넘어서 이동 시도
for i in range(10):  # 맵 크기보다 많이 이동
    if front_is_clear():
        move()
        print(f"이동 {i+1}: ({character_data[0]['x']}, {character_data[0]['y']})")
    else:
        print(f"더 이상 이동할 수 없습니다. 위치: ({character_data[0]['x']}, {character_data[0]['y']})")
        break
"""
    
    result = executor.execute(boundary_test, "test_session_6")
    print(f"실행 결과: {result['success']}")
    print(f"출력:\n{result.get('output', '')}")

if __name__ == "__main__":
    try:
        test_basic_game_functions()
        test_complex_scenarios()
        test_story_integration()
        test_error_handling()
        print("\n모든 게임 엔진 테스트 완료!")
    except Exception as e:
        print(f"\n게임 엔진 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()