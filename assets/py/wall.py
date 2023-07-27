import js
from coordinate import map_data, map_size

class Wall:
    def __init__(self, wall_data):
        self.wall_data=wall_data
        self.movableType=['door']
        
        # 벽의 정보를 담는 컨테이너
        container = js.document.createElement('div')
        container.setAttribute('class', 'wall-container')
        self.container = container
      
    def drawWall(self):
        # 초기 wall_data를 출력하는 함수
        container = self.container
        js.console.log(container)
        for type in self.wall_data.keys():
          for (x,y) in self.wall_data[type]:
            
            if (x<0 or x>2*map_data["width"] or y<0 or y>2*map_data["height"]):
              continue
            self.addWall(type,(x,y))
            
    def addWall(self,type, pos):
      x, y = pos
      js.console.log('addWall: ',x,y)
      
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

      self.container.appendChild(wall)
      
    def resetWall(self):
        self.container.replaceChildren()
        self.wall_data={'wall': [], 'door': []}
        self.drawWall()
          
          
            