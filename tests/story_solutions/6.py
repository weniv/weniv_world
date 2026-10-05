days = ['월', '화', '수', '목', '금']
sales = []
for i in range(5):
    if i:
        move()
    before = dict(item())
    pick_all()
    gold = item().get('goldbar', 0) - before.get('goldbar', 0)
    fish = item().get('fish-3', 0) - before.get('fish-3', 0)
    sales.append(gold * 100000 + fish * 3000)
print(f'가장 적은 금액: {min(sales)}')
print(f'이벤트 요일: {days[sales.index(max(sales))]}요일')
print(f'쉬는 날: {days[sales.index(min(sales))]}요일')
