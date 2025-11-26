
from worldMap import Map
from wall import Wall
from character import Character
from mob import Mob
from item import Item
from error import *
from coordinate import map_data, running_speed, character_data, default_character, mob_data, item_data, wall_data, valid_items, edible_items,wall_type, story_data, mob_info, skill_data, character_info, print_data, say_data
from built_in_functions import print, say, directions, item, set_item, move, turn_left, pick, put, repeat, attack, front_is_clear, left_is_clear, right_is_clear, back_is_clear, open_door, typeof_wall, mission_start, mission_end, on_item, mob_exist, character_exist, show_modal_alert, eat
from solution import story_solution
from pyscript import when
from js import alert, setTimeout
from pyodide.ffi import create_once_callable
from pyodide.ffi.wrappers import add_event_listener
import json
import math
import copy
from datetime import datetime

# item select
item_select = {
    'status':False,
    'name':''
}
mob_select = {
    'status':False,
    'name':''
}
# story select
story_select = {
    'status': False,
    'index': 1
}
# spped value
a = 0.00020004
b = -0.0408163393
c = 2.5411162993

# speed slide bar
slider = js.document.getElementById("speed-range")
slider_output = js.document.getElementById("speed-text")
slider_output.innerHTML = slider.value
running_speed = a * int(slider.value)**2 + b * int(slider.value) + c

def change_speed(e):
    global running_speed
    slider_output.innerHTML = slider.value
    running_speed = a * int(slider.value)**2 + b * int(slider.value) + c
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
map_data['height'] = int(map_slider_x.value)
map_data['width'] = int(map_slider_y.value)

def change_map(evt=None):
    js.console.log('change map')
    global wall_data, item_data, draw_map, mob_data, character_data
    main_ch = character_data[0]
    
    #슬라이더로 맵 크기 변경 
    if evt: 
        if main_ch['x'] > int(map_slider_x.value) - 1 or main_ch['y'] > int(map_slider_y.value) - 1:
            js.alert(f"기본 캐릭터의 위치보다 작게 맵을 설정할 수 없습니다.")
            map_slider_x.value = initX
            map_slider_y.value = initY
            map_slider_output_x.innerHTML = initX
            map_slider_output_y.innerHTML = initY
            return
        map_data['height'] = int(map_slider_x.value)
        map_data['width'] = int(map_slider_y.value)
        map_slider_output_x.innerHTML = map_slider_x.value
        map_slider_output_y.innerHTML = map_slider_y.value
    else:
        map_slider_output_x.innerHTML = map_data['height']
        map_slider_x.value = map_data['height']
        map_slider_output_y.innerHTML = map_data['width']
        map_slider_y.value = map_data['width']
        
    map_exist = js.document.querySelector('.map-container')
    # TODO: map object는 map_data에서 관리해야할 것으로 보임
    if map_exist:
        js.document.querySelector('.map-container').remove()
        world_map = Map(map_data['height'], map_data['width'])
        draw_map = world_map.drawMap()
        # draw_map.appendChild(draw_character)
        app = Element("app").element
        app.appendChild(draw_map)

        wall.resizeWall(map_data['width'], map_data['height'])
        wall_container = wall.drawWall()
        wall_data['world'] = wall.wall_data
        draw_map.appendChild(wall_container)

        # map-item, mob_add 이벤트 등록
        for map_elem in draw_map.querySelectorAll('.map-item'):
            add_event_listener(map_elem, 'click', map_item_add)
            add_event_listener(map_elem, 'click', mob_add)

        # wall_container의 자식요소들에 이벤트 등록
        for wall_elem in wall_container.querySelectorAll('.wall'):
            add_event_listener(wall_elem,'click',change_wall_type)
            add_event_listener(wall_elem,'mouseover',wall_mouse_activation)
            add_event_listener(wall_elem,'mouseenter',wall_mouse_enter)
            add_event_listener(wall_elem,'mouseleave',wall_mouse_leave)

        # 우클릭 삭제 이벤트 리스너 등록
        register_contextmenu_listener()


    # 캐릭터 갱신
    for c in character_data[:]:
        if not (0 <= c['x'] < map_data['height'] and 0 <= c['y'] < map_data['width']):
            character_data.remove(c)
        else:
            new_ch = Character(x=c['x'], y=c['y'], name=c['character'], width=32, height=40,rotate=c['directions'])
            c['character_obj'] = new_ch
            draw_ch = c['character_obj'].draw()
            draw_map.appendChild(draw_ch)
            add_event_listener(draw_ch, 'click', show_character_info)


    # 아이템 갱신
    for i in copy.deepcopy(item_data).keys():
        if not (0 <= i[0] < map_data['height'] and 0 <= i[1] < map_data['width']):
            del item_data[i]
        else:
            new_item = Item(i[0], i[1], item_data[i]['item'], item_data[i]['count'])
            new_item.draw()
    

    # 몹 갱신
    for m in mob_data[:]:
        if not (0 <= m['x'] < map_data['height'] and 0 <= m['y'] < map_data['width']):
            mob_data.remove(m)
        else:
            new_mob = Mob(x=m['x'], y=m['y'],mob=m['mob'] ,name=m['name'], width=32, height=40,directions=m['directions'], initHp=mob_info[m['mob']]['hp'])
            m['mob_obj'] = new_mob
            draw_ch = m['mob_obj'].draw()
            draw_map.appendChild(draw_ch)

