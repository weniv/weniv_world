# 마지막 관문 앞으로!

## 마지막 관문 앞으로! `내장 함수` `람다 함수`

라이캣의 팀은 모든 도전을 극복하고, 마침내 만장굴의 깊은 곳에 도착했습니다. 만장굴은 깊고도 넓었습니다. 한참을 걸어가던 일행은 갈림길에 도달했습니다. 갈림길에는 `max, 포션`이라고 적힌 표지판과 포션을 담은 유리병들이 놓여 있었습니다.

> "이게 포션이다냥! max라고 되어 있으니 갈림길 앞에 포션이 더 많은 곳으로 움직이는 것인가보다냥!"

그렇게 라이캣은 더 많은 포션이 위치해 있는 길을 선택해가며 움직이기 시작했습니다. 만장굴 끝에는 거대한 문이 있었습니다. 

![](15.webp)

개리가 문에 붙어있는 장식품을 힘을주어 눌러보자 장식물이 안으로 들어갔습니다. 누른 장식물은 다시 눌러 원상복구 할 수 있었어요. 


좀 더 살펴보자 아래와 같은 안내 문구를 발견할 수 있었습니다.

```text
지금까지 먹은 포션 중 3개보다 많고, 6개보다 적은 모든 포션의 수의 합을 구해 외쳐라!
```

라이캣이 지금까지 먹은 포션의 갯수를 말하자 문에는 서서히 문양이 나타나기 시작했습니다.


### 임무
포션이 좀 더 많이 놓인 갈림길을 따라 이동하며 라이캣이 지금까지 먹은 포션의 수를 기록해야 합니다. 갈림길 끝에 도달하면 3개보다 많고 6개보다 적은 포션의 총합을 계산해야 합니다. 이 숫자를 정확히 계산하여 말하세요.

### 기본 데이터
총 4개의 갈림길이 나옵니다.

```python
# 라이캣이 먹은 포션의 수
potion_counts = [0, 0, 0, 0]
```


## 사용 코드
아래 제시된 코드를 활용하여 문제를 해결해 주세요.
```python
filter()
sum()
lambda x: x**2
```