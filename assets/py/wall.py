import js
from coordinate import map_data

class Wall:
    def __init__(self, wall_data):
        self.wall_data=wall_data
        self.movableType=['door']
        
    def drawWall(self):
        container = js.document.createElement('div')
        container.setAttribute('class', 'wall-container')
        
        for type in self.wall_data.keys():
          for (x,y) in self.wall_data[type]:
            # js.console.log(x, y)
            if (x<0 or x>2*map_data["width"] or y<0 or y>2*map_data["height"]):
              continue
            cx, cy = self._wall_to_pos(x,y)
            wall = js.document.createElement('div')
            wall.setAttribute('class','wall')
            if(x%2):
              # 가로
              wall.classList.add('landscape')
              wall.style.left=f'{(x-1)*51}px'
              wall.style.top=f'{(2*map_data["height"]-y)*51}px'
              
            else:
              wall.classList.add('portrait')
              wall.style.left=f'{x*51}px'
              wall.style.top=f'{(2*map_data["height"]-y-1)*51}px'
              
            if (type in self.movableType):
              wall.classList.add('movable')

            container.appendChild(wall)

        return container
         
    def _wall_to_pos(self, x,y):
        # 벽을 놓을 수 있는 좌표계를 position 좌표계로 변환
        return (x-1)/2, map_data['height']-(y-1)/2
    