map_slider_x.oninput = change_map
map_slider_y.oninput = change_map

#벽 생성
wall = Wall()
wall_container = wall.drawWall();
wall_data['world'] = wall.wall_data

# character 생성
# TODO: 캐릭터 크기 수정
licat = Character(x=0, y=0, name='licat', width=32, height=40)
character_data[0]['character_obj'] = licat
draw_character = licat.draw()

# map 생성
world_map = Map(map_data['height'], map_data['width'])
draw_map = world_map.drawMap()
draw_map.appendChild(draw_character)
draw_map.appendChild(wall_container)

# 생성된 요소 app추가
app = Element("app").element
app.appendChild(draw_map)

@when("click", selector="#init")
def init(evt=None):
    global wall_data, wall_container, mob_data, draw_map, print_data, say_data
    js.console.log('월드 초기화')
    map_data['height'] = 5
    map_data['width'] = 5
    print_data.clear()
    say_data.clear()

    idx = story_select['index']
    if(story_select['status'] and story_data.get(idx)):
        map_data['width']= story_data[idx]['map_width']
        map_data['height']= story_data[idx]['map_height']
        
    map_slider_x.value = 5
    map_slider_y.value = 5
    item_data.clear()
    map_slider_output_x.innerHTML = map_slider_x.value
    map_slider_output_y.innerHTML = map_slider_y.value
    map_exist = js.document.querySelector('.map-container')

    # TODO: map object는 map_data에서 관리해야할 것으로 보임
    if map_exist:
        js.document.querySelector('.map-container').remove()
        world_map = Map(map_data['height'], map_data['width'])
        draw_map = world_map.drawMap()
        draw_map.appendChild(draw_character)
        app = Element("app").element
        app.appendChild(draw_map)
        
        wall.resetWall(map_data['width'], map_data['height'])
        if(story_select['status'] and story_data.get(idx)):
            wall_data['world']= story_data[idx]['wall']
            wall.wall_data = story_data[idx]['wall']
        
            wall.resizeWall(story_data[idx]['map_width'],story_data[idx]['map_height'])

            items = story_data[idx]['item']

            for pos in items:
                if ( 0 <= pos[0] < map_data['height'] and 0 <= pos[1] < map_data['width']):
                    item = Item(pos[0], pos[1], items[pos]['item'], items[pos]['count'])
                    item.draw()

            for mob in story_data[idx].get('mob_data',[]):
                add_mob(mob['x'], mob['y'], mob['mob'], mob['name'], mob['directions'])

                
        wall_container = wall.drawWall()
        wall_data['world']= wall.wall_data

        if(story_select['status']):
            wall_container.style.pointerEvents='none'
            js.document.querySelector('.map-items').style.pointerEvents='none'

        # map-item, mob_add 이벤트 등록
        for map_elem in draw_map.querySelectorAll('.map-item'):
            add_event_listener(map_elem, 'click', map_item_add)
            add_event_listener(map_elem, 'click', mob_add)

        # wall_container의 자식요소들에 이벤트 등록
        for wall_elem in wall_container.querySelectorAll('.wall'):
            add_event_listener(wall_elem,'click',change_wall_type)
            add_event_listener(wall_elem,'mouseover',wall_mouse_activation)
            add_event_listener(wall_elem,'mouseenter',wall_mouse_enter)
            add_event_listener(wall_elem,'mouseleave',wall_mouse_leave)

        draw_map.appendChild(wall_container)

        # 우클릭 삭제 이벤트 리스너 등록
        register_contextmenu_listener()

    if not story_select['status']:
        mob_data.clear()
    init_character()
        
@when("click", selector="#init_character")
def init_character(evt=None):
    js.console.log('캐릭터 초기화')
    global running_speed
    js.document.querySelector('.character').remove()
    character_data.clear()
    character_data.append({
        'character': 'licat',
        'character_obj': None,
        'x': 0,
        'y': 0,
        'directions': 0, # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
        'items': {},
        'hp':100,
        # 'power':10,
        'mp':100
    })
    licat = Character(x=0, y=0, name='licat', width=32, height=40,rotate=0)
    for line in js.document.querySelectorAll('.line'):
        line.remove()
    character_data[0]['character_obj'] = licat
    draw_character = licat.draw()
    js.document.querySelector('.map-container').appendChild(draw_character)
    change_speed(running_speed)
    add_event_listener(draw_character, 'click', show_character_info)

