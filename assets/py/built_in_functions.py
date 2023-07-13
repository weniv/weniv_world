import js
from coordinate import character_data
from item import Item

def print(*args):
    '''
    html 문서 내 출력
    '''
    output = js.document.getElementById('output')
    result = ''
    for arg in args:
        result += str(arg) + '\n'
    result = output.value + result
    output.value = result

def set_item(x, y, name, count=1, description={}):
    item = Item(x, y, name, count, description)
    draw_item = item.draw()
    js.document.querySelector('.map-container').appendChild(draw_item)

def move(character=None):
    if character != None:
        character.move()
    else:
        if character_data[0]['character_obj'] != None:
            character_data[0]['character_obj'].move()
        else:
            print('캐릭터가 없습니다.')

def turn_left(character=None):
    if character != None:
        character.turn_left()
    else:
        if character_data[0]['character_obj'] != None:
            character_data[0]['character_obj'].turn_left()
        else:
            print('캐릭터가 없습니다.')

def pick(character=None):
    if character != None:
        character.pick()
    else:
        if character_data[0]['character_obj'] != None:
            character_data[0]['character_obj'].pick()
        else:
            print('캐릭터가 없습니다.')

def put(character=None):
    if character != None:
        character.put()
    else:
        if character_data[0]['character_obj'] != None:
            character_data[0]['character_obj'].put()
        else:
            print('캐릭터가 없습니다.')

def repeat(count, f):
    for i in range(0, count):
        f()

def front_is_clear():
    pass

def left_is_clear():
    pass