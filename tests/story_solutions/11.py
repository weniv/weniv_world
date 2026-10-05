for x, y in [(0, 1), (1, 1), (1, 0), (2, 0), (2, 1), (3, 4), (4, 2)]:
    goto(x, y)
    pick_all()
goto(4, 4)
print(item()['diamond'])