def init_story_character(update_data, evt=None):
    global running_speed
    js.document.querySelector('.character').remove()
    character_data.clear()
    licat_data={{
        'character': 'licat',
        'character_obj': None,
        'x': 0,
        'y': 0,
        'directions': 0, # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
        'items': {},
        'hp':100,
        # 'power':10,
        'mp':100
    }}
    licat_data.update(update_data)
    print(licat_data)

    character_data.append(licat_data)
    licat = Character(x=0, y=0, name='licat', width=32, height=40,rotate=0)
    for line in js.document.querySelectorAll('.line'):
        line.remove()
    character_data[0]['character_obj'] = licat
    draw_character = licat.draw()
    js.document.querySelector('.map-container').appendChild(draw_character)
    change_speed(running_speed)
    add_event_listener(draw_character, 'click', show_character_info)

@when("click", selector="#btn-list-function")
def list_function(evt=None):
    '''
    메인화면에서 함수 목록 보는 함수
    event.js에서 처리하고 있어서 주석처러하였습니다.
    '''
    # js.console.log('함수 목록')
    # js.document.querySelector('.function-list').classList.# toggle('hidden')

@when("click", selector="#btn-list-variable")
def list_variable(evt=None):
    '''
    메인화면에서 변수 목록 보는 함수
    event.js에서 처리하고 있어서 주석처러하였습니다.
    '''
    # js.console.log('변수 목록')
    # js.document.querySelector('.variable-list').classList.# # toggle('hidden')

@when("click", selector=".character")
def show_character_info(evt=None):
    '''
    캐릭터를 클릭하면 캐릭터 정보(character_data)를 볼 수 있는 함수
    '''
    # evt를 통해 x좌표, y좌표를 얻어냄
    # x = evt.x
    # y = evt.y
    # x좌표, y좌표에 말풍선 생성
    bubble = js.document.createElement('div')
    bubble.setAttribute('class', 'character-info-bubble info-modal')

    # 말풍선에 캐릭터 정보 추가
    bubble.innerHTML = f'''
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
                <dd class="bubble-body-item-content">{character_data[0]['hp']} / {character_data[0]['character_obj'].initHp}</dd>
            </div>
            <div class="info-item">
                <dt class="bubble-body-item-title">마나</dt>
                <dd class="bubble-body-item-content">{character_data[0]['mp']} / {character_data[0]['character_obj'].initMp}</dd>
            </div>
        </dl>
        <button type="button" id="init_character" class="btn-reset">
            <span class="sr-only">캐릭터 초기화</span>
        </button>
    '''
    # app에 말풍선 추가(이미 말풍선이 존재하는 경우에는 추가하지 않음.)
    addedBubble = js.document.querySelector('.character-info-bubble')
    target_character = js.document.querySelector('.character')

    if not addedBubble:
        target_character.appendChild(bubble)
        init_button = js.document.querySelector('#init_character')
        add_event_listener(init_button, 'click', init_character)

    # 5초후 제거
    setTimeout(
        create_once_callable(
            lambda: (
                bubble.remove()
            )
        ), 5000
    )

@when("click", selector="#btn-download-worlddata")
def download_worlddata(evt=None):
    '''
    메인화면에서 월드데이터 다운로드
    '''
    js.console.log('월드데이터 다운로드')

    # 월드데이터 다운로드
    temp_character_data = character_data.copy()
    for c in temp_character_data:
        c['character_obj'] = None
        
    temp_wall_data = {}
    for key in wall_data['world'].keys():
        # temp_wall_data[(key[0],key[1])] = wall_data['world'][key]
        temp_wall_data[str(key)] = wall_data['world'][key]
    
    temp_item_data = {}
    for key in item_data.keys():
        temp_item_data[str(key)] = item_data[key]
    
    temp_mob_data = mob_data.copy()
    for m in temp_mob_data:
        m['mob_obj'] = None
        
    worlddata = {
        "character_data": temp_character_data,
        "item_data": temp_item_data,
        "map_data": map_data,
        "wall_data": temp_wall_data,
        "mob_data": temp_mob_data
    }

    json_data = json.dumps(worlddata)
    file = js.File.new([json_data], "world_data.json", {type: "text/plain"})
    url = js.URL.createObjectURL(file)
    hidden_link = js.document.createElement("a")
    hidden_link.setAttribute("download", "world_data.json")
    hidden_link.setAttribute("href", url)
    hidden_link.click()

@when("click", selector="#btn-upload-worlddata")
def upload_worlddata(evt=None):
    '''
    메인화면에서 월드데이터 업로드
    '''
    js.console.log('월드데이터 업로드')
    js.document.getElementById("worldFileInput").click()


@when("change", selector="#worldFileInput")
def upload_world_data(evt):
    origin_data = evt.target.files
    data_file = js.FileReader.new()
    data_file.readAsText(origin_data.item(0))
    data_file.onload = parsing_json
    evt.target.value = ""


def check_json_data(json_data):
    pass

def init_charcter(draw_character):
    global running_speed
    character = js.document.querySelector('.character')
    if character:
        js.document.querySelector('.character').remove()
    for line in js.document.querySelectorAll('.line'):
        line.remove()

    js.document.querySelector('.map-container').appendChild(draw_character)
    change_speed(running_speed)
    add_event_listener(draw_character, 'click', show_character_info)

