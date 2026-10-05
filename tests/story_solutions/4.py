for _ in range(3):
    move()
    pick_all()
price = {'fish-1': 1000, 'fish-2': 2000, 'fish-3': 3000}
total = 0
print('종류    마리    가격    합')
for name in ['fish-1', 'fish-2', 'fish-3']:
    count = item()[name]
    total += count * price[name]
    print(name, count, price[name], count * price[name], sep='    ')
print('총 합', total)
