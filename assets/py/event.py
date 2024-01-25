import js

from world_map import Map
from wall import Wall
from character import Character
from item import Item
from coordinate import (
    character_data,
    map_data,
    wall_data,
    item_data,
    running_speed,
    map_size,
    border_size,
    wall_type,
    story_data,
)
from built_in_functions import (
    print,
    say,
    directions,
    show_item,
    set_item,
    move,
    turn_left,
    pick,
    put,
    repeat,
    attack,
    front_is_clear,
    left_is_clear,
    right_is_clear,
    back_is_clear,
)
from pyscript import when
from js import alert, setTimeout
from pyodide.ffi import create_once_callable
from pyodide.ffi.wrappers import add_event_listener
import json
import math

j.console.log("?? 실행??")

# item select
item_select = {"status": False, "name": ""}
# story select
story_select = {"status": False, "index": 1}
# spped value
a = 0.00020004
b = -0.0408163393
c = 2.5411162993

# speed slide bar
slider = js.document.getElementById("speed-range")
slider_output = js.document.getElementById("speed-text")
slider_output.innerHTML = slider.value
running_speed = a * int(slider.value) ** 2 + b * int(slider.value) + c


def change_speed(e):
    global running_speed
    slider_output.innerHTML = slider.value
    running_speed = a * int(slider.value) ** 2 + b * int(slider.value) + c
    if licat:
        licat.set_speed(running_speed)
    else:
        # 추후 다른 캐릭터 추가 시 구현
        pass


slider.oninput = change_speed

# map slide bar
map_slider_x = js.document.getElementById("map-range-x")
map_slider_y = js.document.getElementById("map-range-y")
map_slider_output_x = js.document.getElementById("map-text-x")
map_slider_output_y = js.document.getElementById("map-text-y")
map_slider_output_x.innerHTML = map_slider_x.value
map_slider_output_y.innerHTML = map_slider_y.value
map_data["height"] = int(map_slider_x.value)
map_data["width"] = int(map_slider_y.value)


def change_map(e):
    global wall_data
    map_data["height"] = int(map_slider_x.value)
    map_data["width"] = int(map_slider_y.value)
    map_slider_output_x.innerHTML = map_slider_x.value
    map_slider_output_y.innerHTML = map_slider_y.value
    map_exist = js.document.querySelector(".map-container")
    # TODO: map object는 map_data에서 관리해야할 것으로 보임
    if map_exist:
        js.document.querySelector(".map-container").remove()
        map = Map(map_data["height"], map_data["width"])
        draw_map = map.drawMap()
        draw_map.appendChild(draw_character)
        app = js.document.createElement("app")
        app.appendChild(draw_map)

        wall.resizeWall(map_data["width"], map_data["height"])
        wall_container = wall.drawWall()
        wall_data["world"] = wall.wall_data

        # map-item 이벤트 등록
        for map_elem in draw_map.querySelectorAll(".map-item"):
            add_event_listener(map_elem, "click", map_item_add)

        # wall_container의 자식요소들에 이벤트 등록
        for wall_elem in wall_container.querySelectorAll(".wall"):
            add_event_listener(wall_elem, "click", change_wall_type)
            add_event_listener(wall_elem, "mouseover", wall_mouse_activation)
            add_event_listener(wall_elem, "mouseenter", wall_mouse_enter)
            add_event_listener(wall_elem, "mouseleave", wall_mouse_leave)

        draw_map.appendChild(wall_container)

    # 범위를 벗어난 아이템 삭제
    global item_data
    keys_to_remove = []  # 제거할 항목의 키를 저장할 리스트

    for x, y in item_data.keys():
        if not (0 <= x < map_data["height"] and 0 <= y < map_data["width"]):
            keys_to_remove.append((x, y))
    for key in keys_to_remove:
        del item_data[key]

    for key, value in item_data.items():
        x, y = key
        name = value["item"]
        count = value["count"]
        set_item(x, y, name, count)


map_slider_x.oninput = change_map
map_slider_y.oninput = change_map

# 벽 생성
wall = Wall()
wall_container = wall.drawWall()
wall_data["world"] = wall.wall_data


