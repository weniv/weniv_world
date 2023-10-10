import js

from coordinate import character_data, map_data
from item import Item


# 이전 코드
# def print(*args):
#     '''
#     html 문서 내 출력
#     '''
#     output = js.document.getElementById('output')
#     result = ''
#     for arg in args:
#         result += str(arg) + '\n'
#     result = output.value + result
#     output.value = result


def print(*texts, type="normal"):
    """
    html 문서 내 출력
    """
    output = js.document.getElementById("output")
    result = ""

    for text in texts:
        result += str(text)

    if output:
        paragraph = js.document.createElement("p")
        paragraph.innerHTML = result
        paragraph.classList.add("output-item")
        if type == "error":
            paragraph.setAttribute("data-error", "true")
        output.appendChild(paragraph)
    else:
        js.console.log(result)


def say(text="", character=None, speech_time=5000):
    """
    charecter의 말풍선에 출력
    """
    if character != None:
        character.say(text)
    else:
        if character_data[0]["character_obj"] != None:
            character_data[0]["character_obj"].say(text, speech_time)
        else:
            print("캐릭터가 없습니다.")


def directions(character=None):
    """
    character의 방향을 right, left, top, bottom으로 반환
    """
    d = {0: "right", 1: "top", 2: "left", 3: "bottom"}
    if character != None:
        # TODO: 0번째가 아니라 순회 돌면서 self.name으로 찾아서 directions 반환
        # return d[character.directions] # self.directions가 제대로 반영 안되어 있음
        return d[character_data[0]["directions"]]
    else:
        if character_data[0]["character_obj"] != None:
            # return d[character_data[0]['character_obj'].directions] # self.directions가 제대로 반영 안되어 있음
            return d[character_data[0]["directions"]]
        else:
            print("캐릭터가 없습니다.")
            return None


def show_item(character=None):
    """
    character가 가지고 있는 아이템을 보여주는 함수
    """
    if character != None:
        # TODO: 0번째가 아니라 순회 돌면서 self.name으로 찾아서 items 반환
        return character_data[0]["items"]
    else:
        if character_data[0]["character_obj"] != None:
            # return d[character_data[0]['character_obj'].directions] # self.directions가 제대로 반영 안되어 있음
            return character_data[0]["items"]
        else:
            print("캐릭터가 없습니다.")
            return None


def set_item(x, y, name, count=1, description={}, character=None):
    if not (isinstance(x, int) and isinstance(y, int)):
        js.alert("좌표는 정수로 입력해야 합니다.")
        print(f"{x}, {y} error.TypeError: Position must be integer", type="error")
        return None

    if not (0 <= x < map_data["height"] and 0 <= y < map_data["width"]):
        js.alert("월드를 벗어나서 아이템을 추가할 수 없습니다.")
        print("error.OutOfWorld: out of world", type="error")
        return None

    item = Item(x, y, name, count, description)
    item.draw()


def move(character=None):
    if character != None:
        character.move()
    else:
        if character_data[0]["character_obj"] != None:
            character_data[0]["character_obj"].move()
        else:
            print("캐릭터가 없습니다.")


def turn_left(character=None):
    if character != None:
        character.turn_left()
    else:
        if character_data[0]["character_obj"] != None:
            character_data[0]["character_obj"].turn_left()
        else:
            print("캐릭터가 없습니다.")


def pick(character=None):
    if character != None:
        character.pick()
    else:
        if character_data[0]["character_obj"] != None:
            character_data[0]["character_obj"].pick()
        else:
            print("캐릭터가 없습니다.")


def put(item_name="fish", character=None):
    if character != None:
        character.put(item_name)
    else:
        if character_data[0]["character_obj"] != None:
            character_data[0]["character_obj"].put(item_name)
        else:
            print("캐릭터가 없습니다.")


def repeat(count, f):
    if isinstance(count, int) == True:
        for i in range(0, count):
            f()
    elif isinstance(f, int) == True:
        for i in range(0, f):
            count()


def front_is_clear(character=None):
    if character != None:
        print(f"character not none")
        return character.front_is_clear()
    else:
        if character_data[0]["character_obj"] != None:
            return character_data[0]["character_obj"].front_is_clear()
        else:
            print("캐릭터가 없습니다.")


def left_is_clear(character=None):
    if character != None:
        character.left_is_clear()
    else:
        if character_data[0]["character_obj"] != None:
            character_data[0]["character_obj"].left_is_clear()
        else:
            print("캐릭터가 없습니다.")


def right_is_clear(character=None):
    if character != None:
        character.right_is_clear()
    else:
        if character_data[0]["character_obj"] != None:
            character_data[0]["character_obj"].right_is_clear()
        else:
            print("캐릭터가 없습니다.")


def back_is_clear(character=None):
    if character != None:
        character.back_is_clear()
    else:
        if character_data[0]["character_obj"] != None:
            character_data[0]["character_obj"].back_is_clear()
        else:
            print("캐릭터가 없습니다.")


def attack(character=None):
    if character != None:
        character.attack()
    else:
        if character_data[0]["character_obj"] != None:
            character_data[0]["character_obj"].attack()
        else:
            print("캐릭터가 없습니다.")

def open(character=None):
    if character != None:
        character.open()
    else:
        if character_data[0]["character_obj"] != None:
            character_data[0]["character_obj"].open()
        else:
            print("캐릭터가 없습니다.")
            
def typeof_wall(character=None):
    if character != None:
        return character.typeof_wall()
    else:
        if character_data[0]["character_obj"] != None:
            return character_data[0]["character_obj"].typeof_wall()
        else:
            print("캐릭터가 없습니다.")
            return None
            