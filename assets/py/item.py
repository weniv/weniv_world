import js
from coordinate import item_data

class Item:
    def __init__(self, x, y, name, description={}, count=0):
        self.name = name
        self.description = description
        self.count = count
        self.x = x
        self.y = y
        self.img = f'assets/img/item/{name}.png'

    def draw(self):
        '''
        x좌표, y좌표에 item을 생성하는 함수
        '''
        item = js.document.createElement('img')
        item.setAttribute('class', 'item')
        item.classList.add(f'{self.name}')
        # character.style.width = f'{self.width}px'
        item.setAttribute('src', self.img)
        item.style.position = 'absolute'
        item.style.top = f'{self.y * 100 + 25}px'
        item.style.left = f'{self.x * 100 + 25}px'
        item_data.append({
            'item': self.name,
            'x': self.x,
            'y': self.y
        })
        return item

    def get_count(self):
        return self.count
    
    def set_count(self, count):
        self.count = count

    def set_map(self, x, y):
        self.x = x
        self.y = y