# character 생성
# TODO: 캐릭터 크기 수정
licat = Character(x=0, y=0, name="licat", width=32, height=40)
character_data[0]["character_obj"] = licat
draw_character = licat.draw()

# map 생성
map = Map(map_data["height"], map_data["width"])
draw_map = map.drawMap()
draw_map.appendChild(draw_character)
draw_map.appendChild(wall_container)

# 생성된 요소 app추가
app = js.document.createElement("app")
app.appendChild(draw_map)


@when("click", selector="#init")
def init(evt=None):
    global wall_data
    js.console.log("월드 초기화")
    map_data["height"] = 5
    map_data["width"] = 5
    map_slider_x.value = 5
    map_slider_y.value = 5
    item_data.clear()
    map_slider_output_x.innerHTML = map_slider_x.value
    map_slider_output_y.innerHTML = map_slider_y.value
    map_exist = js.document.querySelector(".map-container")
    # TODO: map object는 map_data에서 관리해야할 것으로 보임
    if map_exist:
        js.document.querySelector(".map-container").remove()
        map = Map(map_data["height"], map_data["width"])
        draw_map = map.drawMap()
        draw_map.appendChild(draw_character)
        app = js.document.createElement("app")
        app.appendChild(draw_map)

        wall.resetWall(map_data["width"], map_data["height"])

        if story_select["status"]:
            idx = story_select["index"]
            if story_data.get(idx):
                map_data["height"] = story_data[idx]["map_height"]
                wall_data["world"] = story_data[idx]["wall"]
                wall.wall_data = story_data[idx]["wall"]

                items = story_data[idx]["item"]

                for pos in items:
                    item = Item(pos[0], pos[1], items[pos]["item"], items[pos]["count"])
                    item.draw()

        wall_container = wall.drawWall()
        wall_data["world"] = wall.wall_data

        if story_select["status"]:
            wall_container.style.pointerEvents = "none"
            js.document.querySelector(".map-items").style.pointerEvents = "none"

        # map-item 이벤트 등록
        for map_elem in draw_map.querySelectorAll(".map-item"):
            add_event_listener(map_elem, "click", map_item_add)

        # wall_container의 자식요소들에 이벤트 등록
        for wall_elem in wall_container.querySelectorAll(".wall"):
            add_event_listener(wall_elem, "click", change_wall_type)
            add_event_listener(wall_elem, "mouseover", wall_mouse_activation)
            add_event_listener(wall_elem, "mouseenter", wall_mouse_enter)
            add_event_listener(wall_elem, "mouseleave", wall_mouse_leave)

        draw_map.appendChild(wall_container)

    init_character()


@when("click", selector="#init_character")
def init_character(evt=None):
    js.console.log("캐릭터 초기화")
    global running_speed
    js.document.querySelector(".character").remove()
    character_data[0] = {
        "character": "licat",
        "character_obj": None,
        "x": 0,
        "y": 0,
        "directions": 0,  # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
        "items": {},
    }
    licat = Character(x=0, y=0, name="licat", width=32, height=40, rotate=0)
    for line in js.document.querySelectorAll(".line"):
        line.remove()
    character_data[0]["character_obj"] = licat
    draw_character = licat.draw()
    js.document.querySelector(".map-container").appendChild(draw_character)
    change_speed(running_speed)
    add_event_listener(draw_character, "click", show_character_info)


@when("click", selector="#btn-list-function")
def list_function(evt=None):
    """
    메인화면에서 함수 목록 보는 함수
    event.js에서 처리하고 있어서 주석처러하였습니다.
    """
    # js.console.log('함수 목록')
    # js.document.querySelector('.function-list').classList.# toggle('hidden')


@when("click", selector="#btn-list-variable")
def list_variable(evt=None):
    """
    메인화면에서 변수 목록 보는 함수
    event.js에서 처리하고 있어서 주석처러하였습니다.
    """
    # js.console.log('변수 목록')
    # js.document.querySelector('.variable-list').classList.# # toggle('hidden')