def parsing_json(evt):
    init()
    json_data = json.loads(evt.target.result)
    check_json_data(json_data)

    global character_data
    character_data.clear()
    for c in json_data["character_data"]:
        character_data.append(c)

    global map_data
    for key, value in json_data["map_data"].items():
        map_data[key]=value
        
    temp_wall_data = {}
    temp_item_data = {}

    for key in json_data["wall_data"].keys():
        temp_x,temp_y = key.strip('()').split(',')
        temp_x = float(temp_x)
        temp_y = float(temp_y)

        temp_x = int(temp_x) if float.is_integer(temp_x) else temp_x
        temp_y = int(temp_y) if float.is_integer(temp_y) else temp_y
        temp_wall_data[(temp_x,temp_y)] = json_data["wall_data"][key]
        
    global wall_data, wall
    wall_data['world'] = temp_wall_data
    wall.wall_data = temp_wall_data
    
    for key in json_data["item_data"].keys():
        temp_x ,temp_y = key.strip('()').split(',')
        temp_x = int(temp_x)
        temp_y = int(temp_y)
        temp_item_data[(temp_x,temp_y)] = json_data["item_data"][key]
    
    global item_data
    for i in temp_item_data:
        item_data[i] = temp_item_data[i]
        
    global mob_data
    mob_data.clear()
    for m in json_data["mob_data"]:
        mob_data.append(m)
    
    change_map()
    

@when("click", selector=".wall")
def change_wall_type(evt):
    '''
    벽 타입 변경
    '''
    posX = float(evt.target.dataset.x)
    posY= float(evt.target.dataset.y)
    currentType = evt.target.dataset.type

    # 벽 변경: type이 없는 항목에서만 동작
    if(wall_type != 'delete'):
        if not currentType: # data-type==''
            wall_data['world'][(posX, posY)]=wall_type
            wall_data['world']=dict(sorted(wall_data['world'].items(), key=lambda x: (x[0][0], x[0][1])))
            evt.target.dataset.type = wall_type
            wall.wall_data = wall_data['world']

    # 벽 삭제: type이 있는 항목에서만 동작
    else:
        if currentType != '':
            del wall_data['world'][(posX, posY)]
            wall.wall_data = wall_data['world']
            # wall_data['world'][(posX, posY)] = ''
            evt.target.dataset.type = ''
            evt.target.style.outline = ''


@when('mouseover', selector='.wall')
def wall_mouse_activation(evt):
    currentType = evt.target.dataset.type

    # 벽 추가: type이 없는 항목에서만 pointer
    if(wall_type != 'delete'):
        if not currentType:
            evt.target.style.cursor = 'pointer'
        else:
            evt.target.style.cursor = 'default'

    # 벽 삭제: type이 있는 항목에서만 pointer
    else:
        if currentType:
            evt.target.style.cursor = 'pointer'
        else:
            evt.target.style.cursor = 'default'

@when('mouseenter', selector='.wall')
def wall_mouse_enter(evt):
    currentType = evt.target.dataset.type

    if(wall_type == 'delete'):
        if currentType:
            evt.target.style.outline = '3px solid red'

@when('mouseleave', selector='.wall')
def wall_mouse_leave(evt):
    currentType = evt.target.dataset.type

    if(wall_type == 'delete'):
        if currentType:
            evt.target.style.outline = ''


# radio 속성을 선택했을 때, wall_type을 변경하는 이벤트 등록
@when("change", selector="input[name='wall-type']")
def change_walltype_input(evt):
    global wall_type
    wall_type = evt.target.value

@when("click", selector="input[name='item']")
def change_item_select(evt):
    if item_select['status'] and evt.target.id == item_select['name']:
        label = js.document.querySelector(f"label[for='{evt.target.id}']")
        label.classList.remove('select')

        item_select['status'] = False
        js.document.querySelector('.wall-container').style.pointerEvents=''

        item_select['name'] = ''
        js.document.querySelector('.world-map').style.cursor='auto'
    elif item_select['status'] and evt.target.id != item_select['name']:
        # 이전 선택 스타일 취소
        if(item_select['name']):
            label = js.document.querySelector(f"label[for='{item_select['name']}']")
            label.classList.remove('select')
            
        js.document.querySelector('.wall-container').style.pointerEvents='none'

        item_select['name'] = evt.target.id
        js.document.querySelector('.world-map').style.cursor=f"url(assets/img/item/{evt.target.id}.png), auto"

        label = js.document.querySelector(f"label[for='{evt.target.id}']")
        label.classList.add('select')
    else: 
        mob_select['status'] = False
        mob_select['name'] = ''
        item_select['status'] = True
        item_select['name'] = evt.target.id
        js.document.querySelector('.wall-container').style.pointerEvents='none'
        js.document.querySelector('.world-map').style.cursor=f"url(assets/img/item/{evt.target.id}.png), auto"

        label = js.document.querySelector(f"label[for='{evt.target.id}']")
        label.classList.add('select')

