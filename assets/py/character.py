import js
from coordinate import character_data

class Character:
    def __init__(self, x, y, name, width=100, height=100, initHp=100, dropRate=0.1, power=10):
        self.x = x
        self.y = y
        self.name = name
        self.width = width
        self.height = height
        self.initHp = initHp
        self.dropRate = dropRate
        self.power = power
        self.hp = initHp
        self.img = f'assets/img/characters/{name}.png'

    def draw(self):
        '''
        x좌표, y좌표에 character를 생성하는 함수
        '''
        character = js.document.createElement('img')
        character.setAttribute('class', 'character')
        character.setAttribute('style', f'width: {self.width}px;')
        character.setAttribute('src', self.img)
        character.style.position = 'absolute'
        character.style.top = f'{self.y * 100 + 25}px'
        character.style.left = f'{self.x * 100 + 25}px'
        finder = False
        for c in character_data:
            if c['character'] == self.name:
                c['x'] = self.x
                c['y'] = self.y
                finder = True
        if not finder:
            character_data.append({
                'character': self.name,
                'x': self.x,
                'y': self.y
            })
        return character

    def move(self):
        pass

    def turn_left(self):
        pass    

    def pick(self):
            pass

    def put(item_name='beeper'):
        pass

    def check_bottom(self):
        pass

    def show_item(self):
        pass
    
    def front_is_clear(self):
        pass

    def left_is_clear(self):
        pass

    def right_is_clear(self):
        pass

    def back_is_clear(self):
        pass

    def direction(self):
        pass
        