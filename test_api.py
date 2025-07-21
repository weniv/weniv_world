#!/usr/bin/env python
"""
Django API 엔드포인트 테스트 스크립트
"""
import os
import django
import json
from django.test import Client

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    client = Client()
    
    print("=== Django API 엔드포인트 테스트 ===\n")
    
    # 1. 스토리 목록 API 테스트
    print("1. 스토리 목록 API 테스트")
    response = client.get('/api/stories/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            stories = data.get('stories', [])
            print(f"   스토리 개수: {len(stories)}")
            if stories:
                print(f"   첫 번째 스토리: {stories[0]['title']}")
        else:
            print(f"   에러: {data}")
    print()
    
    # 2. 개별 스토리 API 테스트
    print("2. 개별 스토리 API 테스트 (스토리 1)")
    response = client.get('/api/stories/1/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            story = data.get('story')
            print(f"   스토리 제목: {story['title']}")
            print(f"   스토리 난이도: {story['difficulty']}")
        else:
            print(f"   에러: {data}")
    print()
    
    # 3. 게임 세션 생성 API 테스트
    print("3. 게임 세션 생성 API 테스트")
    response = client.post('/api/create-session/', 
                          data=json.dumps({'story_id': 1}),
                          content_type='application/json')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            session_id = data.get('session_id')
            print(f"   세션 ID: {session_id}")
            
            # 4. Python 코드 실행 API 테스트
            print("\n4. Python 코드 실행 API 테스트")
            test_code = """
mission_start()
print("Hello, Weniv World!")
move()
print("캐릭터가 이동했습니다!")
mission_end()
"""
            response = client.post('/api/execute-code/',
                                 data=json.dumps({
                                     'code': test_code,
                                     'session_id': session_id,
                                     'story_id': 1
                                 }),
                                 content_type='application/json')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   실행 성공!")
                    print(f"   출력: {data.get('output', '').strip()}")
                    print(f"   월드 상태: {data.get('world_state', {})}")
                    print(f"   캐릭터 상태: {data.get('character_state', {})}")
                else:
                    print(f"   실행 실패: {data.get('error')}")
            
        else:
            print(f"   에러: {data}")
    print()

def test_admin_access():
    """Django Admin 접근 테스트"""
    client = Client()
    
    print("=== Django Admin 접근 테스트 ===\n")
    
    response = client.get('/admin/')
    print(f"Admin 페이지 Status: {response.status_code}")
    if response.status_code == 200:
        print("Admin 페이지 접근 성공!")
    print()

def test_main_page():
    """메인 페이지 테스트"""
    client = Client()
    
    print("=== 메인 페이지 테스트 ===\n")
    
    response = client.get('/')
    print(f"메인 페이지 Status: {response.status_code}")
    if response.status_code == 200:
        print("메인 페이지 로드 성공!")
        # 스토리 데이터가 템플릿에 포함되었는지 확인
        content = response.content.decode('utf-8')
        if 'window.STORY_DATA' in content:
            print("스토리 데이터가 템플릿에 포함됨!")
        else:
            print("스토리 데이터가 템플릿에 포함되지 않음")
    print()

if __name__ == "__main__":
    try:
        test_main_page()
        test_admin_access()
        test_api_endpoints()
        print("모든 테스트 완료!")
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()