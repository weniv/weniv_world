"""
Django 환경에 맞게 변환된 캐릭터 클래스
기존 PyScript/JavaScript 의존성을 제거하고 서버 사이드 로직으로 변환
"""
from typing import Dict, Any, List, Tuple
import time

class Character:
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        name: str = "licat",
        directions: int = 0,
        width: int = 100,
        height: int = 33,
        initHp: int = 100,
        dropRate: float = 0.1,
        initMp: int = 100,
        rotate: int = 0,
    ):
        self.x = x
        self.y = y
        self.name = name
        self.directions = directions  # 0(동), 1(북), 2(서), 3(남)
        self.width = width
        self.height = height
        self.initHp = initHp
        self.dropRate = dropRate
        self.hp = initHp
        self.mp = initMp
        self.initMp = initMp
        self.rotate = rotate
        self.running_time = 0
        
        # 게임 상태 (Django 세션에서 관리)
        self.world_map = None
        self.items = {}
        
    def get_state(self) -> Dict[str, Any]:
        """현재 캐릭터 상태를 딕셔너리로 반환"""
        return {
            'x': self.x,
            'y': self.y,
            'name': self.name,
            'directions': self.directions,
            'hp': self.hp,
            'mp': self.mp,
            'items': self.items.copy(),
            'image_url': f"assets/img/characters/{self.name}-{self.directions}.webp"
        }
    
    def set_world_map(self, world_map):
        """월드 맵 참조 설정"""
        self.world_map = world_map
    
    def move(self) -> Dict[str, Any]:
        """캐릭터 이동"""
        x, y = self.x, self.y
        directions = self.directions
        
        # 다음 위치 계산
        nx, ny = x, y
        if directions == 0:  # 동(오른쪽)
            ny = y + 1
        elif directions == 1:  # 북(위)
            nx = x - 1
        elif directions == 2:  # 서(왼쪽)
            ny = y - 1
        elif directions == 3:  # 남(아래)
            nx = x + 1
        
        # 이동 가능성 검사
        error = self._check_movable(x, y, nx, ny)
        if error:
            return {
                'success': False,
                'error': error,
                'position': {'x': x, 'y': y}
            }
        
        # 위치 업데이트
        self.x = nx
        self.y = ny
        
        return {
            'success': True,
            'position': {'x': nx, 'y': ny},
            'previous_position': {'x': x, 'y': y},
            'animation': {
                'type': 'move',
                'direction': directions
            }
        }
    
    def turn_left(self) -> Dict[str, Any]:
        """왼쪽으로 회전"""
        old_direction = self.directions
        self.directions = (self.directions + 1) % 4
        
        return {
            'success': True,
            'directions': self.directions,
            'previous_directions': old_direction,
            'animation': {
                'type': 'turn_left',
                'image_url': f"assets/img/characters/{self.name}-{self.directions}.webp"
            }
        }
    
    def pick(self) -> Dict[str, Any]:
        """아이템 줍기"""
        if not self.world_map:
            return {'success': False, 'error': 'WorldMapNotSet'}
        
        item = self.world_map.get_item_at(self.x, self.y)
        if not item:
            return {'success': False, 'error': 'ItemIsNotExist'}
        
        # 아이템을 인벤토리에 추가
        item_name = item['item']
        if item_name in self.items:
            self.items[item_name] += 1
        else:
            self.items[item_name] = 1
        
        # 월드에서 아이템 제거
        self.world_map.remove_item_at(self.x, self.y)
        
        return {
            'success': True,
            'item': item_name,
            'inventory': self.items.copy(),
            'animation': {
                'type': 'pick',
                'item': item_name
            }
        }
    
    def put(self, item_name: str) -> Dict[str, Any]:
        """아이템 내려놓기"""
        if not self.world_map:
            return {'success': False, 'error': 'WorldMapNotSet'}
        
        # 인벤토리에 아이템이 있는지 확인
        if item_name not in self.items or self.items[item_name] <= 0:
            return {'success': False, 'error': 'ItemIsNotExist'}
        
        # 발 아래 이미 아이템이 있는지 확인
        existing_item = self.world_map.get_item_at(self.x, self.y)
        if existing_item and existing_item['item'] != item_name:
            return {'success': False, 'error': 'AnotherItemIsExist'}
        
        # 인벤토리에서 아이템 제거
        self.items[item_name] -= 1
        if self.items[item_name] == 0:
            del self.items[item_name]
        
        # 월드에 아이템 추가
        self.world_map.add_item_at(self.x, self.y, item_name)
        
        return {
            'success': True,
            'item': item_name,
            'inventory': self.items.copy(),
            'animation': {
                'type': 'put',
                'item': item_name
            }
        }
    
    def attack(self, skill: str = "claw-yellow") -> Dict[str, Any]:
        """공격"""
        # 스킬 데이터는 설정에서 가져와야 함 (임시로 하드코딩)
        skill_data = {
            "claw-yellow": {"mana": 10, "power": 20},
            "claw-white": {"mana": 15, "power": 30}
        }
        
        if skill not in skill_data:
            return {'success': False, 'error': 'InvalidSkill'}
        
        if skill_data[skill]["mana"] > self.mp:
            return {'success': False, 'error': 'NotEnoughMana'}
        
        # 앞에 벽이 있는지 확인
        if self.typeof_wall() in ["wall", "door"]:
            return {'success': False, 'error': 'WallIsExist'}
        
        # 공격 대상 위치 계산
        nx, ny = self._get_front_position()
        
        if not self.world_map or not self.world_map.is_valid_position(nx, ny):
            return {'success': False, 'error': 'OutOfWorld'}
        
        # 마나 소모
        self.mp -= skill_data[skill]["mana"]
        
        # 몹 공격 (몹 시스템이 구현되면 추가)
        # mob = self.world_map.get_mob_at(nx, ny)
        # if mob:
        #     mob.take_damage(skill_data[skill]["power"])
        
        return {
            'success': True,
            'skill': skill,
            'target_position': {'x': nx, 'y': ny},
            'mp': self.mp,
            'animation': {
                'type': 'attack',
                'skill': skill,
                'target': {'x': nx, 'y': ny}
            }
        }
    
    def eat(self, item_name: str) -> Dict[str, Any]:
        """아이템 먹기"""
        # 먹을 수 있는 아이템 데이터 (임시)
        edible_items = {
            "apple": {"hp": 20, "mp": 10},
            "fish": {"hp": 30, "mp": 0}
        }
        
        if item_name not in edible_items:
            return {'success': False, 'error': 'InedibleItem'}
        
        if item_name not in self.items or self.items[item_name] <= 0:
            return {'success': False, 'error': 'ItemIsNotExist'}
        
        # 아이템 소모
        self.items[item_name] -= 1
        if self.items[item_name] == 0:
            del self.items[item_name]
        
        # HP, MP 회복
        item_effects = edible_items[item_name]
        old_hp, old_mp = self.hp, self.mp
        
        self.hp = min(self.initHp, self.hp + item_effects.get("hp", 0))
        self.mp = min(self.initMp, self.mp + item_effects.get("mp", 0))
        
        return {
            'success': True,
            'item': item_name,
            'hp': {'old': old_hp, 'new': self.hp},
            'mp': {'old': old_mp, 'new': self.mp},
            'inventory': self.items.copy(),
            'animation': {
                'type': 'eat',
                'item': item_name
            }
        }
    
    def front_is_clear(self) -> bool:
        """앞이 비어있는지 확인"""
        return self._is_clear("front")
    
    def left_is_clear(self) -> bool:
        """왼쪽이 비어있는지 확인"""
        return self._is_clear("left")
    
    def right_is_clear(self) -> bool:
        """오른쪽이 비어있는지 확인"""
        return self._is_clear("right")
    
    def back_is_clear(self) -> bool:
        """뒤가 비어있는지 확인"""
        return self._is_clear("back")
    
    def check_bottom(self) -> bool:
        """발 아래 아이템이 있는지 확인"""
        if not self.world_map:
            return False
        return self.world_map.get_item_at(self.x, self.y) is not None
    
    def typeof_wall(self) -> str:
        """앞에 있는 벽의 타입 반환"""
        if not self.world_map:
            return ""
        
        wall_pos = self._get_front_wall_position()
        return self.world_map.get_wall_type(wall_pos[0], wall_pos[1])
    
    def open_door(self) -> Dict[str, Any]:
        """문 열기"""
        wall_type = self.typeof_wall()
        if wall_type != "door":
            return {'success': False, 'error': 'CannotOpenWall'}
        
        wall_pos = self._get_front_wall_position()
        self.world_map.remove_wall(wall_pos[0], wall_pos[1])
        
        return {
            'success': True,
            'wall_position': {'x': wall_pos[0], 'y': wall_pos[1]},
            'animation': {
                'type': 'open_door',
                'position': {'x': wall_pos[0], 'y': wall_pos[1]}
            }
        }
    
    # 내부 메서드들
    def _check_movable(self, x: int, y: int, nx: int, ny: int) -> str:
        """이동 가능성 검사"""
        if not self.world_map:
            return "WorldMapNotSet"
        
        if not self.world_map.is_valid_position(nx, ny):
            return "OutOfWorld"
        
        if self.world_map.has_wall_between(x, y, nx, ny):
            return "WallIsExist"
        
        if self.world_map.has_obstacle_at(nx, ny):
            return "ObstacleExist"
        
        return ""
    
    def _is_clear(self, direction: str) -> bool:
        """특정 방향이 비어있는지 확인"""
        direction_map = {
            "front": 0,
            "left": 1,
            "back": 2,
            "right": 3
        }
        
        target_direction = (self.directions + direction_map[direction]) % 4
        nx, ny = self.x, self.y
        
        if target_direction == 0:  # 동
            ny += 1
        elif target_direction == 1:  # 북
            nx -= 1
        elif target_direction == 2:  # 서
            ny -= 1
        elif target_direction == 3:  # 남
            nx += 1
        
        return self._check_movable(self.x, self.y, nx, ny) == ""
    
    def _get_front_position(self) -> Tuple[int, int]:
        """앞 위치 반환"""
        x, y = self.x, self.y
        if self.directions == 0:  # 동
            return (x, y + 1)
        elif self.directions == 1:  # 북
            return (x - 1, y)
        elif self.directions == 2:  # 서
            return (x, y - 1)
        elif self.directions == 3:  # 남
            return (x + 1, y)
    
    def _get_front_wall_position(self) -> Tuple[float, float]:
        """앞 벽 위치 반환"""
        if self.directions == 0:  # 동
            return (self.x, self.y + 0.5)
        elif self.directions == 1:  # 북
            return (self.x - 0.5, self.y)
        elif self.directions == 2:  # 서
            return (self.x, self.y - 0.5)
        elif self.directions == 3:  # 남
            return (self.x + 0.5, self.y)