for x, y in sorted(item_data):
    goto(x, y)
    pick_all()
print(sorted(item().items(), key=lambda x: x[1], reverse=True))