@when("click",selector=".map-item")
def map_item_add(evt):
    if(item_select['status']):
        # 좌표값 계산
        map_items = js.document.querySelectorAll('.map-item')
        index = 0
        for item in map_items:
            if item == evt.currentTarget:
                break
            index += 1
            
        # index를 통해 x, y 좌표 계산
        x, y = divmod(index, map_data['width'])
        evt.target.style.backgroundColor = ''

        count = 0
        input_count = js.prompt('추가할 아이템 개수를 입력하세요\n(* 추가할 위치에 다른 아이템이 있는 경우 사라집니다.)', '1')

        # 양의 정수이면 count에 저장 / 입력값이 없으면 None 반환 / 입력값이 유효하지 않으면 alert
        if input_count == None:
            return None
        elif not input_count.isdigit() or int(input_count)<0 or input_count=='':
            show_modal_alert('자연수를 입력해주세요')
            return None
        else:
            count = int(input_count)
            on_item = item_data.get((x,y))
            
            if item_data.get((x,y),{}).get('item','')==item_select['name']:
                item_data[(x,y)]['count'] += count
                new_item = Item(x, y, item_select['name'], count)
                new_item.draw()
            else:
                item_data[(x,y)] = {
                    'item': item_select['name'],
                    'count': count
                }
                new_item = Item(x, y, item_select['name'], count)
                new_item.draw()

        item_select['status']=False
        label = js.document.querySelector(f"label[for='{item_select['name']}']")
        label.classList.remove('select')
        item_select['name']=''

        js.document.querySelector('.wall-container').style.pointerEvents=''
        js.document.querySelector('.world-map').style.cursor='auto'

# mob
@when("click", selector="input[name='mob']")
def change_mob_select(evt):
    if mob_select['status'] and evt.target.id == mob_select['name']:
        label = js.document.querySelector(f"label[for='{evt.target.id}']")
        label.classList.remove('select')

        mob_select['status'] = False
        js.document.querySelector('.wall-container').style.pointerEvents=''

        mob_select['name'] = ''
        js.document.querySelector('.world-map').style.cursor='auto'
    elif mob_select['status'] and evt.target.id != mob_select['name']:
        # 이전 선택 스타일 취소
        if(mob_select['name']):
            label = js.document.querySelector(f"label[for='{mob_select['name']}']")
            label.classList.remove('select')
            
        js.document.querySelector('.wall-container').style.pointerEvents='none'

        mob_select['name'] = evt.target.id
        js.console.log('url',f"assets/img/characters/{evt.target.id}-0.png")
        js.document.querySelector('.world-map').style.cursor= f"url(assets/img/characters/{evt.target.id}-0.png)"

        label = js.document.querySelector(f"label[for='{evt.target.id}']")
        label.classList.add('select')
    else: 
        item_select['status'] = False
        item_select['name'] = ''
        mob_select['status'] = True
        mob_select['name'] = evt.target.id
        js.document.querySelector('.wall-container').style.pointerEvents='none'
        js.document.querySelector('.world-map').style.cursor=f"url(assets/img/characters/{evt.target.id}-0.png), auto"

        label = js.document.querySelector(f"label[for='{evt.target.id}']")
        label.classList.add('select')

@when("click",selector=".map-item")
def mob_add(evt):
    if(mob_select['status']):
        # 좌표값 계산
        map_items = js.document.querySelectorAll('.map-item')
        index = 0
        for item in map_items:
            if item == evt.target:
                break
            index += 1
            
        x, y = divmod(index, map_data['width'])
        if character_exist(x, y) or mob_exist(x, y):
            show_modal_alert('다른 캐릭터 또는 몹이 있습니다.')
            evt.target.style.backgroundColor = ''
            return None
        
        input_name = js.prompt('추가할 몹의 이름을 작성해주세요')
        if input_name == None:
            return None
        elif input_name == "":
            show_modal_alert('이름을 입력해주세요')
            return None

        for m in mob_data:
            if m['name']==input_name:
                show_modal_alert('해당 이름을 갖는 몹이 이미 맵에 존재합니다')
                return None

        name = input_name
        add_mob(x,y,mob_select['name'], name)

        mob_select['status']=False
        label = js.document.querySelector(f"label[for='{mob_select['name']}']")
        label.classList.remove('select')
        mob_select['name']=''

        js.document.querySelector('.wall-container').style.pointerEvents=''
        js.document.querySelector('.world-map').style.cursor='auto'
        
@when('mousemove', selector='.world-map')
def show_tooltip(evt=None):
    if(item_select['status']):
        map_items = js.document.querySelector('.map-items')
        x = evt.clientX - map_items.getBoundingClientRect().left;
        y = evt.clientY - map_items.getBoundingClientRect().top;
        
        tooltip = js.document.querySelector('.mouse-tooltip')
        if not tooltip:
            tooltip = js.document.createElement('div')
            tooltip.setAttribute('class', 'mouse-tooltip')
            img = js.document.createElement('img')
            img.setAttribute('src','assets/img/icon/icon-mouse-click.svg')
            text = js.document.createElement('p')
            text.innerHTML = f'우클릭으로 취소'
            tooltip.appendChild(img)
            tooltip.appendChild(text)
            js.document.querySelector('.map-container').appendChild(tooltip)    
        tooltip.style.left = f"{x+50}px"
        tooltip.style.top = f"{y+20}px"
                
