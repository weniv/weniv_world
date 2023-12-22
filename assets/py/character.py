import js
from js import setTimeout
from pyodide.ffi import create_once_callable

from built_in_functions import print, say, _show_modal
from coordinate import (
    character_data,
    mob_data,
    map_data,
    item_data,
    valid_items,
    edible_items,
    skills,
    wall_blocked,
    wall_data,
    running_speed,
)
from item import Item
from error import *

class Character:
    def __init__(
        self,
        x,
        y,
        name,
        directions=0,
        width=100,
        height=33,
        initHp=100,
        dropRate=0.1,
        power=10,
        initMp=100,
        rotate=0,
    ):
        self.x = x
        self.y = y
        self.name = name
        self.directions = directions
        self.width = width
        self.height = height
        self.initHp = initHp
        self.dropRate = dropRate
        self.power = power
        self.hp = initHp
        self.initHp=initHp
        self.mp = initMp
        self.initMp = initMp
        self.img = f"assets/img/characters/{name}-0.png"
        self.running_time = 0
        self.rotate = rotate

    def draw(self):
        """
        x좌표, y좌표에 character를 생성하는 함수
        """
        character = js.document.createElement("div")
        character.setAttribute("class", "character")
        character.classList.add(f"{self.name}")
        character.style.backgroundImage = f'url("assets/img/characters/{self.name}-{self.directions}.png")'
        character.style.transition = f"all {running_speed}s"
        # character.style.width = f"{self.width}px"
        # character.style.height = f"{self.height}px"
        hp = self.draw_hp()
        character.appendChild(hp)
        mp = self.draw_mp()
        character.appendChild(mp)
        # next value(px) : (-1, -3), (-33, -1), (-65, -2), (-97, -3), (-129, -2), (-161, -1), (-193, -2)
        character.style.top = f"{self.x * 100 + 2 + (50 - 32)}px"
        character.style.left = f"{self.y * 100 + 2 + (50 - 32)}px"
        
        finder = False
        
        for c in character_data:
            if c.get('character', '') == self.name:
                c["x"] = self.x
                c["y"] = self.y
                c["directions"] = self.directions
                c["items"] = {}
                c["hp"]=self.hp
                c["power"]=self.power
                c["mp"]=self.mp
                finder = True
        if not finder:
            character_data.append(
                {
                    "character": self.name,
                    "x": self.x,
                    "y": self.y,
                    "directions": self.directions,
                    "items": {},
                    "hp":f"{self.hp}",
                    "power":f"{self.power}",
                    "mp":f"{self.mp}"
                }
            )
        return character
    
    def draw_hp(self):
        hp_container = js.document.getElementById(f'hp-{self.name}')
        if not hp_container:
            hp_container = js.document.createElement("div")
            hp_container.setAttribute('class','state-container hp')
            hp_container.setAttribute('id',f'hp-{self.name}')
        hp = hp_container.querySelector(".bar")
        if not hp:
            hp = js.document.createElement("div")
            hp.setAttribute('class','bar')
            hp_container.appendChild(hp)
        hp.style.transform=f"scaleX({self.hp/self.initHp})"
        text = hp_container.querySelector('.text')
        if not text:
            text = js.document.createElement('span')
            text.setAttribute('class','text')
            hp_container.appendChild(text)
        text.innerText = f"{self.hp}/{self.initHp}"
        
        return hp_container      
    
    def draw_mp(self):
        mp_container = js.document.getElementById(f'mp-{self.name}')
        if not mp_container:
            mp_container = js.document.createElement("div")
            mp_container.setAttribute('class','state-container mp')
            mp_container.setAttribute('id',f'mp-{self.name}')
        mp = mp_container.querySelector(".bar")
        if not mp:
            mp = js.document.createElement("div")
            mp.setAttribute('class','bar')
            mp_container.appendChild(mp)
        mp.style.transform=f"scaleX({self.mp/self.initMp})"
        
        text = mp_container.querySelector('.text')
        if not text:
            text = js.document.createElement('span')
            text.setAttribute('class','text')
            mp_container.appendChild(text)
        text.innerText = f"{self.mp}/{self.initMp}"
        return mp_container

    def say(self, text="", speech_time=5000):
        """
        캐릭터 위에 말풍선과 함께 출력하는 함수
        """
        c = js.document.querySelector(f".{self.name}")
        speech_bubble = js.document.createElement("div")
        speech_bubble.setAttribute("class", "speech-bubble")
        speech_bubble.style.top = "-50px"
        speech_bubble.style.left = "50px"
        speech_bubble.style.zIndex = "20"
        speech_bubble.innerHTML = f"{text}"
        c.appendChild(speech_bubble)
        setTimeout(
            create_once_callable(lambda: (c.removeChild(speech_bubble))), speech_time
        )

    def set_speed(self, speed):
        c = js.document.querySelector(f".{self.name}")
        c.style.transition = f"all {speed}s"
        global running_speed
        running_speed = speed

    
    def move(self):
        self.running_time += 1000 * running_speed
        self._move()
        
        
    def _move(self):
        x = self.x
        y = self.y
        directions = self.directions
        error_check = ''

        # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
        nx, ny = x, y
        if directions == 0:
            ny = y + 1
        elif directions == 1:
            nx = x - 1
            error_check=self._movable(x, y, x - 1, y)
        elif directions == 2:
            ny = y - 1
        elif directions == 3:
            nx = x + 1

        error_check=self._movable(x, y, nx, ny)
        if error_check:
            setTimeout(create_once_callable(lambda: alert_error(error_check)), self.running_time)
            setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)
            
            if error_check == 'OutOfWorld':
                raise OutOfWorld
            elif error_check == 'WallIsExist':
                raise WallIsExist
            elif error_check == 'ObstacleExist':
                raise ObstacleExist
        
        self.x = nx
        self.y = ny
        self._set_character_data("x",nx)
        self._set_character_data("y",ny)
        
        setTimeout(create_once_callable(lambda: (self._move_animation(x, y, directions))), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)

        
    def _move_animation(self, x, y, directions):
        c = js.document.querySelector(f".{self.name}")
        if directions == 0:
            c.style.left = f"{(y + 1) * 100 + 2 + (50 - 32)}px"
            self.draw_move_line(x, y, x, y + 1, directions)
        elif directions == 1:
            c.style.top = f"{(x - 1) * 100 + 2 + (50 - 32)}px"
            self.draw_move_line(x, y, x-1, y, directions)
        elif directions == 2:
            c.style.left = f"{(y - 1) * 100 + 2 + (50 - 32)}px"
            self.draw_move_line(x, y, x, y - 1, directions)
        elif directions == 3:
            c.style.top = f"{(x + 1) * 100 + 2 + (50 - 32)}px"
            self.draw_move_line(x, y, x + 1, y, directions)
 
        
    def _movable(self, x, y, nx, ny):
        if self._out_of_world(nx, ny):
            return 'OutOfWorld'

        if self._wall_exist(x, y, nx, ny):
            return 'WallIsExist'
        
        if self._obstacle_exist(nx, ny):
            return 'ObstacleExist'

    def _out_of_world(self, x, y):
        if not (0 <= x < map_data["height"] and 0 <= y < map_data["width"]):
            return True
        return False
    
    def _wall_exist(self, x, y, nx, ny):
        global wall_data
        wall_x = float((x + nx) / 2)
        wall_y = float((y + ny) / 2)
        
        if wall_data['world'].get((wall_x, wall_y), None) in (wall_blocked+['door']):
            return True
        return False
    
    def _obstacle_exist(self, nx, ny):
        global character_data
        global mob_data
        
        if any(obj.get('x', None) == nx and obj.get('y', None) == ny for obj in character_data) or any(obj.get('x', None) == nx and obj.get('y', None) == ny for obj in mob_data):
            return True
        return False
        
    def _pos_to_wall(self, x, y):
        # position 좌표계를 벽을 놓을 수 있는 좌표계로 변환
        return 2 * x + 1, 2 * map_data["height"] - 1 - 2 * y

    def turn_left(self):
        self.running_time += 1000 * running_speed
        self._turn_left()
        
    def _turn_left(self):
        directions = self.directions
        
        nd = directions + 1
        if nd > 3:
            nd = 0
        
        self.directions=nd
        self._set_character_data("directions",nd)
       
        setTimeout(create_once_callable(lambda: (self._turn_left_animation(directions))), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)

    def _turn_left_animation(self, directions):
        c = js.document.querySelector(f".{self.name}")
        c.style.transformOrigin = "center center"

        if directions == 0:
            c.style.backgroundImage = (
                f'url("assets/img/characters/{self.name}-{directions+1}.png")'
            )
        elif directions == 1:
            c.style.backgroundImage = (
                f'url("assets/img/characters/{self.name}-{directions+1}.png")'
            )
        elif directions == 2:
            c.style.backgroundImage = (
                f'url("assets/img/characters/{self.name}-{directions+1}.png")'
            )
        elif directions == 3:
            c.style.backgroundImage = f'url("assets/img/characters/{self.name}-0.png")'

    def attack(self, skill='claw-yellow'):
        self.running_time += 1000 * running_speed
        
        if skill not in skills.keys():
            alert_error('InvalidSkill')
            raise InvalidSkill
        
        self._attack(skill)
        
    def _attack(self, skill):
        x = self.x
        y = self.y
        directions = self.directions
        
        if skills[skill]['mana'] > self.mp:
            alert_error('NotEnoughMana')
            raise NotEnoughMana

        if self.typeof_wall():
            alert_error('WallIsExist')
            raise WallIsExist
            
        # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
        nx, ny = x, y
        if directions == 0:
            ny = y + 1
        elif directions == 1:
            nx = x - 1
        elif directions == 2:
            ny = y - 1
        elif directions == 3:
            nx = x + 1
            
        if not 0<=nx<map_data["height"] or not 0<=ny<map_data["width"]:
            alert_error('OutOfWorld')
            raise OutOfWorld
            
        m_obj=None
        mob_name=''
        for m in mob_data:
            if (m['x'],m['y'])==(nx,ny):
                m_obj = m['mob_obj']
                mob_name = m['name']
                m['hp'] -= skills[skill]['power']
                if(m['hp']<=0):
                    mob_data.remove(m)
                    break
        
        self.mp -= skills[skill]['mana']
        self._set_character_data("mp",self.mp)
        
            
        setTimeout(create_once_callable(lambda: (self.draw_attack(x,y,nx,ny, skill))), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)
        setTimeout(create_once_callable(lambda: self._mob_hp_animation(m_obj, mob_name, skill)), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)
        
        setTimeout(create_once_callable(lambda: self._mp_animation()), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)
        
    def draw_attack(self, x, y, x2, y2, skill):
        attack = js.document.createElement("div")
        attack.className = "attack"
        attack.style.position = "absolute"
        attack.style.width = "32px"
        attack.style.height = "36px"
        attack.style.left = f"{y2 * 100 + 40}px"
        attack.style.top = f"{x2 * 100 + 40}px"
        attack.style.backgroundImage = f'url("assets/img/weapon/{skill}.png")'
        attack.style.backgroundRepeat = "no-repeat"
        map = js.document.querySelector(".map-container")
        map.appendChild(attack)
        setTimeout(create_once_callable(lambda: (map.removeChild(attack))), 1000)


    def _mob_hp_animation(self, mob_obj, mob_name, skill):
        if mob_name:
            mob = js.document.querySelector(f'#{mob_name}.mob')
        if mob_obj and mob:
            mob_obj.hp -= skills[skill]["power"]
            mob_obj.draw_hp()
            if(mob_obj.hp<=0):
                setTimeout(create_once_callable(lambda: self._remove_mob(mob_obj,mob)), 1000)
              
    def _hp_animation(self):
        self.draw_hp()
        
    def _mp_animation(self):
        self.draw_mp()
                
    def _remove_mob(self, mob_obj, mob):
        if mob:
            mob.parentNode.removeChild(mob)
        del mob_obj

    def pick(self):
        self.running_time += 1000 * running_speed
        self._pick()
     
    def _pick(self):
        """
        발 아래 아이템을 주워서 아이템을 가지고 있는지 확인하고,
        가지고 있으면 주인공이 소유한 아이템 개수를 1 증가시키고, 맵에 있는 아이템은 1 감소시킨다.

        모든 아이템이 다 감소되면 document에서 해당 아이템을 삭제한다.
        """
        x = self.x
        y = self.y
        item = item_data.get((x, y))
        
        if item:
            item_count = item.get("count", 0)
            item_count -= 1
            item["count"] = item_count
            item_data[(x, y)] = item
          
            item_list = self._get_character_data("items")
            if item["item"] in item_list.keys():
                item_list[item["item"]] += 1
            else:
                item_list[item["item"]] = 1
            
            if item_count == 0:
                item_data.pop((x, y))
                
            setTimeout(create_once_callable(lambda: (self._pick_animation(x, y ,item_count))), self.running_time)
            setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)

        else:
            setTimeout(create_once_callable(lambda: alert_error('ItemIsNotExist')), self.running_time)
            setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)
            raise ItemIsNotExist
            

    def _pick_animation(self, x, y, item_count):
            if item_count == 0:
                map_items = js.document.querySelectorAll(".map-item")
                index = map_data["width"] * x + y
                target = map_items[index]
                target.removeChild(target.querySelector(".item-container"))
            else:
                js.document.querySelector(f".count{x}{y}").innerHTML = item_count
        
    def put(self, item_name):
        self.running_time += 1000 * running_speed
        
        if item_name not in valid_items:
            alert_error('InvalidItem')
            raise InvalidItem
        self._put(item_name)
        

    def _put(self, item_name):
        """
        주인공 발 아래 동일한 아이템을 내려놓는 함수
        """
        x = self.x
        y = self.y
        item = self.check_bottom()
        item_list = self._get_character_data("items")
        find_item_from_character =item_list.get(item_name, 0)
        
        # 발 아래 아이템이 없을 경우
        if not item:
            if find_item_from_character > 0:
                
                item_list[item_name] -= 1
                if item_list[item_name] == 0:
                    item_list.pop(item_name)
                
                item_data[(x,y)]= {"item":item_name,"count":1}
                setTimeout(create_once_callable(lambda: (self._put_animation(item, x,y,item_name,1))), self.running_time)
                setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)
                
                
            else:
                setTimeout(create_once_callable(lambda: alert_error('ItemIsNotExist')), self.running_time)
                setTimeout(create_once_callable(lambda: self.init_time()), self.running_time) 
                raise ItemIsNotExist
        else:
            # 발 아래 아이템이 있다면
            bottom_item_name = item_data[(x, y)]["item"]

            if bottom_item_name != item_name and find_item_from_character > 0:
                setTimeout(create_once_callable(lambda: alert_error('AnotherItemIsExist')), self.running_time)
                setTimeout(create_once_callable(lambda: self.init_time()), self.running_time) 
                raise AnotherItemIsExist

            # 주인공 발 아래 아이템과 동일한 아이템이 있다면
            elif find_item_from_character > 0 and bottom_item_name == item_name:
                item_list[item_name] -= 1

                if item_list[item_name] == 0:
                    item_list.pop(item_name)
                    item_data[(x, y)]["count"] += 1
                setTimeout(create_once_callable(lambda: (self._put_animation(item,x,y,item_name,item_data[(x, y)]["count"]))), self.running_time)
                setTimeout(create_once_callable(lambda: self.init_time()), self.running_time) 
            
                
                    
    def _put_animation(self,bottom_item, x, y, item_name,count=1):
        if not bottom_item:
            item = Item(x, y, item_name, count)
            item.draw()
        else:
            js.document.querySelector(f".count{x}{y}").innerHTML = count
            
        pass
    def check_bottom(self):
        """
        주인공 발 아래 아이템이 있는지 확인하는 함수
        """

        x = self.x
        y = self.y
        item = item_data.get((x, y))

        return True if item else False

    def show_item_global(self):
        """
        현재 맵에 있는 모든 아이템을 보여주는 함수
        """
        carried_items = []
        for item in item_data.values():
            carried_items.append(item["item"])
        return carried_items

    def show_item(self):
        """
        주인공이 가지고 있는 아이템을 보여주는 함수
        """
        return None

    def draw_move_line(self, x, y, next_x, next_y, directions):
        """
        주인공이 이동할 경로를 그려주는 함수
        """
        line = js.document.createElement("div")

        line.className = "line"
        line.style.position = "absolute"
        line.style.animation = f"line-opacity {running_speed * 2}s ease-in-out"
        line.style.left = f"{y * 100 + 60}px"
        line.style.top = f"{x * 100 + 60}px"
        line.style.width = "100px"
        line.style.height = "2px"
        # line.style.border = '1px solid #ccc'
        line.style.backgroundColor = "#ccc"
        line.style.transformOrigin = "top left"

        # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
        if directions == 0:
            line.style.rotate = "0deg"
        elif directions == 1:
            line.style.rotate = "-90deg"
        elif directions == 2:
            line.style.rotate = "-180deg"
        elif directions == 3:
            line.style.rotate = "90deg"

        line.style.boxSizing = "border-box"
        line.style.zIndex = "1"

        js.document.querySelector(".map-container").appendChild(line)

    def front_is_clear(self):
        """
        캐릭터가 바라보는 방향의 앞이 비어있는지 확인하는 함수
        """
        return self._is_clear("front")

    def left_is_clear(self):
        """
        캐릭터가 바라보는 방향의 왼쪽이 비어있는지 확인하는 함수
        """
        return self._is_clear("left")

    def right_is_clear(self):
        """
        캐릭터가 바라보는 방향의 오른쪽이 비어있는지 확인하는 함수
        """
        return self._is_clear("right")

    def back_is_clear(self):
        """
        캐릭터가 바라보는 방향의 뒤가 비어있는지 확인하는 함수
        """
        return self._is_clear("back")

    def _is_clear(self, input_dir="front"):
        global wall_data
        target_direction = self.directions
        x = self.x
        y = self.y
        
        if input_dir == "front":
            pass
        elif input_dir == "left":
            target_direction += 1
        elif input_dir == "back":
            target_direction += 2
        elif input_dir == "right":
            target_direction += 3

        if target_direction > 3:
            target_direction -= 4

        nx, ny = x, y
        if target_direction == 0:  # 동
            ny = y + 1
        elif target_direction == 1:  # 북
            nx = x - 1
        elif target_direction == 2:  # 서
            ny = y - 1
        elif target_direction == 3:  # 남
            nx = x + 1
            
        
        
        if self._out_of_world(nx, ny) or self._wall_exist(x, y, nx, ny) or self._obstacle_exist(nx, ny):
            return False
        return True

    def directions(self):
        pass

    def init_time(self):
        self.running_time = 0

    def open_door(self):
        self.running_time += 1000 * running_speed
        self._open_door()

    def _open_door(self):
        wall_pos = self._front_wall()
        if self.typeof_wall() == "door":
            
            # self._set_wall_data(wall_pos, "")
            del wall_data['world'][wall_pos]
            setTimeout(create_once_callable(lambda: (self._open_door_animation(wall_pos))), self.running_time)
            setTimeout(create_once_callable(lambda: self.init_time()), self.running_time) 
            
            

        elif self.typeof_wall() != "":
            setTimeout(create_once_callable(lambda: alert_error('CannotOpenWall')), self.running_time)
            setTimeout(create_once_callable(lambda: self.init_time()), self.running_time) 
            raise CannotOpenWall
            

    def _open_door_animation(self,wall_pos):
        self._set_wall_screen(wall_pos,"")

    def typeof_wall(self):
        global wall_data

        pos = self._front_wall()
        if not 0<=pos[0]<map_data["height"] or not 0<=pos[1]<map_data["width"]:
        # if pos not in wall_data['world'].keys():
            return 'OutOfWorld'
            
        return wall_data["world"].get(pos, None)

    def _front_wall(self):
        directions = self.directions

        if directions == 0:  # 동
            posX, posY = (self.x, self.y + 0.5)
        elif directions == 1:  # 북
            posX, posY = (self.x - 0.5, self.y)
        elif directions == 2:  # 서
            posX, posY = (self.x, self.y - 0.5)
        elif directions == 3:  # 남
            posX, posY = (self.x + 0.5, self.y)

        return (posX, posY)

    # def _set_wall_data(self, pos, type):
    #     wall_data["world"][pos] = type

    def _set_wall_screen(self, pos, type):
        js.document.querySelector(
            f'.wall[data-x="{pos[0]}"][data-y="{pos[1]}"]'
        ).dataset.type = type
        
    def _set_character_data(self, key, value):
        global character_data
        for c in character_data:
            if c['character']==self.name:
                c[key] = value
                break
    
    def _get_character_data(self, key):
        global character_data
        for c in character_data:
            if c['character']==self.name:
                return c[key]
        return None
    
    def eat(self, item_name):
        self.running_time += 1000 * running_speed
        
        if item_name not in valid_items:
            setTimeout(create_once_callable(lambda: alert_error('InvalidItem')), self.running_time)
            setTimeout(create_once_callable(lambda: self.init_time()), self.running_time) 
            
            
            raise InvalidItem
        
        if item_name not in edible_items.keys():
            setTimeout(create_once_callable(lambda: alert_error('InedibleItem')), self.running_time)
            setTimeout(create_once_callable(lambda: self.init_time()), self.running_time) 
            raise InedibleItem
        
        item_data = self._get_character_data('items')
        if item_name not in item_data.keys():
            setTimeout(create_once_callable(lambda: alert_error('ItemIsNotExist')), self.running_time)
            setTimeout(create_once_callable(lambda: self.init_time()), self.running_time) 
            raise ItemIsNotExist
        

        say("냠냠")
        if item_data[item_name]==1:
            del item_data[item_name]
        else:
            item_data[item_name]-=1
        
        item_hp = edible_items[item_name].get('hp',0)
        item_mp = edible_items[item_name].get('mp',0)
        if self.hp + item_hp > self.initHp:
            self.hp = self.initHp
        else: 
            self.hp += item_hp
            
        if self.mp + item_mp > self.initMp:
            self.mp=self.initMp
        else:
            self.mp += item_mp
            
        self._set_character_data("hp",self.hp)
        self._set_character_data("mp",self.mp)
        
        setTimeout(create_once_callable(lambda: self._hp_animation()), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)
        
        setTimeout(create_once_callable(lambda: self._mp_animation()), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)
       