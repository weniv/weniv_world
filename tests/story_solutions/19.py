# {basic_code}
# 위 줄은 노트북에 처음 들어가는 기본 코드(worlds.json의 basic_code)로 바뀝니다.
for 야채 in required_ingredient:
    required[required_ingredient.index(야채)] = any(
        i['name'] == 야채 and i['freshness'] >= required_freshness for i in items
    )
print(all(required))
