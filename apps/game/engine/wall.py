"""
Django 환경에 맞게 변환된 벽 클래스
"""
from typing import Dict, Any

class Wall:
    def __init__(self, x: float, y: float, wall_type: str = "wall"):
        self.x = x
        self.y = y
        self.wall_type = wall_type  # "wall", "fence", "door" 등
    
    def get_state(self) -> Dict[str, Any]:
        """벽 상태 반환"""
        return {
            'x': self.x,
            'y': self.y,
            'type': self.wall_type,
            'image_url': f"assets/img/wall/{self.wall_type}.png"
        }
    
    def is_passable(self) -> bool:
        """통과 가능한지 확인"""
        return self.wall_type not in ["wall", "fence", "door"]
    
    def open_door(self) -> bool:
        """문 열기 (문인 경우만)"""
        if self.wall_type == "door":
            self.wall_type = ""  # 문을 열어서 빈 공간으로 만듦
            return True
        return False