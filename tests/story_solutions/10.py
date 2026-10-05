d = {'골드바': 0, '물고기': 0}
for x, y in [(0, 1), (1, 1), (1, 0), (2, 0), (2, 1), (3, 1), (3, 0), (4, 0), (4, 1)]:
    goto(x, y)
    while on_item():
        name = item_data[(x, y)]['item']
        pick()
        if name == 'goldbar':
            d['골드바'] += 1
        else:
            d['물고기'] += 1
print(f"골드바는 {d['골드바']}개 있습니다. 물고기는 {d['물고기']}마리 있습니다.")
