import engine
from coordinate import item_data


def place_item(x, y, name, delta, event="item"):
    """
    (x, y) 칸의 아이템 개수를 delta만큼 바꿉니다.

    - 같은 아이템이 있으면 개수를 더하고, 다른 아이템이 있으면 새 아이템으로 바꿉니다.
    - 개수가 0 이하가 되면 칸에서 아이템을 지웁니다.
    - 화면이 따라 그릴 수 있도록 결과를 이벤트로 남깁니다.
    """
    pos = (x, y)
    current = item_data.get(pos)
    if current and current["item"] == name:
        current["count"] += delta
    else:
        item_data[pos] = current = {"item": name, "count": delta}

    if current["count"] <= 0:
        del item_data[pos]
        engine.emit(event, pos=[x, y], item=None, count=0)
    else:
        engine.emit(event, pos=[x, y], item=name, count=current["count"])
