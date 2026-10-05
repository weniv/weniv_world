items = [['당근', 3], ['사과', 5], ['당근', 6], ['포도', 4], ['당근', 7]]
print([item for item in items if item[0] == '당근' and item[1] >= 5])
