goto(0, 1)
pick_all()
goto(0, 2)
pick_all()
if item()['fish-1'] >= 10 and item()['goldbar'] >= 10:
    goto(1, 4)
    put('fish-1')
    say('오늘은 밥차를 운영합니다!')
else:
    goto(1, 4)
    say('오늘은 밥차를 운영하지 않습니다!')
