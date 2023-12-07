import js
from js import setTimeout
from pyodide.ffi import create_once_callable
from built_in_functions import (
    move,
    turn_left,
    front_is_clear,
    left_is_clear,
)
from error import alert_error
from coordinate import character_data

def turn_right():
    turn_left()
    turn_left()
    turn_left()


def turn_around():
    turn_left()
    turn_left()


def move_to_wall():
    while front_is_clear():
        move()


def turn_left_until_clear():
    for i in range(4):
        if not front_is_clear():
            turn_left()
        else:
            return
    alert_error("사방이 막혀있습니다.")
    


# jump 함수 관련 로직
def jump(character=None):
    if character != None:
        setTimeout(create_once_callable(lambda: _jump(character)), character.running_time)
        setTimeout(create_once_callable(lambda:character.init_time()), character.running_time)
        
    else:
        if character_data[0]["character_obj"] != None:
            character = character_data[0]["character_obj"]
            setTimeout(create_once_callable(lambda: _jump(character)), character.running_time)
            setTimeout(create_once_callable(lambda:character.init_time()), character.running_time)
        else:
            print("캐릭터가 없습니다.")

def _jump(ch):
    x, y = ch._get_character_data('x'), ch._get_character_data('y')
    directions = ch._get_character_data('directions')
    
    fx, fy = x, y # 바로 앞
    nx, ny = x, y # 도착 지점
    
    if directions == 0:
        fy += 1
        ny += 2
    elif directions == 1:
        fx -= 1
        nx -= 2
    elif directions == 2:
        fy -= 1
        ny -= 2
    elif directions == 3:
        fx += 1
        nx += 2
        
    js.console.log(f"nx: {nx}, ny: {ny}")
    
    error_check = None
    if ch._out_of_world(nx, ny):
        error_check = "OutOfWorld"
    elif ch._obstacle_exist(nx, ny):
        error_check = "ObstacleExist"
    
    if error_check:
        setTimeout(create_once_callable(lambda: alert_error(error_check)), ch.running_time)
        setTimeout(create_once_callable(lambda: ch.init_time()), ch.running_time)
    else: 
        setTimeout(create_once_callable(lambda: (ch._move_animation(fx, fy, directions))), ch.running_time)
        setTimeout(create_once_callable(lambda: ch.init_time()), ch.running_time)
        
        setTimeout(create_once_callable(lambda: _scale(ch, 'up')), ch.running_time)
        setTimeout(create_once_callable(lambda: ch.init_time()), ch.running_time)
        
        setTimeout(create_once_callable(lambda: (ch._move_animation(fx, fy, directions))), ch.running_time)
        setTimeout(create_once_callable(lambda: ch.init_time()), ch.running_time)
        
        setTimeout(create_once_callable(lambda: _scale(ch, 'down')), ch.running_time)
        setTimeout(create_once_callable(lambda: ch.init_time()), ch.running_time)
        
        ch.x = nx
        ch.y = ny
        ch._set_character_data('x', nx)
        ch._set_character_data('y', ny)
        
        
def _scale(ch, type):
    name = ch._get_character_data('character')
    c = js.document.querySelector(f".{name}")
    
    if type=='up':
        c.style.scale = "1.2"
    elif type=='down':
        c.style.scale = "1"