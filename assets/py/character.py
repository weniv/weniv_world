import js
from item import Item
from coordinate import character_data, map_data, running_speed, item_data
from js import alert, setTimeout, clearTimeout
from pyodide.ffi import create_once_callable

class Character:
    def __init__(self, x, y, name, directions=0, width=100, height=33, initHp=100, dropRate=0.1, power=10):
        self.x = x
        self.y = y
        self.name = name
        self.directions = directions
        self.width = width
        self.height = height
        self.initHp = initHp
        self.dropRate = dropRate
        self.power = power
        self.hp = initHp
        self.img = f'assets/img/characters/{name}.png'
        self.running_time = 0

    def draw(self):
        '''
        x좌표, y좌표에 character를 생성하는 함수
        '''
        character = js.document.createElement('div')
        character.setAttribute('class', 'character')
        character.classList.add(f'{self.name}')
        character.style.width = f'{self.width}px'
        character.style.height = f'{self.height}px'
        character.style.backgroundImage = f'url("{self.img}")'
        character.style.backgroundRepeat = 'no-repeat'
        # next value(px) : (-1, -3), (-33, -1), (-65, -2), (-97, -3), (-129, -2), (-161, -1), (-193, -2)
        character.style.backgroundPosition = '-1px -3px'
        character.style.transition = f'all {running_speed}s'
        character.style.position = 'absolute'
        character.style.top = f'{self.y * 100 + 40}px'
        character.style.left = f'{self.x * 100 + 40}px'
        finder = False
        for c in character_data:
            if c['character'] == self.name:
                c['x'] = self.x
                c['y'] = self.y
                c['directions'] = self.directions
                c['items'] = {}
                finder = True
        if not finder:
            character_data.append({
                'character': self.name,
                'x': self.x,
                'y': self.y,
                'directions': self.directions,
                'items': {}
            })
        return character
    
    def set_speed(self, speed):
        c = js.document.querySelector(f'.{self.name}')
        c.style.transition = f'all {speed}s'

    # TODO: 경로를 dict에 저장해놓고, dict에 따라 keyframes animation을 만드는 작업 필요. 애니메이션이 한 번에 움직이기 때문.
    def move(self):
        self.running_time += 1000 * running_speed
        setTimeout(
            create_once_callable(
                lambda: (
                    self._move()
                )
            ),
            self.running_time
        )
        setTimeout(
            create_once_callable(
                lambda: self.init_time()
            ),
            self.running_time
        )

    def _move(self):
        c = js.document.querySelector(f'.{self.name}')
        directions = character_data[0]['directions']
        
        x = character_data[0]['x']
        y = character_data[0]['y']
        
        if directions == 0:
            if x >= map_data['width']-1:
                js.alert('맵을 벗어납니다.')
                return
            c.style.left = f'{(x + 1) * 100 + 40}px'
            # c.style.transform = f'translateX({character_data[0]["x"] * 100 + 125}px)'
            character_data[0]["x"] += 1
        elif directions == 1:
            if y <= 0:
                js.alert('맵을 벗어납니다.')
                return
            c.style.top = f'{(y - 1) * 100 - 40}px'
            # c.style.transform = f'translateY({character_data[0]["y"] * 100 - 125}px)'
            character_data[0]["y"] -= 1
        elif directions == 2:
            if x <= 0:
                js.alert('맵을 벗어납니다.')
                return
            c.style.left = f'{(x - 1) * 100 - 40}px'
            # c.style.transform = f'translateX({character_data[0]["x"] * 100 - 125}px)'
            character_data[0]["x"] -= 1
        elif directions == 3:
            if y >= map_data['height'] - 1:
                js.alert('맵을 벗어납니다.')
                return
            c.style.top = f'{(y + 1) * 100 + 40}px'
            # c.style.transform = f'translateY({character_data[0]["y"] * 100 + 125}px)'
            character_data[0]["y"] += 1

    def turn_left(self):
        self.running_time += 1000 * running_speed
        setTimeout(
            create_once_callable(
                lambda: (
                    self._turn_left()
                )
            ),
            self.running_time
        )
        setTimeout(
            create_once_callable(
                lambda: self.init_time()
            ),
            self.running_time
        )

    def _turn_left(self):
        c = js.document.querySelector(f'.{self.name}')
        directions = character_data[0]['directions']
        
        if directions == 0:
            c.style.transform = 'rotate(-90deg)'
            character_data[0]['directions'] += 1
        elif directions == 1:
            c.style.transform = 'rotate(-180deg)'
            character_data[0]['directions'] += 1
        elif directions == 2:
            c.style.transform = 'rotate(-270deg)'
            character_data[0]['directions'] += 1
        elif directions == 3:
            c.style.transform = 'rotate(0deg)'
            character_data[0]['directions'] = 0    

    def pick(self):
        '''
        발 아래 아이템을 주워서 아이템을 가지고 있는지 확인하고, 
        가지고 있으면 주인공이 소유한 아이템 개수를 1 증가시키고, 맵에 있는 아이템은 1 감소시킨다.

        모든 아이템이 다 감소되면 document에서 해당 아이템을 삭제한다.
        '''
        x = character_data[0]['x']
        y = character_data[0]['y']
        
        item = item_data.get((x, y))
        
        if item:
            item_count = item.get('count', 0)
            item_count -= 1
            item['count'] = item_count
            item_data[(x, y)] = item
            # TODO: 0번째에서 꺼내는 것이 아니라 자신의 아이템에서 꺼내야 함.
            if item['item'] in character_data[0]['items'].keys():
                character_data[0]['items'][item['item']] += 1
            else:
                character_data[0]['items'][item['item']] = 1
            if item_count == 0:
                js.document.querySelector(f'.{item["item"]}').remove()
                item_data.pop((x, y))
            return item_count
        else:
            return '발 아래 아이템이 없습니다!'

    def put(self, item_name='fish'):
        '''
        주인공 발 아래 아이템을 내려놓는 함수
        '''
        x = character_data[0]['x']
        y = character_data[0]['y']
        
        item = item_data.get((x, y))

        # 주인공에게 발 아래 아이템이 있다면
        if item:
            # 주인공 발 아래 아이템과 동일한 아이템이 있다면
            # TODO: 0번째에서 가져오는 것이 아니라 자신의 아이템을 찾아 가져와야 함.
            if character_data[0]['items'].get(item_name, 0) > 0:
                if item['items'] == item_name:
                    item_count = item.get('count', 0)
                    if item_count > 0:
                        item_count += 1
                        item['count'] = item_count
                        item_data[(x, y)] = item
                        return item_count
                else:
                    return '다른 아이템이 있습니다!'
            else:
                return '동일한 종류의 아이템이 없습니다!'
        # 주인공에게 발 아래 아이템이 없다면
        else:
            # TODO: 0번째에서 가져오는 것이 아니라 자신의 아이템을 찾아 가져와야 함.
            if character_data[0]['items'].get(item_name, 0) > 0:
                item = Item(x, y, item_name, 1)
                draw_item = item.draw()
                js.document.querySelector('.map-container').appendChild(draw_item)
            else:
                return '가진 아이템이 없습니다.'


    def check_bottom(self):
        '''
        주인공 발 아래 아이템이 있는지 확인하는 함수
        '''
        x = character_data[0]['x']
        y = character_data[0]['y']
        
        item = item_data.get((x, y))

        if item:
            return True
        else:
            return False

    def show_item_global(self):
        '''
        현재 맵에 있는 모든 아이템을 보여주는 함수
        '''
        carried_items = []
        for item in item_data.values():
            carried_items.append(item['item'])
        return carried_items
    
    def show_item(self):
        '''
        주인공이 가지고 있는 아이템을 보여주는 함수
        '''
        return None
    
    def front_is_clear(self):
        pass

    def left_is_clear(self):
        pass

    def right_is_clear(self):
        pass

    def back_is_clear(self):
        pass

    def directions(self):
        pass
        
    def init_time(self):
        self.running_time = 0