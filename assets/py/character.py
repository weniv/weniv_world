import js
from coordinate import character_data, map_data, running_speed

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
        character.classList.add(f'{self.name}')
        character.style.width = f'{self.width}px'
        character.style.transition = f'all {running_speed}s'
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
    
    def set_speed(self, speed):
        c = js.document.querySelector(f'.{self.name}')
        c.style.transition = f'all {speed}s'

    # TODO: 경로를 dict에 저장해놓고, dict에 따라 keyframes animation을 만드는 작업 필요. 애니메이션이 한 번에 움직이기 때문.
    def move(self):
        c = js.document.querySelector(f'.{self.name}')
        if character_data[0]['direction'] == 0:
            if character_data[0]['x'] >= map_data['width']-1:
                js.alert('맵을 벗어납니다.')
                return
            c.style.left = f'{character_data[0]["x"] * 100 + 125}px'
            # c.style.transform = f'translateX({character_data[0]["x"] * 100 + 125}px)'
            character_data[0]["x"] += 1
        elif character_data[0]['direction'] == 1:
            if character_data[0]['y'] <= 0:
                js.alert('맵을 벗어납니다.')
                return
            c.style.top = f'{character_data[0]["y"] * 100 - 125}px'
            # c.style.transform = f'translateY({character_data[0]["y"] * 100 - 125}px)'
            character_data[0]["y"] -= 1
        elif character_data[0]['direction'] == 2:
            if character_data[0]['x'] <= 0:
                js.alert('맵을 벗어납니다.')
                return
            c.style.left = f'{character_data[0]["x"] * 100 - 125}px'
            # c.style.transform = f'translateX({character_data[0]["x"] * 100 - 125}px)'
            character_data[0]["x"] -= 1
        elif character_data[0]['direction'] == 3:
            if character_data[0]['y'] >= map_data['height']-1:
                js.alert('맵을 벗어납니다.')
                return
            c.style.top = f'{character_data[0]["y"] * 100 + 125}px'
            # c.style.transform = f'translateY({character_data[0]["y"] * 100 + 125}px)'
            character_data[0]["y"] += 1

    def turn_left(self):
        c = js.document.querySelector(f'.{self.name}')
        if character_data[0]['direction'] == 0:
            c.style.transform = 'rotate(-90deg)'
            character_data[0]['direction'] += 1
        elif character_data[0]['direction'] == 1:
            c.style.transform = 'rotate(-180deg)'
            character_data[0]['direction'] += 1
        elif character_data[0]['direction'] == 2:
            c.style.transform = 'rotate(-270deg)'
            character_data[0]['direction'] += 1
        elif character_data[0]['direction'] == 3:
            c.style.transform = 'rotate(0deg)'
            character_data[0]['direction'] = 0    

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
        