# 구출하라!

## 구출하라! `클래스` `데이터 구조`

스페이스 스톤은 공간을 다스리는 스톤! 개리는 라이캣에게 스페이스 스톤을 받아 포털을 열었습니다.

대대로 위니브 월드의 인력 공급원으로 활동해 온 개굴 부족은 오랜 시간 노역에 시달려왔습니다. 그들의 삶은 노예적 습관에 깊게 젖어 있었고, 이는 개리가 마주한 가장 큰 장애물이었습니다. 변화를 두려워하는 그들을 어떻게 설득할 것인지, 개리는 고민에 빠졌습니다.

개굴 부족은 대대로 위니브 월드의 가장 큰 인력 공급원이었습니다. 이미 개굴 부족의 깊은 곳까지 스며든 노예의 습관은 가장 큰 허들임. 그래서 구출을 한다고 하여 그들이 노역장에서 나올 수 있을까 고민. 그들은 변화가 두려울 것임. 그렇다고 하더라도 구출해야 함

> "옭아매는 모든 쇠사슬에 도끼를 들겠다 개굴!"

개리는 결심했습니다. 부족원들을 안전한 곳으로 옮겨 그들과 대화를 나누기로 한 것입니다. 이 과정은 쉽지 않을 것이라는 것을 그는 알고 있었습니다. 어떤 이들은 강제적인 변화에 저항하고, 심지어 개리에게 반기를 드는이도 있을 것입니다.

그렇다 하여 선택의 여지를 주는 것은 작전이 들킬 수 있기에 매우 위험한 행위입니다. 변화를 받아들이지 않는 이들이 있을지라도, 그는 구출 작전을 감행하기로 결정합니다.


### 임무
개리가 스페이스 스톤을 사용하여 안전하게 모든 부족원들을 새로운 환경으로 이동시키는 프로세스를 구현하세요. 이 임무는 데이터 구조 중 하나인 '큐(Queue)'나 '스택(Stack)'을 이용하여 해결해야 합니다. 각 부족원들은 큐에 들어가 순차적으로 포털을 통해 이동하게 됩니다.

### 기본 데이터
```python
class TribeMember:
    pass

class PortalQueue:
    pass

tribe_members = [
    TribeMember('member1'), 
    TribeMember('member2'),
    TribeMember('member3'),
    TribeMember('member4'),
    TribeMember('member5')
]
portal_queue = PortalQueue()

# 부족원 인스턴스 생성 및 큐에 추가
for member in tribe_members:
    portal_queue.enter_portal(member)

# 모든 부족원 이동
result = portal_queue.transport_all()
print(result)
```

### 결과값
```python
'모든 부족원이 안전하게 이동되었습니다.'
```

## 사용 코드
```python
class TribeMember:
    # 멤버 초기화 및 특성 정의
    def __init__(self, name):
        self.name = name

class PortalQueue:
    # 포털 큐 초기화 및 멤버 관리 메서드 정의
    def __init__(self):
        self.queue = []

    def enter_portal(self, member):
        # 멤버 포털 진입 로직
        pass

    def transport_all(self):
        # 모든 멤버 이동 로직(5명이 모두 이동하였는지 확인)
        pass
```