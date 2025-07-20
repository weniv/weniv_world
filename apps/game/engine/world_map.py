"""
Django 환경에 맞게 변환된 월드 맵 클래스
기존 PyScript/JavaScript 의존성을 제거하고 서버 사이드 로직으로 변환
"""
from typing import Dict, Any, List, Tuple, Optional

class Map:
    def __init__(self, world_data: Dict[str, Any] = None):
        if world_data is None:
            world_data = {"height": 5, "width": 5}
        
        self.height = world_data.get("height", 5)
        self.width = world_data.get("width", 5)
        
        # 게임 상태 데이터
        self.items = world_data.get("items", {})  # {(x, y): {"item": "beeper", "count": 1}}
        self.walls = world_data.get("walls", {})  # {(x, y): "wall_type"}
        self.mobs = world_data.get("mobs", [])    # [{"x": 1, "y": 1, "name": "mob1", "hp": 100}]
        self.characters = world_data.get("characters", [])
        
        # 유효한 아이템 목록
        self.valid_items = ["beeper", "apple", "fish", "diamond", "goldbar"]
        self.wall_blocked = ["wall", "fence"]
    
    def get_state(self) -> Dict[str, Any]:
        """현재 월드 상태를 딕셔너리로 반환"""
        return {
            "height": self.height,
            "width": self.width,
            "items": self.items.copy(),
            "walls": self.walls.copy(),
            "mobs": self.mobs.copy(),
            "characters": self.characters.copy()
        }
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """좌표가 유효한 범위인지 확인"""
        return 0 <= x < self.height and 0 <= y < self.width
    
    def get_item_at(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """특정 위치의 아이템 반환"""
        return self.items.get((x, y))
    
    def add_item_at(self, x: int, y: int, item_name: str, count: int = 1):
        """특정 위치에 아이템 추가"""
        if not self.is_valid_position(x, y):
            return False
        
        if (x, y) in self.items:
            # 기존 아이템이 있는 경우
            existing_item = self.items[(x, y)]
            if existing_item["item"] == item_name:
                existing_item["count"] += count
            else:
                return False  # 다른 아이템이 이미 있음
        else:
            # 새 아이템 추가
            self.items[(x, y)] = {"item": item_name, "count": count}
        
        return True
    
    def remove_item_at(self, x: int, y: int, count: int = 1) -> bool:
        """특정 위치의 아이템 제거"""
        if (x, y) not in self.items:
            return False
        
        item = self.items[(x, y)]
        item["count"] -= count
        
        if item["count"] <= 0:
            del self.items[(x, y)]
        
        return True
    
    def get_wall_type(self, x: float, y: float) -> str:
        """특정 위치의 벽 타입 반환"""
        return self.walls.get((x, y), "")
    
    def add_wall(self, x: float, y: float, wall_type: str):
        """벽 추가"""
        self.walls[(x, y)] = wall_type
    
    def remove_wall(self, x: float, y: float):
        """벽 제거"""
        if (x, y) in self.walls:
            del self.walls[(x, y)]
    
    def has_wall_between(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """두 위치 사이에 벽이 있는지 확인"""
        wall_x = float((x1 + x2) / 2)
        wall_y = float((y1 + y2) / 2)
        
        wall_type = self.get_wall_type(wall_x, wall_y)
        return wall_type in (self.wall_blocked + ["door"])
    
    def has_obstacle_at(self, x: int, y: int) -> bool:
        """특정 위치에 장애물(캐릭터, 몹)이 있는지 확인"""
        # 캐릭터 확인
        for char in self.characters:
            if char.get("x") == x and char.get("y") == y:
                return True
        
        # 몹 확인
        for mob in self.mobs:
            if mob.get("x") == x and mob.get("y") == y:
                return True
        
        return False
    
    def get_mob_at(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """특정 위치의 몹 반환"""
        for mob in self.mobs:
            if mob.get("x") == x and mob.get("y") == y:
                return mob
        return None
    
    def add_mob(self, x: int, y: int, name: str, hp: int = 100):
        """몹 추가"""
        if not self.is_valid_position(x, y):
            return False
        
        mob = {
            "x": x,
            "y": y,
            "name": name,
            "hp": hp,
            "max_hp": hp
        }
        self.mobs.append(mob)
        return True
    
    def remove_mob(self, x: int, y: int):
        """몹 제거"""
        self.mobs = [mob for mob in self.mobs if not (mob.get("x") == x and mob.get("y") == y)]
    
    def damage_mob_at(self, x: int, y: int, damage: int) -> bool:
        """특정 위치의 몹에 데미지"""
        mob = self.get_mob_at(x, y)
        if not mob:
            return False
        
        mob["hp"] -= damage
        if mob["hp"] <= 0:
            self.remove_mob(x, y)
        
        return True
    
    def add_character(self, character_data: Dict[str, Any]):
        """캐릭터 추가"""
        self.characters.append(character_data)
    
    def update_character(self, character_name: str, **kwargs):
        """캐릭터 정보 업데이트"""
        for char in self.characters:
            if char.get("character") == character_name:
                char.update(kwargs)
                break
    
    def get_character(self, character_name: str) -> Optional[Dict[str, Any]]:
        """캐릭터 정보 반환"""
        for char in self.characters:
            if char.get("character") == character_name:
                return char
        return None
    
    def mission_start(self):
        """미션 시작 - 필요시 구현"""
        pass
    
    def mission_end(self):
        """미션 종료 - 필요시 구현"""
        pass
    
    def reset(self, world_data: Dict[str, Any] = None):
        """월드 초기화"""
        if world_data:
            self.__init__(world_data)
        else:
            self.items.clear()
            self.walls.clear()
            self.mobs.clear()
            self.characters.clear()
    
    def get_map_data_for_frontend(self) -> Dict[str, Any]:
        """프론트엔드에서 사용할 맵 데이터 생성"""
        # 좌표를 문자열 키로 변환 (JSON 직렬화를 위해)
        items_str_keys = {f"{x},{y}": item for (x, y), item in self.items.items()}
        walls_str_keys = {f"{x},{y}": wall_type for (x, y), wall_type in self.walls.items()}
        
        return {
            "height": self.height,
            "width": self.width,
            "items": items_str_keys,
            "walls": walls_str_keys,
            "mobs": self.mobs.copy(),
            "characters": self.characters.copy()
        }