# 부족의 마음 사로잡기!

## 부족의 마음 사로잡기! `컴프리헨션` `삼항 연산자` `람다 함수` `JSON`

자바독은 라이캣과 만난 고향으로 돌아왔습니다. 그는 각 부족 믿음직한 친구들에게 전서를 보내어, 라이언에게 강제로 동원되어 험난한 작업에 시달리던 특급 기술자들을 자신의 집으로 한 분씩 초대했습니다.

마인드 스톤은 자바독에게 마음을 연결하여 진심을 느끼고, 진심을 전달할 수 있는 능력을 부여했습니다. 초대된 특급기술자와 대화에서 일상의 회복을 갈망하는 마음, 가족과의 소중한 시간을 되찾고자 하는 욕구, 평화로운 주말을 꿈꾸는 감정들이 느껴졌습니다.

자바독은 이들을 위해 마음을 다해 저녁식사를 준비했습니다. 진심이 담긴 대접으로 서서히 그들의 마음의 문이 열리기 시작했습니다. 하지만 단박에 모든 것이 해결될 수는 없었고, 그래서도 안 되었습니다. 자바독은 인내심을 갖고, 마을을 조금씩 변화시키기 시작했습니다.

이러한 노력 끝에, 많은 사람들이 자바독의 진심을 알게 되었고, 진실을 마주할 용기와 변화를 이끌어내는 의지를 얻었습니다.

> "재촉과 성냄없는 프로젝트, 가족과의 저녁식사, 주말이 있는 삶, 우리의 소망은 그리 크지 않다독. 그러나 보라 독. 이 작은 소망조차 이루기 힘든 사회에서, 이 작은 소망을 위해 행동하지 않는다면 30년, 50년 후에 어떤 모습일지!"

자바독은 마인드 스톤을 통해 마음을 전하며, 그들에게 새로운 비전을 제시했습니다. 기술자들의 마음은 움직이기 시작했습니다.

![설득하는 자바독](19.webp)

> "우리의 미래가 아니라, 우리 자녀들의 미래를 위해서!" 

자바독의 진심은 마을 사람들에게 깊은 울림을 주었고, 변화를 만들어 냈습니다.

### 임무
주어진 JSON 형태의 데이터에서 각 재료의 신선도와 개수를 기반으로 특정 요리를 할 수 있는지 판단하세요. 이 임무는 JSON 데이터의 이해, 데이터 추출 및 조건에 따른 처리, 그리고 `any`와 `all` 함수를 사용해주세요. 특정 요리에 필요한 재료의 신선도와 개수가 충분한지를 판단하여 True 또는 False로 결과를 터미널에 출력합니다.

### 기본 데이터
```python
# 요리에 필요한 재료의 조건 확인
required_ingredient = ["당근", "양상추", "양파", "방울토마토"]
required_freshness = 5
# 당근, 양상추, 양파, 방울토마토가 조건에 만족하는 것이 있는지 확인하는 리스트
required = [False, False, False, False]

items = [
    {"name": "당근", "freshness": 7},
    {"name": "사과", "freshness": 5},
    {"name": "당근", "freshness": 6},
    {"name": "포도", "freshness": 4},
    {"name": "당근", "freshness": 8},
    {"name": "양상추", "freshness": 8},
    {"name": "양파", "freshness": 5},
    {"name": "방울토마토", "freshness": 5},
]
```

### 목표 요리 및 필요 재료
- 요리: 신선한 당근 샐러드
- 필요 재료: 신선도 5 이상인 당근, 양상추, 양파, 방울토마토

### 결과값
```python
True 또는 False
```

## 사용 코드
아래 제시된 코드를 활용하여 문제를 해결해 주세요.

```python
filter()
all()
any()
sum()
and
or
[item for item in items]
result = 'hello' if True else 'world'
required[required_ingredient.index(야채)]
```