@when("click", selector=".character")
def show_character_info(evt=None):
    """
    캐릭터를 클릭하면 캐릭터 정보(character_data)를 볼 수 있는 함수
    """
    # evt를 통해 x좌표, y좌표를 얻어냄
    # x = evt.x
    # y = evt.y
    # x좌표, y좌표에 말풍선 생성
    bubble = js.document.createElement("div")
    bubble.setAttribute("class", "character-info-bubble info-modal")

    # 말풍선에 캐릭터 정보 추가
    bubble.innerHTML = f"""
        <p class="info-title">캐릭터 정보</p>
        <dl class="info-list">
            <div class="info-item">
                <dt class="bubble-body-item-title">이름</dt>
                <dd class="bubble-body-item-content">{character_data[0]['character']}</dd>
            </div>
            <div class="info-item">
                <dt class="bubble-body-item-title">x좌표</dt>
                <dd class="bubble-body-item-content">{character_data[0]['x']}</dd>
            </div>
            <div class="info-item">
                <dt class="bubble-body-item-title">y좌표</dt>
                <dd class="bubble-body-item-content">{character_data[0]['y']}</dd>
            </div>
            <div class="info-item">
                <dt class="bubble-body-item-title">방향</dt>
                <dd class="bubble-body-item-content">{character_data[0]['directions']}</dd>
            </div>
            <div class="info-item">
                <dt class="bubble-body-item-title">아이템</dt>
                <dd class="bubble-body-item-content">{character_data[0]['items']}</dd>
            </div>
             <div class="info-item">
                <dt class="bubble-body-item-title">체력</dt>
                <dd class="bubble-body-item-content">{character_data[0]['hp']}</dd>
            </div>
        </dl>
        <button type="button" id="init_character" class="btn-reset">
            <span class="sr-only">캐릭터 초기화</span>
        </button>
    """
    # app에 말풍선 추가(이미 말풍선이 존재하는 경우에는 추가하지 않음.)
    addedBubble = js.document.querySelector(".character-info-bubble")
    target_character = js.document.querySelector(".character")

    if not addedBubble:
        target_character.appendChild(bubble)

    # 5초후 제거
    setTimeout(create_once_callable(lambda: (bubble.remove())), 5000)


@when("click", selector="#btn-download-worlddata")
def download_worlddata(evt=None):
    """
    메인화면에서 월드데이터 다운로드
    """
    js.console.log("월드데이터 다운로드")

    # 월드데이터 다운로드
    character_info = character_data.copy()
    character_info[0]["character_obj"] = None
    worlddata = {
        "character_data": character_info,
        "item_data": item_data,
        "map_data": map_data,
        "wall_data": wall_data["world"],
    }

    json_data = json.dumps(worlddata)
    file = js.File.new([json_data], "unused_file_name.txt", {type: "text/plain"})
    url = js.URL.createObjectURL(file)
    hidden_link = js.document.createElement("a")
    hidden_link.setAttribute("download", "my_other_file_name.txt")
    hidden_link.setAttribute("href", url)
    hidden_link.click()

