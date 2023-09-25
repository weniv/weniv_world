from built_in_functions import (
    move,
    turn_left,
    front_is_clear,
    left_is_clear,
)


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
        if not left_is_clear():
            turn_left()


def jump():
    turn_left()
    move()
    turn_right()
    move()
    move()
    turn_right()
    move()
    turn_left()
