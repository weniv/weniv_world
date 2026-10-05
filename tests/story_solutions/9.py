def delivery():
    turn_left()
    turn_left()
    turn_left()
    steps = 0
    while not on_item():
        move()
        steps += 1
    count = 0
    while on_item():
        pick()
        count += 1
    turn_left()
    turn_left()
    repeat(steps, move)
    say(f'배송 {count}개 완료')
    turn_left()
    turn_left()
    turn_left()
    if front_is_clear():
        move()
repeat(5, delivery)
