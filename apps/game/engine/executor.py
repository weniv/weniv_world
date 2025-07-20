"""
Python 코드를 안전하게 실행하는 엔진
Django 환경에서 사용자 코드를 샌드박스에서 실행
"""
import sys
import io
import traceback
import time
import threading
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, List, Optional

from .character import Character
from .world_map import Map
from .functions import set_executor

class PythonExecutor:
    def __init__(self):
        self.world_map = None
        self.character = None
        self.output_buffer = io.StringIO()
        self.error_buffer = io.StringIO()
        self.actions = []  # 실행된 액션들 기록
        self.execution_time = 0
        self.max_execution_time = 30  # 최대 실행 시간 (초)
        self.speed = 1.0  # 게임 속도
    
    def initialize_session(self, session_data: Dict[str, Any]):
        """게임 세션 초기화"""
        # 월드 맵 초기화
        world_data = session_data.get('world_data', {})
        self.world_map = Map(world_data)
        
        # 캐릭터 초기화
        character_data = session_data.get('character_data', {})
        self.character = Character(
            x=character_data.get('x', 0),
            y=character_data.get('y', 0),
            name=character_data.get('name', 'licat'),
            directions=character_data.get('directions', 0),
            initHp=character_data.get('initHp', 100),
            initMp=character_data.get('initMp', 100)
        )
        
        # 캐릭터에 월드 맵 참조 설정
        self.character.set_world_map(self.world_map)
        
        # 캐릭터를 월드에 추가
        self.world_map.add_character(self.character.get_state())
        
        # 전역 실행기 설정
        set_executor(self)
        
        # 액션 로그 초기화
        self.actions = []
    
    def execute(self, code: str) -> Dict[str, Any]:
        """Python 코드 실행"""
        start_time = time.time()
        
        # 출력 버퍼 초기화
        self.output_buffer = io.StringIO()
        self.error_buffer = io.StringIO()
        
        try:
            # 실행 환경 설정
            exec_globals = self.get_execution_globals()
            
            # 시간 제한을 위한 타이머 설정
            execution_thread = threading.Thread(
                target=self._execute_with_timeout,
                args=(code, exec_globals)
            )
            execution_thread.daemon = True
            execution_thread.start()
            execution_thread.join(self.max_execution_time)
            
            if execution_thread.is_alive():
                return {
                    'success': False,
                    'error': 'ExecutionTimeout',
                    'message': f'코드 실행이 {self.max_execution_time}초를 초과했습니다.',
                    'output': self.output_buffer.getvalue()
                }
            
            self.execution_time = time.time() - start_time
            
            return {
                'success': True,
                'output': self.output_buffer.getvalue(),
                'actions': self.actions.copy(),
                'world_state': self.get_world_state(),
                'character_state': self.get_character_state(),
                'execution_time': self.execution_time
            }
            
        except Exception as e:
            self.execution_time = time.time() - start_time
            
            return {
                'success': False,
                'error': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc(),
                'output': self.output_buffer.getvalue(),
                'actions': self.actions.copy(),
                'execution_time': self.execution_time
            }
    
    def _execute_with_timeout(self, code: str, exec_globals: Dict[str, Any]):
        """시간 제한이 있는 코드 실행"""
        try:
            with redirect_stdout(self.output_buffer), redirect_stderr(self.error_buffer):
                exec(code, exec_globals)
        except Exception as e:
            # 예외를 다시 발생시켜 메인 스레드에서 처리하도록 함
            raise e
    
    def get_execution_globals(self) -> Dict[str, Any]:
        """Python 실행 환경의 전역 변수 설정"""
        # 기존 게임 함수들 임포트
        from .functions import (
            move, turn_left, pick, put, attack, eat,
            front_is_clear, left_is_clear, right_is_clear, back_is_clear,
            check_bottom, typeof_wall, open_door,
            mission_start, mission_end, say, show_modal_alert,
            get_character_position, get_character_direction, get_character_items,
            get_character_hp, get_character_mp, get_world_size, get_item_at,
            reset_game, set_speed
        )
        
        return {
            # 게임 함수들
            'move': move,
            'turn_left': turn_left,
            'pick': pick,
            'put': put,
            'attack': attack,
            'eat': eat,
            'front_is_clear': front_is_clear,
            'left_is_clear': left_is_clear,
            'right_is_clear': right_is_clear,
            'back_is_clear': back_is_clear,
            'check_bottom': check_bottom,
            'typeof_wall': typeof_wall,
            'open_door': open_door,
            'mission_start': mission_start,
            'mission_end': mission_end,
            'say': say,
            'show_modal_alert': show_modal_alert,
            
            # 유틸리티 함수들
            'get_position': get_character_position,
            'get_direction': get_character_direction,
            'get_items': get_character_items,
            'get_hp': get_character_hp,
            'get_mp': get_character_mp,
            'get_world_size': get_world_size,
            'get_item_at': get_item_at,
            'reset_game': reset_game,
            'set_speed': set_speed,
            
            # 기본 Python 함수들 (제한된)
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round,
            'sorted': sorted,
            'reversed': reversed,
            'enumerate': enumerate,
            'zip': zip,
            
            # 제어 구조
            'True': True,
            'False': False,
            'None': None,
            
            # 수학 함수들 (안전한 것들만)
            '__builtins__': {
                'len': len,
                'range': range,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'print': print,
            }
        }
    
    def add_action(self, action_type: str, action_data: Dict[str, Any]):
        """액션 로그 추가"""
        action = {
            'type': action_type,
            'data': action_data,
            'timestamp': time.time(),
            'character_state': self.character.get_state() if self.character else {},
            'world_state_snapshot': self.get_world_state()
        }
        self.actions.append(action)
    
    def get_world_state(self) -> Dict[str, Any]:
        """현재 월드 상태 반환"""
        if self.world_map:
            return self.world_map.get_state()
        return {}
    
    def get_character_state(self) -> Dict[str, Any]:
        """현재 캐릭터 상태 반환"""
        if self.character:
            return self.character.get_state()
        return {}
    
    def get_session_data(self) -> Dict[str, Any]:
        """세션 데이터 반환 (저장용)"""
        return {
            'world_data': self.get_world_state(),
            'character_data': self.get_character_state(),
            'actions': self.actions.copy(),
            'execution_time': self.execution_time
        }
    
    def set_speed(self, speed: float):
        """게임 속도 설정"""
        self.speed = max(0.1, min(10.0, speed))  # 0.1x ~ 10x 속도
    
    def reset(self):
        """실행기 초기화"""
        self.actions = []
        self.execution_time = 0
        if self.world_map:
            self.world_map.reset()
        if self.character:
            self.character.x = 0
            self.character.y = 0
            self.character.directions = 0
            self.character.hp = self.character.initHp
            self.character.mp = self.character.initMp
            self.character.items = {}
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """코드 검증 (위험한 코드 차단)"""
        dangerous_keywords = [
            'import', 'exec', 'eval', 'open', 'file', 'input', 'raw_input',
            '__import__', '__builtins__', 'globals', 'locals', 'vars',
            'dir', 'hasattr', 'getattr', 'setattr', 'delattr',
            'compile', 'reload', 'exit', 'quit'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in code:
                return {
                    'valid': False,
                    'error': f'위험한 키워드가 감지되었습니다: {keyword}'
                }
        
        # 기본적인 구문 검사
        try:
            compile(code, '<string>', 'exec')
            return {'valid': True}
        except SyntaxError as e:
            return {
                'valid': False,
                'error': f'구문 오류: {str(e)}'
            }