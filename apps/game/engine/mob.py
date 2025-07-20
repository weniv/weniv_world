"""
Django 환경에 맞게 변환된 몹 클래스
"""
from typing import Dict, Any

class Mob:
    def __init__(self, x: int, y: int, name: str, hp: int = 100, mp: int = 50):
        self.x = x
        self.y = y
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.mp = mp
        self.max_mp = mp
        self.image_url = f"assets/img/mob/{name}.png"
    
    def get_state(self) -> Dict[str, Any]:
        """몹 상태 반환"""
        return {
            'x': self.x,
            'y': self.y,
            'name': self.name,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'mp': self.mp,
            'max_mp': self.max_mp,
            'image_url': self.image_url,
            'is_alive': self.hp > 0
        }
    
    def take_damage(self, damage: int) -> Dict[str, Any]:
        """데미지 받기"""
        old_hp = self.hp
        self.hp = max(0, self.hp - damage)
        
        return {
            'damage': damage,
            'hp': {'old': old_hp, 'new': self.hp},
            'is_alive': self.hp > 0,
            'animation': {
                'type': 'damage',
                'damage': damage
            }
        }
    
    def heal(self, amount: int) -> Dict[str, Any]:
        """치료"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        
        return {
            'heal': amount,
            'hp': {'old': old_hp, 'new': self.hp}
        }
    
    def is_alive(self) -> bool:
        """생존 여부 확인"""
        return self.hp > 0
    
    def move_to(self, x: int, y: int):
        """위치 이동"""
        self.x = x
        self.y = y