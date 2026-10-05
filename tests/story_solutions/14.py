crew_info = [
    ('자바독', 95, '메모'),
    ('개리', 85, '메모'),
    ('소울곰', 1, '메모'),
]
crew = list(map(lambda c: dict(zip(['이름', '코딩 능력치', '메모'], c)), crew_info))
print(list(map(lambda c: c['이름'], crew)))
