import js
from coordinate import map_data, map_size, border_size

class Wall:
    def __init__(self, wall_data):
        self.wall_data=wall_data
        
        # 벽의 정보를 담는 컨테이너
        container = js.document.createElement('div')
        container.setAttribute('class', 'wall-container')
        self.container = container
      
    def drawWall(self):
        # 초기 wall_data를 출력하는 함수
        container = self.container
        for type in self.wall_data.keys():
          for (x,y) in self.wall_data[type]:
            
            if (x<0 or x>2*map_data["width"] or y<0 or y>2*map_data["height"]):
              continue
            self.addWall(type,(x,y))
            
    def addWall(self,type, pos):
      x, y = pos
      
      # 상자 기준 크기
      box_size = map_size+border_size*2
      
      wall = js.document.createElement('div')
      wall.setAttribute('class','wall')
      
      if (isinstance(x, int)): # 세로
        wall.setAttribute('data-direction','portrait')
      else: # 가로
        wall.setAttribute('data-direction','landscape')
      
      wall.style.top=f'{(x+0.5)*box_size}px'
      wall.style.left=f'{(y+0.5)*box_size+1}px'
      
      wall.setAttribute('data-type',type)
      self.container.appendChild(wall)

         
    def resetWall(self):
        self.container.innerHTML=""
        self.wall_data={'wall': [], 'door': [], 'fence':[]}
        self.drawWall()
          
          
            