@when('mouseleave', selector='.world-map')
def remove_tooltip(evt=None):
    tooltip = js.document.querySelector('.mouse-tooltip')
    if tooltip:
        tooltip.remove()
        
@when('contextmenu', selector='.world-map')
def cancle_item_add(evt=None):
    if(item_select['status']):
        evt.preventDefault()
        # active된 label이 있으면 active 해제
        label = js.document.querySelector(f"label[for='{item_select['name']}']")
        label.classList.remove('select')

        item_select['status']=False
        item_select['name']=''
        js.document.querySelector('.wall-container').style.pointerEvents=''
        js.document.querySelector('.world-map').style.cursor='auto'
        tooltip = js.document.querySelector('.mouse-tooltip')
        if tooltip:
            tooltip.remove()
            
@when("click", selector="#output-init")
def init_output(evt=None):
    for output_line in js.document.querySelectorAll('.output-item'):
        output_line.remove()
    for liElement in js.document.querySelectorAll('.index-list li'):
        liElement.remove()
    print_data.clear()

@when("click", selector="#output-download")
def init_output(evt=None):
    ''''
    js.document.querySelectorAll('.output-item')에 있는 모든 내용을
    txt 파일로 다운로드 하는 코드
    '''
    js.console.log('다운로드')
    output = js.document.querySelectorAll('.output-item')
    output_text = ''
    for line in output:
        output_text += line.innerHTML + '\n'
    file = js.File.new([output_text], "result.txt", {type: "text/plain"})
    url = js.URL.createObjectURL(file)
    hidden_link = js.document.createElement("a")
    hidden_link.setAttribute("download", "result.txt")
    hidden_link.setAttribute("href", url)
    hidden_link.click()

@when("click", selector=".btn-add-code")
def add_code_sell(evt=None):
    newRepl = js.document.createElement('py-repl')
    newRepl.textContent = ''
    js.document.getElementById('notebookSection').appendChild(newRepl)