'''
@when("click", selector="#btn-upload-worlddata")
def upload_worlddata(evt=None):
    js.console.log('월드데이터 업로드')
    js.document.getElementById("worldFileInput").click()


@when("change", selector="#worldFileInput")
def upload_world_data(evt):
    origin_data = evt.target.files

    data_file = js.FileReader.new()
    data_file.readAsText(origin_data.item(0))
    data_file.onload = parsing_json


def check_json_data(json_data):
    pass

def init_charcter(draw_character):
    js.console.log('캐릭터 초기화')
    global running_speed
    character = js.document.querySelector('.character')
    if character:
        js.document.querySelector('.character').remove()
    for line in js.document.querySelectorAll('.line'):
        line.remove()
    js.document.querySelector('.map-container').appendChild(draw_character)
    change_speed(running_speed)
    js.console.log('캐릭터 초기화 완료')
    add_event_listener(draw_character, 'click', show_character_info)

def parsing_json(evt):
    js.console.log('파싱')
    js.console.log(evt.target.result),
    js.console.log('파싱2')
    js.console.log(json.loads(evt.target.result)),
    js.console.log('파싱3')
    json_data = json.loads(evt.target.result)
    check_json_data(json_data)
    # # 캐릭터 좌표
    # # 0번째는 default 캐릭터
    # character_data = [
    #     {
    #         "character": "licat",
    #         "character_obj": None,
    #         "x": 0,
    #         "y": 0,
    #         "directions": 0,  # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
    #         "items": {},
    #     }
    # ]

    global wall_data
    global character_data
    character_data = json_data["character_data"]
    js.console.log("캐릭터 데이터")
    js.console.log(character_data)
    global item_data
    item_data = json_data["item_data"]
    js.console.log("아이템 데이터")
    js.console.log(item_data)
    global map_data
    map_data = json_data["map_data"]
    js.console.log("맵 데이터")
    js.console.log(map_data)
    temp_wall_data = {}
    for key in json_data["wall_data"].keys():
        temp_wall_data[tuple(key)] = json_data["wall_data"][key]
    js.console.log("벽 데이터")
    js.console.log(temp_wall_data)
    wall_data['world'] = temp_wall_data
    js.console.log("벽 데이터2")
    js.console.log(wall_data['world'])
    global wall_container
    map_slider_x.value = map_data['height']
    map_slider_y.value = map_data['width']
    map_slider_output_x.innerHTML = map_slider_x.value
    map_slider_output_y.innerHTML = map_slider_y.value
    map_exist = js.document.querySelector('.map-container')
    js.console.log("맵 존재여부")
    js.console.log(map_exist)
    if character_data[0]['character_obj'] is None:
        licat = Character(x=0, y=0, name='licat', width=32, height=40,rotate=0)
        character_data[0]['character_obj'] = licat
    else:
        licat = character_data[0]['character_obj']
    js.console.log("캐릭터")
    js.console.log(licat)
    draw_character = licat.draw()

    keys_to_remove = []  # 제거할 항목의 키를 저장할 리스트

    for (x, y) in item_data.keys():
        if not (0 <= x < map_data['height'] and 0 <= y < map_data['width']):
            keys_to_remove.append((x, y))
    for key in keys_to_remove:
        del item_data[key]

    for key, value in item_data.items():
        x, y = key
        name = value['item']
        count = value['count']
        set_item(x, y, name, count)
    if map_exist:
        js.console.log('존재')
        js.document.querySelector('.map-container').remove()
        map = Map(map_data['height'], map_data['width'])
        draw_map = map.drawMap()
        draw_map.appendChild(draw_character)
        app = js.document.createElement("app")
        app.appendChild(draw_map)

        wall.resizeWall(map_data['width'], map_data['height'])

        wall_container = wall.drawWall()
        wall_data['world'] = wall.wall_data

        # map-item 이벤트 등록
        for map_elem in draw_map.querySelectorAll('.map-item'):
            add_event_listener(map_elem, 'click', map_item_add)

        # wall_container의 자식요소들에 이벤트 등록
        for wall_elem in wall_container.querySelectorAll('.wall'):
            add_event_listener(wall_elem,'click',change_wall_type)
            add_event_listener(wall_elem,'mouseover',wall_mouse_activation)
            add_event_listener(wall_elem,'mouseenter',wall_mouse_enter)
            add_event_listener(wall_elem,'mouseleave',wall_mouse_leave)

        draw_map.appendChild(wall_container)

    init_charcter(draw_character)
'''
@when("click", selector=".wall")
def change_wall_type(evt):
    """
    벽 타입 변경
    """
    posX = float(evt.target.dataset.x)
    posY = float(evt.target.dataset.y)
    currentType = evt.target.dataset.type

    # 벽 추가: type이 없는 항목에서만 동작
    if wall_type != "delete":
        if not currentType:
            wall_data["world"][(posX, posY)] = wall_type
            evt.target.dataset.type = wall_type

    # 벽 삭제: type이 있는 항목에서만 동작
    else:
        if currentType:
            del wall_data['world'][(posX, posY)]
            # wall_data["world"][(posX, posY)] = ""
            evt.target.dataset.type = ""
            evt.target.style.outline = ""


@when("mouseover", selector=".wall")
def wall_mouse_activation(evt):
    currentType = evt.target.dataset.type

    # 벽 추가: type이 없는 항목에서만 pointer
    if wall_type != "delete":
        if not currentType:
            evt.target.style.cursor = "pointer"
        else:
            evt.target.style.cursor = "default"

    # 벽 삭제: type이 있는 항목에서만 pointer
    else:
        if currentType:
            evt.target.style.cursor = "pointer"
        else:
            evt.target.style.cursor = "default"


