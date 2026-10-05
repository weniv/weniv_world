import math

# 한 줄의 오른쪽 끝(4번 칸)이 일의 자리입니다.
l = []
for row in range(5):
    number = 0
    for col in range(5):
        if (row, col) in item_data:
            goto(row, col)
            number += pick_all() * 10 ** (4 - col)
    l.append(number)
print(math.ceil(sum(l) * 10 / 100))
