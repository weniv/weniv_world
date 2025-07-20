"""
Django 환경에 맞게 변환된 아이템 클래스
"""
from typing import Dict, Any, Optional

class Item:
    def __init__(self, x: int, y: int, item_name: str, count: int = 1):
        self.x = x
        self.y = y
        self.item_name = item_name
        self.count = count
        self.image_url = f"assets/img/item/{item_name}.png"
    
    def get_state(self) -> Dict[str, Any]:
        """아이템 상태 반환"""
        return {
            'x': self.x,
            'y': self.y,
            'item': self.item_name,
            'count': self.count,
            'image_url': self.image_url
        }
    
    def decrease_count(self, amount: int = 1) -> bool:
        """아이템 개수 감소"""
        if self.count >= amount:
            self.count -= amount
            return True
        return False
    
    def increase_count(self, amount: int = 1):
        """아이템 개수 증가"""
        self.count += amount
    
    def is_empty(self) -> bool:
        """아이템이 모두 소모되었는지 확인"""
        return self.count <= 0