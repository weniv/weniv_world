for x, y in [(0, 1), (0, 3), (2, 4), (4, 1), (4, 0), (2, 0)]:
    goto(x, y)
    pick_all()
goto(0, 0)
print(f"라이캣은 물고기 {item()['fish-1']}마리를 잡았다!")
