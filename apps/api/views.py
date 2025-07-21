from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from django.core.cache import cache
import json
import uuid

from apps.story.models import Story
from apps.game.models import GameSession
from apps.progress.models import UserProgress
from apps.game.engine.executor import PythonExecutor


@method_decorator(csrf_exempt, name='dispatch')
class GameAPIView(View):
    """게임 API 통합 엔드포인트"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'execute_code':
                return self.execute_python_code(request, data)
            elif action == 'save_session':
                return self.save_game_session(request, data)
            elif action == 'load_session':
                return self.load_game_session(request, data)
            elif action == 'create_session':
                return self.create_game_session(request, data)
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def execute_python_code(self, request, data):
        """Python 코드 실행"""
        code = data.get('code', '')
        session_id = data.get('session_id')
        story_id = data.get('story_id')

        if not session_id:
            return JsonResponse({'error': 'Session ID required'}, status=400)

        try:
            # Python 게임 엔진 실행
            executor = PythonExecutor()
            result = executor.execute(code, session_id, story_id)

            # 실행 결과 저장
            if story_id:
                story = get_object_or_404(Story, id=story_id)
                session, created = GameSession.objects.update_or_create(
                    session_id=session_id,
                    story=story,
                    defaults={
                        'submitted_code': code,
                        'world_data': result.get('world_state', {}),
                        'character_data': result.get('character_state', {}),
                        'is_completed': result.get('success', False)
                    }
                )

                # 사용자 진행률 업데이트
                existing_progress = UserProgress.objects.filter(
                    session_id=session_id, story=story
                ).first()
                
                current_attempts = existing_progress.attempts if existing_progress else 0
                
                progress, created = UserProgress.objects.update_or_create(
                    session_id=session_id,
                    story=story,
                    defaults={
                        'submitted_code': code,
                        'completed': result.get('success', False),
                        'attempts': current_attempts + 1
                    }
                )

            return JsonResponse({
                'success': True,
                'result': result,
                'world_state': result.get('world_state', {}),
                'character_state': result.get('character_state', {}),
                'output': result.get('output', ''),
                'error': result.get('error')
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    def save_game_session(self, request, data):
        """게임 세션 저장"""
        session_id = data.get('session_id')
        story_id = data.get('story_id')
        world_data = data.get('world_data', {})
        character_data = data.get('character_data', {})
        submitted_code = data.get('submitted_code', '')

        if not session_id:
            return JsonResponse({'error': 'Session ID required'}, status=400)

        try:
            if story_id:
                story = get_object_or_404(Story, id=story_id)
                session, created = GameSession.objects.update_or_create(
                    session_id=session_id,
                    story=story,
                    defaults={
                        'world_data': world_data,
                        'character_data': character_data,
                        'submitted_code': submitted_code
                    }
                )
            else:
                # 자유 모드 세션 저장
                session, created = GameSession.objects.update_or_create(
                    session_id=session_id,
                    defaults={
                        'world_data': world_data,
                        'character_data': character_data,
                        'submitted_code': submitted_code
                    }
                )

            return JsonResponse({
                'success': True,
                'session_id': session.session_id,
                'created': created
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def load_game_session(self, request, data):
        """게임 세션 로드"""
        session_id = data.get('session_id')
        story_id = data.get('story_id')

        if not session_id:
            return JsonResponse({'error': 'Session ID required'}, status=400)

        try:
            if story_id:
                story = get_object_or_404(Story, id=story_id)
                session = GameSession.objects.filter(
                    session_id=session_id,
                    story=story
                ).first()
            else:
                session = GameSession.objects.filter(
                    session_id=session_id,
                    story__isnull=True
                ).first()

            if not session:
                # 세션이 없으면 기본 데이터로 새 세션 생성
                default_data = {
                    'world_data': {
                        'height': 5,
                        'width': 5
                    },
                    'character_data': {
                        'x': 0,
                        'y': 0,
                        'direction': 0,
                        'items': {}
                    }
                }
                return JsonResponse({
                    'success': True,
                    'session_data': default_data,
                    'new_session': True
                })

            return JsonResponse({
                'success': True,
                'session_data': {
                    'world_data': session.world_data,
                    'character_data': session.character_data,
                    'submitted_code': session.submitted_code,
                    'is_completed': session.is_completed
                },
                'new_session': False
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def create_game_session(self, request, data):
        """새 게임 세션 생성"""
        story_id = data.get('story_id')
        
        # 고유한 세션 ID 생성
        session_id = str(uuid.uuid4())

        try:
            if story_id:
                story = get_object_or_404(Story, id=story_id)
                session = GameSession.objects.create(
                    session_id=session_id,
                    story=story,
                    world_data=story.initial_world_data or {
                        'height': 5,
                        'width': 5
                    },
                    character_data={
                        'x': 0,
                        'y': 0,
                        'direction': 0,
                        'items': {}
                    }
                )
            else:
                session = GameSession.objects.create(
                    session_id=session_id,
                    world_data={
                        'height': 5,
                        'width': 5
                    },
                    character_data={
                        'x': 0,
                        'y': 0,
                        'direction': 0,
                        'items': {}
                    }
                )

            return JsonResponse({
                'success': True,
                'session_id': session_id,
                'session_data': {
                    'world_data': session.world_data,
                    'character_data': session.character_data
                }
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def execute_code(request):
    """Python 코드 실행 API"""
    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        session_id = data.get('session_id')
        story_id = data.get('story_id')

        # 직접 GameAPIView 메서드 호출
        api_view = GameAPIView()
        return api_view.execute_python_code(request, data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def save_session(request):
    """게임 세션 저장 API"""
    try:
        data = json.loads(request.body)
        api_view = GameAPIView()
        return api_view.save_game_session(request, data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def load_session(request):
    """게임 세션 로드 API"""
    try:
        data = json.loads(request.body)
        api_view = GameAPIView()
        return api_view.load_game_session(request, data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_session(request):
    """새 게임 세션 생성 API"""
    try:
        data = json.loads(request.body)
        api_view = GameAPIView()
        return api_view.create_game_session(request, data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@cache_page(60 * 15)  # 15분 캐시
@require_http_methods(["GET"])
def get_stories(request):
    """스토리 목록 조회 API"""
    try:
        # 캐시 키 생성
        cache_key = 'stories_list_active'
        stories_data = cache.get(cache_key)
        
        if stories_data is None:
            stories = Story.objects.filter(is_active=True).select_related('category').order_by('category__order', 'order')
            
            stories_data = []
            for story in stories:
                stories_data.append({
                    'id': story.id,
                    'title': story.title,
                    'content': story.content,
                    'objectives': story.objectives,
                    'difficulty': story.difficulty,
                    'order': story.order,
                    'category': {
                        'id': story.category.id,
                        'name': story.category.name
                    } if story.category else None,
                    'initial_world_data': story.initial_world_data,
                    'solution_code': story.solution_code
                })
            
            # 캐시에 저장 (15분)
            cache.set(cache_key, stories_data, 60 * 15)

        return JsonResponse({
            'success': True,
            'stories': stories_data
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_story(request, story_id):
    """개별 스토리 조회 API"""
    try:
        story = get_object_or_404(Story, id=story_id, is_active=True)
        
        story_data = {
            'id': story.id,
            'title': story.title,
            'content': story.content,
            'objectives': story.objectives,
            'difficulty': story.difficulty,
            'order': story.order,
            'category': {
                'id': story.category.id,
                'name': story.category.name
            } if story.category else None,
            'initial_world_data': story.initial_world_data,
            'solution_code': story.solution_code
        }

        return JsonResponse({
            'success': True,
            'story': story_data
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
