class Treasure:
    names = {'gold': '금괴', 'diamond': '보석'}

    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

    def __str__(self):
        return f'{self.names[self.name]} {self.quantity}개'

    def get_item(self):
        self.quantity += 1

gold = Treasure('gold', 0)
diamond = Treasure('diamond', 0)
for x, y in sorted(item_data):
    goto(x, y)
    while on_item():
        name = item_data[(x, y)]['item']
        pick()
        (gold if name == 'goldbar' else diamond).get_item()
goto(1, 0)

treasure_list = [gold, diamond]
for treasure in treasure_list:
    print(treasure)
