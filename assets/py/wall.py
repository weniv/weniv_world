import js
from coordinate import map_data, map_size, border_size, wall_type
         
class Wall:
    def __init__(self):
      self.width = map_data['width']
      self.height = map_data['height']
      self.wall_data = {(0,0.5):'wall', (0, 1.5):'',(3,0.5):'fence'}
      self.initWallDate()
    
      
          
    def initWallDate(self):
      wall_data = {}
      
      x = 0
      while x <= self.height - 1:
          if x == int(x):  # x가 정수일 때
              y = 0.5
              while y <= self.width - 1:
                  wall_data[(x, y)]=''
                  y += 1
          else:  # x가 정수가 아닐 때
              y = 0
              while y <= self.width - 1:
                  wall_data[(x, y)]=''
                  y += 1
          x += 0.5
          
      self.wall_data = wall_data
      print(f'wall_data: {self.wall_data}')
      
      
    def drawWall(self):
      box_size = map_size + border_size*2
      container = js.document.createElement('div')
      container.setAttribute('class', 'wall-container')
      
      for (x, y) in self.wall_data.keys():
        wall = js.document.createElement('div')
        wall.setAttribute('class', 'wall')
        wall.setAttribute('data-type', self.wall_data[(x,y)])
        wall.style.top=f'{(x+0.5)*box_size}px'
        wall.style.left=f'{(y+0.5)*box_size+1}px'
        if(int(x)==x):
            print('portrait', x, y,)  
            wall.setAttribute('data-direction', 'portrait')
        else:
            print('landscape',x,y)
            wall.setAttribute('data-direction', 'landscape')
        container.appendChild(wall)
      return container
          
    def resizeWall(self):
      '''
      map의 크기가 변경될 때, wall_data를 갱신합니다.
      '''
      pass
      
      
