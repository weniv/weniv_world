"""
기존 Python 게임 로직을 Django 환경에서 실행하는 엔진
"""
import sys
import io
import traceback
import importlib.util
import os
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any

# Django 전용 coordinate 모듈 생성
class DjangoCoordinate:
    """Django 환경에서 사용할 coordinate 모듈"""
    def __init__(self):
        self.map_data = {"height": 5, "width": 5}
        self.character_data = [
            {
                "character": "licat",
                "character_obj": None,
                "x": 0,
                "y": 0,
                "directions": 0,
                "items": {},
            }
        ]
        self.item_data = {}
        self.wall_data = {"world": {}}
        self.mob_data = []
        self.print_data = []
        self.say_data = []
        
        # 스토리 데이터 임시 저장
        self.story_data = {}

class PythonExecutor:
    def __init__(self):
        # Django 전용 coordinate 모듈 사용
        self.coordinate = DjangoCoordinate()
        
        self.output_buffer = io.StringIO()
        self.error_buffer = io.StringIO()
    
    def execute(self, code: str, session_id: str, story_id: int = None) -> Dict[str, Any]:
        """
        Python 코드를 안전하게 실행
        """
        try:
            # 게임 세션 초기화
            self.initialize_game_session(session_id, story_id)
            
            # 출력 버퍼 초기화
            self.output_buffer = io.StringIO()
            self.error_buffer = io.StringIO()
            
            # 실행 환경 설정
            exec_globals = self.get_execution_globals()
            
            # 출력 캡처하여 코드 실행
            with redirect_stdout(self.output_buffer), redirect_stderr(self.error_buffer):
                exec(code, exec_globals)
            
            # 실행 후 상태 수집
            world_state = self.get_world_state()
            character_state = self.get_character_state()
            
            return {
                'success': True,
                'output': self.output_buffer.getvalue(),
                'world_state': world_state,
                'character_state': character_state
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'output': self.output_buffer.getvalue()
            }
    
    def convert_tuple_keys_to_string(self, data):
        """tuple key를 string으로 변환"""
        if isinstance(data, dict):
            return {str(k): self.convert_tuple_keys_to_string(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.convert_tuple_keys_to_string(item) for item in data]
        else:
            return data

    def initialize_game_session(self, session_id: str, story_id: int = None):
        """게임 세션 초기화"""
        if not self.coordinate:
            return
        
        # Django Story 모델에서 데이터 로드
        if story_id:
            try:
                from apps.story.models import Story
                story = Story.objects.get(id=story_id)
                story_data = story.initial_world_data or {}
                
                # 맵 크기 설정
                self.coordinate.map_data = {
                    'width': story_data.get('map_width', 5),
                    'height': story_data.get('map_height', 5)
                }
                
                # 벽 데이터 설정 (tuple key를 string으로 변환)
                wall_data = story_data.get('wall', {})
                self.coordinate.wall_data = {
                    'world': self.convert_tuple_keys_to_string(wall_data)
                }
                
                # 아이템 데이터 설정 (tuple key를 string으로 변환)
                item_data = story_data.get('item', {})
                self.coordinate.item_data = self.convert_tuple_keys_to_string(item_data)
                
                # 몹 데이터 설정
                self.coordinate.mob_data = story_data.get('mob_data', [])
                
            except Exception as e:
                print(f"Story 로드 실패: {e}")
                # 기본 설정으로 폴백
                self.coordinate.map_data = {"height": 5, "width": 5}
                self.coordinate.wall_data = {"world": {}}
                self.coordinate.item_data = {}
                self.coordinate.mob_data = []
        else:
            # 기본 설정
            self.coordinate.map_data = {"height": 5, "width": 5}
            self.coordinate.wall_data = {"world": {}}
            self.coordinate.item_data = {}
            self.coordinate.mob_data = []
        
        # 캐릭터 초기화
        self.coordinate.character_data = [
            {
                "character": "licat",
                "character_obj": None,
                "x": 0,
                "y": 0,
                "directions": 0,
                "items": {},
            }
        ]
        
        # 출력 데이터 초기화
        self.coordinate.print_data = []
        self.coordinate.say_data = []
    
    def get_execution_globals(self) -> Dict[str, Any]:
        """Python 실행 환경의 전역 변수 설정"""
        # Django 게임 함수들 임포트
        from .django_game_functions import (
            set_executor, mission_start, mission_end, move, turn_left, turn_right,
            pick, put, say, front_is_clear, on_item, item, directions, set_item,
            repeat, turn_around, move_to_wall, turn_left_until_clear, reset
        )
        
        # 현재 실행기를 게임 함수에 설정
        set_executor(self)
        
        globals_dict = {
            # 기본 Python 함수들
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'sorted': sorted,
            'reversed': reversed,
            'enumerate': enumerate,
            'zip': zip,
            'round': round,
            
            # Django 게임 함수들
            'mission_start': mission_start,
            'mission_end': mission_end,
            'move': move,
            'turn_left': turn_left,
            'turn_right': turn_right,
            'pick': pick,
            'put': put,
            'say': say,
            'front_is_clear': front_is_clear,
            'on_item': on_item,
            'item': item,
            'directions': directions,
            'set_item': set_item,
            'repeat': repeat,
            'turn_around': turn_around,
            'move_to_wall': move_to_wall,
            'turn_left_until_clear': turn_left_until_clear,
            'reset': reset,
        }
        
        # 게임 모듈의 전역 변수들 추가
        if self.coordinate:
            globals_dict.update({
                'map_data': self.coordinate.map_data,
                'character_data': self.coordinate.character_data,
                'item_data': self.coordinate.item_data,
                'wall_data': self.coordinate.wall_data,
                'mob_data': self.coordinate.mob_data,
            })
        
        return globals_dict
    
    def get_world_state(self) -> Dict[str, Any]:
        """현재 월드 상태 반환"""
        if not self.coordinate:
            return {}
            
        return {
            'map_data': getattr(self.coordinate, 'map_data', {}),
            'wall_data': getattr(self.coordinate, 'wall_data', {}),
            'item_data': getattr(self.coordinate, 'item_data', {}),
            'mob_data': getattr(self.coordinate, 'mob_data', []),
        }
    
    def get_character_state(self) -> Dict[str, Any]:
        """현재 캐릭터 상태 반환"""
        if not self.coordinate:
            return {}
            
        character_data = getattr(self.coordinate, 'character_data', [])
        if character_data:
            return character_data[0]
        return {}