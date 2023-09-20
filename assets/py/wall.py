import js
from coordinate import map_data, map_size, border_size, wall_type
         
class Wall:
    def __init__(self):
      self.width = map_data['width']
      self.height = map_data['height']
      self.wall_data = {}
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
          
      wall_data[(0, 0.5)] = 'wall'
      wall_data[(0, 1.5)] = 'door'
      wall_data[(0, 2.5)] = 'fence'
      self.wall_data = wall_data
      
      
    def drawWall(self):
      box_size = map_size + border_size*2
      container = js.document.createElement('div')
      container.setAttribute('class', 'wall-container')
      
      for (x, y) in self.wall_data.keys():
        wall = js.document.createElement('div')
        wall.setAttribute('class', 'wall')
        wall.setAttribute('data-type', self.wall_data[(x,y)])
        wall.setAttribute('data-X',x)
        wall.setAttribute('data-Y',y)
        wall.style.top=f'{(x+0.5)*box_size}px'
        wall.style.left=f'{(y+0.5)*box_size+1}px'
        if(int(x)==x):
            wall.setAttribute('data-direction', 'portrait')
        else:
            wall.setAttribute('data-direction', 'landscape')
        container.appendChild(wall)
        
        
      return container
    
    def changeWallType(self, event):
      # 이벤트가 발생한 DOM 요소에 dataset_type을 추가
      if(wall_type == 'delete'):
        event.target.setAttribute('data-type', '')
      else:
        event.target.setAttribute('data-type', wall_type)
      
    def deleteActivate(self, event):
      if(event.target.getAttribute('data-type') and wall_type == 'delete'):
        event.target.style.outline = '1px solid red'
        
        
    def resizeWall(self):
      '''
      map의 크기가 변경될 때, wall_data를 갱신합니다.
      '''
      pass
      
      
