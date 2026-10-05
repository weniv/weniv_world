potion_counts = [0, 0, 0, 0]
for i, (x, y) in enumerate([(1, 1), (3, 1), (3, 2), (2, 4)]):
    goto(x, y)
    potion_counts[i] = pick_all()
say(sum(filter(lambda x: 3 < x < 6, potion_counts)))
