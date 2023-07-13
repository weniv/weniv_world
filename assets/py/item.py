import js
from coordinate import item_data

class Item:
    def __init__(self, x, y, name, count=1, description={}):
        self.name = name
        self.count = count
        self.description = description
        self.x = x
        self.y = y
        self.img = f'assets/img/item/{name}.png'

    # TODO: 해당 좌표에 동일 아이템이 있으면 count만 증가시키고 아이템은 삭제하고 넣어야 함
    # TODO: 해당 좌표에 다른 아이템이 있으면 삭제하고 넣어야 함
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
        item.style.top = f'{self.y * 100 + 50}px'
        item.style.left = f'{self.x * 100 + 50}px'
        item_data[(self.x, self.y)] = {
            'item': self.name,
            'count': self.count
        }
        js.document.querySelector('.map-container').appendChild(item)
        self.draw_count()
    
    # TODO: 해당 좌표에 이미 텍스트가 있으면 지우고 넣어야 함
    def draw_count(self):
        '''
        x좌표, y좌표 item에 상단 오른쪽 개수를 생성하는 함수
        '''
        count = js.document.createElement('div')
        count.setAttribute('class', 'count')
        count.classList.add(f'{self.name}')
        count.style.position = 'absolute'
        count.style.top = f'{self.y * 100 + 25}px'
        count.style.left = f'{self.x * 100 + 75}px'
        count.style.display = 'flex'
        count.style.justifyContent = 'center'
        count.style.alignItems = 'center'
        count.style.border = '1px solid black'
        if self.count < 9:
            count.style.width = '18px'
            count.style.height = '18px'
        elif self.count < 99:
            count.style.width = '20px'
            count.style.height = '20px'
        elif self.count < 999:
            count.style.width = '22px'
            count.style.height = '22px'
        else:
            count.style.width = '24px'
            count.style.height = '24px'
        count.style.borderRadius = '50%'
        count.style.fontSize = '10px'
        count.innerHTML = f'{self.count}'
        js.document.querySelector('.map-container').appendChild(count)

    def get_count(self):
        return self.count
    
    def set_count(self, count):
        self.count = count

    def set_map(self, x, y):
        self.x = x
        self.y = y