@when("click", selector = ".story-list")
def set_story(evt=None):
    # story toggle
    if(evt.target.tagName == 'BUTTON' and evt.target.classList.contains('btn-toggle')):
        storyItems = js.document.querySelectorAll('.story-list>li')
        liElem = evt.target.closest('li')
        liElem.classList.toggle('active')

        for li in storyItems:
            if(li != evt.target.closest('li')):
                li.classList.remove('active')

        if(liElem.classList.contains('active')):
            story_select['index']=list(storyItems).index(evt.target.closest('li'))+1 
        else:
            story_select['index']=0
        init()
        
        idx = story_select['index']
        if idx:
            localData = js.localStorage.getItem(f"{idx}_code")
            code_list = json.loads(localData) if localData else []
            notebookSection = js.document.getElementById('notebookSection')
            notebookSection.innerHTML = ''
            if code_list:
                js.console.log('code list')
                for code in code_list:
                    newRepl = js.document.createElement('py-repl')
                    newRepl.textContent = code
                    notebookSection.appendChild(newRepl)
                    if code == code_list[-1]:
                        newRepl.setAttribute('auto-generate', 'true')
            else:
                newRepl = js.document.createElement('py-repl')
                # 기본코드
                basic_code = story_data[idx].get('basic_code','')
                newRepl.textContent = basic_code
                notebookSection.appendChild(newRepl)

                cms = newRepl.querySelector('.cm-content')
                cm = js.document.createElement('div')
                cm.setAttribute('class', 'cm-activeLine cm-line')
                cm.innerHTML = '<br/>'
                cms.appendChild(cm)

                newRepl.setAttribute('auto-generate', 'true')
    # story submit
    if(evt.target.tagName == 'BUTTON' and evt.target.classList.contains('btn-submit')):
        # 코드 저장 및 정답 확인
        notebookSection = js.document.getElementById('notebookSection')
        codeBlocks = notebookSection.querySelectorAll('py-repl')
        code_list = []
        for codeBlock in codeBlocks:
            cms = codeBlock.querySelector('.cm-content')
            code_list.append(cms.innerText)
        js.localStorage.setItem(f"{story_select['index']}_code", json.dumps(code_list))
        js.localStorage.setItem(f"{story_select['index']}_time", datetime.now().strftime('%Y-%m-%d %H:%M'))
        check_data = {
            'print_data': print_data,
            'say_data': say_data,
            'item_data': item_data,
            'character_data': character_data[0],
            'item':character_data[0]['items'],
            'mob_data': mob_data,
            'code':code_list
        }
        # 인증서 날짜 확인용
        storyChapter = {
            '입문': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            '기초': [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
        };

        solution_flag = True
        solution = story_solution[story_select['index']]

        for key in check_data.keys():
            if key not in solution.keys():
                continue
            
            if key=='print_data' or key=='say_data':
                for s in solution[key]:
                    if not any(s in check for check in check_data[key]):
                        solution_flag = False
                        break

                # TODO: 리스트의 경우 요소를 각각 solution[key]에 추가
                
                if len(solution[key])==1:
                    if check_data[key] and check_data[key][-1] not in solution[key]:
                        solution_flag = False

            elif key=='character_data':
                ch_solution = solution[key]
                ch_check = check_data[key]
                if not all(ch_solution.get(prop, None) == ch_check.get(prop, None) for prop in ch_solution.keys()):
                    solution_flag = False

            elif key=='item':
                if not solution[key]==check_data[key]:
                    solution_flag = False

            elif key=='item_data':
                if not solution[key] == check_data[key]:
                    solution_flag = False 

            elif key=='code':
                for code in solution[key]:
                    if not any(code in checke_code for checke_code in check_data[key]):
                        solution_flag = False
                        break

        if solution_flag==True:
            # TODO: 경고창을 안내창으로 변경
            js.localStorage.setItem(f"{story_select['index']}_check", "정답")
            liElem = evt.target.closest('li')
            liElem.classList.add('submit')
            show_modal_alert('정답입니다.', 'success')

            # solution index가 있는 리스트에 따라서 전체 제출여부를 확인
            # storyChatper의 value를 순회하면서 story_select['index']가 있는지 호가인
            for chapter in storyChapter:
                if story_select['index'] in storyChapter[chapter]:
                    chapter_list = storyChapter[chapter]
                    for idx in chapter_list:
                        if js.localStorage.getItem(f"{idx}_check") != "정답":
                            return None
                    if not (js.localStorage.getItem(f"{chapter}_certif_time")):
                        show_modal_alert(f'{chapter} 챕터의 모든 문제를 풀었습니다.\n인증서를 다운받을 수 있습니다.', 'success')
                        js.localStorage.setItem(f"{chapter}_certif_time",datetime.now().strftime('%Y.%m.%d'))
                    return None
        else:
            show_modal_alert('오답입니다.')
@when("click", selector=".btn-story")
def change_storymode(evt=None):
    if(evt.target.classList.contains('active')):
        story_select['status'] = True
        if not (js.document.querySelector('.story-list>li.active')):
            story_select['index'] = 0
    else:
        story_select['status'] = False
    init()    


@when('click', selector='.btn-close-story')
def story_close(evt=None):
    story_select['status'] = False
    init()

def add_mob(x, y, mob_type, name, directions=0):
    '''
    몹을 추가하는 함수
    순환 참조로 인해 이 함수만 index.html에 있음
    
    테스트 코드:
    add_mob('lion', 4, 4)
    add_mob('py', 3, 3)
    add_mob('binky', 3, 2)
    add_mob('gary', 2, 3)
    '''
    global mob_data
    
    if int(x) != x or int(y) != y or not name:
        alert_error('InvalidSyntax')
        raise InvalidSyntax
    
    if not (0 <= x < map_data['height'] and 0 <= y < map_data['width']):
        alert_error('OutOfWorld')
        raise OutOfWorld
    
    if mob_type not in mob_info.keys():
        alert_error('InvalidMob')
        raise InvalidMob
        
    if character_exist(x, y) or mob_exist(x, y):
        alert_error('ObstacleExist')
        raise ObstacleExist

    elif name and mob_type:
        for m in mob_data:
            if m['name'] == name:
                alert_error('MobIsExist')
                raise MobIsExist
                
    
    mob = None;
    if mob_type=='lion':
        mob = Mob(x=x, y=y, mob=mob_type, name=name, width=32,height=40,initHp=200)
        mob_data.append(
            {
                'name': name,
                'mob': mob_type,
                'mob_obj': mob,
                'x': x,
                'y': y,
                'directions': 0, # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남),
                'hp':200,
            }
        )
    else: 
        mob = Mob(x=x, y=y, mob=mob_type, name=name, width=32,height=40,initHp=50)
        mob_data.append(
            {
                'name': name,
                'mob': mob_type,
                'mob_obj': mob,
                'x': x,
                'y': y,
                'directions': 0, # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남),
                'hp':50,
            }
        )
    draw_ch = mob.draw()
    draw_map.appendChild(draw_ch)

    return mob

def add_ch(x, y, name):
    global character_data
    
    if int(x) != x or int(y) != y:
        alert_error('InvalidSyntax')
        raise InvalidSyntax

    if name not in character_info.keys():
        alert_error('InvalidCharacter')
        raise InvalidCharacter
    
    if not (0 <= x < map_data['height'] and 0 <= y < map_data['width']):
        alert_error('OutOfWorld')
        raise OutOfWorld
    
    if character_exist(x, y) or mob_exist(x,y):
        alert_error('ObstacleExist')
        raise ObstacleExist

    # character는 중복 미허용
    for c in character_data:
        if c.get('character', '') == name:
            alert_error('CharacterIsExist')
            raise CharacterIsExist
            
    if name == default_character:
        character_data.insert(0, 
            {
                'character': name,
                'character_obj': None,
                'x': x,
                'y': y,
                'directions': 0, # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
                'items': {},
                'hp':100,
                # 'power':10,
            }
        )
    else:
        character_data.append(
            {
                'character': name,
                'character_obj': None,
                'x': x,
                'y': y,
                'directions': 0, # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
                'items': {},
                'hp':100,
                # 'power':10,
            }
        )
    char = Character(x=x, y=y, name=name, width=32, height=40)
    char._set_character_data('character_obj',char)
    draw_ch=char.draw()
    draw_map.appendChild(draw_ch)
    return char


@when("click", selector=".btn-assets")
def item_active(evt=None):
    if item_select['status'] and 'active' not in evt.currentTarget.classList:
            label = js.document.querySelector(f"label[for={item_select['name']}]")
            label.classList.add('select')

# ESC 키로 캐릭터 정보 팝업 닫기
def handle_keydown(evt):
    """
    ESC 키를 누르면 캐릭터 정보 팝업을 닫는 함수
    """
    if evt.key == 'Escape':
        bubble = js.document.querySelector('.character-info-bubble')
        if bubble:
            bubble.remove()

# 전역 keydown 이벤트 리스너 등록
add_event_listener(js.document, 'keydown', handle_keydown)


# 우클릭으로 아이템, 몹, 벽 삭제
def handle_contextmenu_delete(evt):
    """
    우클릭으로 아이템, 몹, 벽을 삭제하는 함수
    - 스토리 모드에서는 삭제 불가
    - 메인 캐릭터(licat)는 삭제 불가
    """
    js.console.log('=== contextmenu event fired ===')
    js.console.log('target:', evt.target)
    js.console.log('target.tagName:', evt.target.tagName)
    js.console.log('target.classList:', list(evt.target.classList))

    # 스토리 모드에서는 삭제 기능 비활성화
    if story_select['status']:
        js.console.log('story mode - return')
        return

    # 아이템 추가 모드일 때는 기존 취소 로직 사용
    if item_select['status'] or mob_select['status']:
        js.console.log('item/mob select mode - return')
        return

    target = evt.target

    # 아이템 삭제 처리
    # .item (이미지), .count (개수), .item-container 모두 처리
    item_container = None
    if target.classList.contains('item-container'):
        js.console.log('direct item-container')
        item_container = target
    elif target.classList.contains('item') or target.classList.contains('count'):
        js.console.log('item or count element')
        # .item 또는 .count의 부모인 .item-container 찾기
        item_container = target.parentElement
        js.console.log('parent:', item_container)
        if item_container:
            js.console.log('parent classList:', list(item_container.classList))
        if item_container and not item_container.classList.contains('item-container'):
            item_container = None
    else:
        # closest로 시도
        js.console.log('trying closest')
        item_container = target.closest('.item-container')

    js.console.log('item_container found:', item_container)

    if item_container:
        evt.preventDefault()
        evt.stopPropagation()

        # 부모 map-item에서 좌표 계산
        map_item = item_container.parentElement
        js.console.log('map_item:', map_item)
        if map_item:
            js.console.log('map_item classList:', list(map_item.classList))
        if map_item and map_item.classList.contains('map-item'):
            map_items = js.document.querySelectorAll('.map-item')
            index = 0
            for item in map_items:
                if item == map_item:
                    break
                index += 1

            x, y = divmod(index, map_data['width'])
            js.console.log(f'coordinates: x={x}, y={y}')

            # item_data에서 삭제
            if (x, y) in item_data:
                js.console.log(f'deleting from item_data: {item_data[(x, y)]}')
                del item_data[(x, y)]

            # UI에서 삭제
            js.console.log('removing item_container from UI')
            item_container.remove()
        return

    # 몹 삭제 처리
    mob_elem = target.closest('.mob')
    if mob_elem:
        evt.preventDefault()
        evt.stopPropagation()

        mob_name = mob_elem.id

        # mob_data에서 삭제
        for m in mob_data[:]:  # 리스트 복사본을 순회
            if m['name'] == mob_name:
                mob_data.remove(m)
                break

        # UI에서 삭제
        mob_elem.remove()
        return

    # 벽 삭제 처리
    wall_elem = target.closest('.wall')
    if wall_elem:
        current_type = wall_elem.dataset.type
        if current_type:  # 벽이 있는 경우에만 삭제
            evt.preventDefault()
            evt.stopPropagation()

            posX = float(wall_elem.dataset.x)
            posY = float(wall_elem.dataset.y)

            # wall_data에서 삭제
            if (posX, posY) in wall_data['world']:
                del wall_data['world'][(posX, posY)]
                wall.wall_data = wall_data['world']

            # UI 업데이트
            wall_elem.dataset.type = ''
            wall_elem.style.outline = ''
        return

def register_contextmenu_listener():
    """
    map-container에 우클릭 이벤트 리스너를 등록하는 함수
    맵이 재생성될 때 호출해야 함
    """
    map_container = js.document.querySelector('.map-container')
    if map_container:
        add_event_listener(map_container, 'contextmenu', handle_contextmenu_delete)

# 초기 map-container에 우클릭 이벤트 리스너 등록
register_contextmenu_listener()