@when("mouseenter", selector=".wall")
def wall_mouse_enter(evt):
    currentType = evt.target.dataset.type

    if wall_type == "delete":
        if currentType:
            evt.target.style.outline = "3px solid red"


@when("mouseleave", selector=".wall")
def wall_mouse_leave(evt):
    currentType = evt.target.dataset.type

    if wall_type == "delete":
        if currentType:
            evt.target.style.outline = ""


# radio 속성을 선택했을 때, wall_type을 변경하는 이벤트 등록
@when("change", selector="input[name='wall-type']")
def change_walltype_input(evt):
    global wall_type
    wall_type = evt.target.value


@when("click", selector="input[name='item']")
def change_item_select(evt):
    if item_select["status"] and evt.target.id == item_select["name"]:
        # 선택 취소
        label = js.document.querySelector(f"label[for='{evt.target.id}']")
        label.classList.remove("active")

        item_select["status"] = False
        js.document.querySelector(".wall-container").style.pointerEvents = ""

        item_select["name"] = ""
        js.document.querySelector(".map-container").style.cursor = "auto"
    else:
        # 이전 선택 스타일 취소
        if item_select["name"]:
            label = js.document.querySelector(f"label[for='{item_select['name']}']")
            label.classList.remove("active")

        item_select["status"] = True
        js.document.querySelector(".wall-container").style.pointerEvents = "none"

        item_select["name"] = evt.target.id
        js.document.querySelector(
            ".map-container"
        ).style.cursor = f"url(assets/img/item/{evt.target.id}.png), auto"

        label = js.document.querySelector(f"label[for='{evt.target.id}']")
        label.classList.add("active")


@when("click", selector=".map-item")
def map_item_add(evt):
    if item_select["status"]:
        # 좌표값 계산
        map_items = js.document.querySelectorAll(".map-item")
        index = 0
        for item in map_items:
            if item == evt.target:
                break
            index += 1

        # index를 통해 x, y 좌표 계산
        x, y = divmod(index, map_data["width"])
        evt.target.style.backgroundColor = ""
        set_item(x, y, item_select["name"], 1)

        item_select["status"] = False
        item_select["name"] = ""
        js.document.querySelector(".map-container").style.cursor = "default"
        js.document.querySelector(".wall-container").style.pointerEvents = ""


@when("click", selector="#output-init")
def init_output(evt=None):
    for output_line in js.document.querySelectorAll(".output-item"):
        output_line.remove()
    for liElement in js.document.querySelectorAll(".index-list li"):
        liElement.remove()


@when("click", selector="#output-download")
def init_output(evt=None):
    """'
    js.document.querySelectorAll('.output-item')에 있는 모든 내용을
    txt 파일로 다운로드 하는 코드
    """
    js.console.log("다운로드")
    output = js.document.querySelectorAll(".output-item")
    output_text = ""
    for line in output:
        output_text += line.innerHTML + "\n"
    file = js.File.new([output_text], "result.txt", {type: "text/plain"})
    url = js.URL.createObjectURL(file)
    hidden_link = js.document.createElement("a")
    hidden_link.setAttribute("download", "result.txt")
    hidden_link.setAttribute("href", url)
    hidden_link.click()


@when("click", selector=".btn-add-code")
def add_code_sell(evt=None):
    newRepl = js.document.createElement("py-repl")
    newRepl.textContent = ""
    js.document.getElementById("notebookSection").appendChild(newRepl)


storyList = js.document.querySelectorAll(".story-list>li")


@when("click", selector=".story-list>li")
def set_story_map(evt=None):
    if evt.target.tagName == "BUTTON":
        if evt.currentTarget.classList.contains("active"):
            story_select["index"] = 0
        else:
            story_select["index"] = list(storyList).index(evt.currentTarget) + 1
        init()


@when("click", selector=".btn-story")
def check_story_open(evt=None):
    if evt.target.classList.contains("active"):
        story_select["status"] = True
        if not (js.document.querySelector(".story-list>li.active")):
            story_select["index"] = 0
    else:
        story_select["status"] = False
    init()


@when("click", selector=".btn-close-story")
def story_close(evt=None):
    story_select["status"] = False
    init()
