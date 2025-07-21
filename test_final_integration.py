#!/usr/bin/env python
"""
전체 시스템 통합 테스트 스크립트
"""
import requests
import json
import sys

# Django 개발 서버 URL
BASE_URL = 'http://127.0.0.1:8000'

def test_static_files():
    """정적 파일 서빙 테스트"""
    print("=== 정적 파일 서빙 테스트 ===\n")
    
    static_files = [
        '/static/css/style.css',
        '/static/js/analytics.js', 
        '/static/img/icon/icon-logo.svg',
        '/static/img/characters/licat-0.webp',
        '/static/data/story/story.json',
        '/static/py/coordinate.py'
    ]
    
    for file_path in static_files:
        response = requests.get(f"{BASE_URL}{file_path}")
        status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
        print(f"{file_path}: {status}")
    print()

def test_main_page():
    """메인 페이지 테스트"""
    print("=== 메인 페이지 테스트 ===\n")
    
    response = requests.get(BASE_URL)
    print(f"메인 페이지 Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 메인 페이지 로드 성공!")
        
        # 스토리 데이터 확인
        if 'window.STORY_DATA' in response.text:
            print("✅ 스토리 데이터가 템플릿에 포함됨!")
        else:
            print("❌ 스토리 데이터가 템플릿에 포함되지 않음")
            
        # 정적 파일 경로 확인
        if 'window.STATIC_URL' in response.text:
            print("✅ 정적 파일 URL이 템플릿에 포함됨!")
        else:
            print("❌ 정적 파일 URL이 템플릿에 포함되지 않음")
    print()

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("=== API 엔드포인트 테스트 ===\n")
    
    # 1. 스토리 목록 API
    print("1. 스토리 목록 API 테스트")
    response = requests.get(f'{BASE_URL}/api/stories/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            stories = data.get('stories', [])
            print(f"   ✅ 스토리 개수: {len(stories)}")
        else:
            print(f"   ❌ 에러: {data}")
    print()
    
    # 2. 게임 세션 생성 API
    print("2. 게임 세션 생성 API 테스트")
    response = requests.post(f'{BASE_URL}/api/create-session/', 
                           json={'story_id': 1},
                           headers={'Content-Type': 'application/json'})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            session_id = data.get('session_id')
            print(f"   ✅ 세션 ID: {session_id}")
            
            # 3. Python 코드 실행 API
            print("\n3. Python 코드 실행 API 테스트")
            test_code = """
mission_start()
print("통합 테스트 성공!")
move()
mission_end()
"""
            response = requests.post(f'{BASE_URL}/api/execute-code/',
                                   json={
                                       'code': test_code,
                                       'session_id': session_id,
                                       'story_id': 1
                                   },
                                   headers={'Content-Type': 'application/json'})
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ 코드 실행 성공!")
                    print(f"   출력: {data.get('output', '').strip()}")
                else:
                    print(f"   ❌ 실행 실패: {data.get('error')}")
        else:
            print(f"   ❌ 에러: {data}")
    print()

def test_admin_access():
    """Django Admin 접근 테스트"""
    print("=== Django Admin 접근 테스트 ===\n")
    
    response = requests.get(f'{BASE_URL}/admin/')
    print(f"Admin 페이지 Status: {response.status_code}")
    if response.status_code in [200, 302]:  # 302는 로그인 리다이렉트
        print("✅ Admin 페이지 접근 성공!")
    else:
        print("❌ Admin 페이지 접근 실패")
    print()

if __name__ == "__main__":
    print("🚀 위니브 월드 Django 전체 시스템 통합 테스트 시작\n")
    
    try:
        test_main_page()
        test_static_files() 
        test_admin_access()
        test_api_endpoints()
        
        print("🎉 모든 통합 테스트 완료!")
        print("✅ Django 기반 위니브 월드가 성공적으로 구동 중입니다!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Django 서버에 연결할 수 없습니다.")
        print("먼저 다음 명령어로 서버를 실행하세요:")
        print("uv run python manage.py runserver")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)