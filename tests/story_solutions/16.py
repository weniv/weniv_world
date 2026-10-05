character = ['라이캣', '개리', '자바독', '빙키', '뮤라', '소울곰', '대리인 No.1']
stone = ['피스 스톤', '스페이스 스톤', '마인드 스톤', '리얼리티 스톤', '타임 스톤', '소울 스톤', '파워 스톤']
for i, (who, what) in enumerate(zip(character, stone), 1):
    print(f'{i}. {who} : {what}')
