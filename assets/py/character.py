import js
from js import setTimeout
from pyodide.ffi import create_once_callable

from built_in_functions import print, say
from coordinate import (
    character_data,
    mob_data,
    map_data,
    item_data,
    blockingWallType,
    wall_data,
    running_speed,
)
from item import Item
from error import OutOfWorld, WallIsExist, CannotOpenWall


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
        # hp = self.draw_hp()
        # character.appendChild(hp)
        # next value(px) : (-1, -3), (-33, -1), (-65, -2), (-97, -3), (-129, -2), (-161, -1), (-193, -2)
        character.style.top = f"{self.y * 100 + 2 + (50 - 32)}px"
        character.style.left = f"{self.x * 100 + 2 + (50 - 32)}px"
        
        finder = False
        
        for c in character_data:
            if c["character"] == self.name:
                c["x"] = self.x
                c["y"] = self.y
                c["directions"] = self.directions
                c["items"] = {}
                c["hp"]=self.hp
                c["power"]=self.power
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
                    "power":f"{self.power}"
                }
            )
        return character
    
    def draw_hp(self):
        hp_container = js.document.getElementById(f'hp-{self.name}')
        if not hp_container:
            hp_container = js.document.createElement("div")
            hp_container.setAttribute('class','hp-container')
            hp_container.setAttribute('id',f'hp-{self.name}')
        hp = hp_container.querySelector(".hp")
        if not hp:
            hp = js.document.createElement("div")
            hp.setAttribute('class','hp')
            hp_container.appendChild(hp)
        hp.style.width = f"{self.hp/self.initHp*100}%"
        
        text = hp_container.querySelector('.hp-text')
        if not text:
            text = js.document.createElement('span')
            text.setAttribute('class','hp-text')
            hp_container.appendChild(text)
        text.innerText = f"{self.hp}/{self.initHp}"
        
        return hp_container      
        

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

    
    # TODO: 경로를 dict에 저장해놓고, dict에 따라 keyframes animation을 만드는 작업 필요. 애니메이션이 한 번에 움직이기 때문.
    def move(self):
        self.running_time += 1000 * running_speed
        self._move()
        
        
    def _move(self):
        x = character_data[0]["x"]
        y = character_data[0]["y"]
        directions = character_data[0]["directions"]
        error_check = ''
        # js.alert(f"현재 x위치= {x} 현재 y위치 = {y} 방향 = {directions}")
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
            setTimeout(create_once_callable(lambda: self._alert_error(error_check)), self.running_time)
            return None
        
        character_data[0]["x"] = nx
        self.x = character_data[0]["x"]
        character_data[0]["y"] = ny
        self.y = character_data[0]["y"]
        
        setTimeout(create_once_callable(lambda: (self._move_animation(x, y, directions))), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)

        
    def _move_animation(self, x, y, directions):
        c = js.document.querySelector(f".{self.name}")
        # directions = character_data[0]["directions"]

        # x = character_data[0]["x"]
        # y = character_data[0]["y"]
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
        # 맵을 벗어나는지 확인
        if self._out_of_world(nx, ny):
            return 'OutOfWorld'

        # 이동 경로에 벽이 있는지 확인
        if self._wall_exist(x, y, nx, ny):
            return 'WallIsExist'
        
        if self._character_exist(nx, ny):
            return 'CharacterIsExist'

    def _out_of_world(self, x, y):
        if not (0 <= x < map_data["height"] and 0 <= y < map_data["width"]):
            return True
        return False
    
    def _wall_exist(self, x, y, nx, ny):
        global wall_data
        wall_x = float((x + nx) / 2)
        wall_y = float((y + ny) / 2)
        
        if wall_data['world'].get((wall_x, wall_y), None) in (blockingWallType+['door']):
            return True
        return False
    
    def _character_exist(self, nx, ny):
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
        directions = character_data[0]["directions"]
        
        self._turn_left()
        
    def _turn_left(self):
        directions = character_data[0]["directions"]
        if directions == 0:
            character_data[0]["directions"] += 1
        elif directions == 1:
            character_data[0]["directions"] += 1
        elif directions == 2:
            character_data[0]["directions"] += 1
        elif directions == 3:
            character_data[0]["directions"] = 0
            
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

    def attack(self):
        self.running_time += 1000 * running_speed
        self._attack()
        
    def _attack(self):
        directions = character_data[0]["directions"]

        x = character_data[0]["x"]
        y = character_data[0]["y"]

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
            js.alert('공격이 맵을 벗어납니다.')
            raise OutOfWorld
            
        m_obj=None
        for m in mob_data:
            if (m['x'],m['y'])==(nx,ny):
                m_obj = m['mob_obj']
                m['hp']-=self.power
                if(m['hp']<=0):
                    mob_data.remove(m)
                    break
            
        setTimeout(create_once_callable(lambda: (self.draw_attack(x,y,nx,ny))), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)
        setTimeout(create_once_callable(lambda: self._attack_hp_animation(m_obj,m['name'])), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)
        
    def draw_attack(self, x, y, x2, y2, name="claw-yellow"):
        attack = js.document.createElement("div")
        attack.className = "attack"
        attack.style.position = "absolute"
        attack.style.width = "32px"
        attack.style.height = "36px"
        attack.style.left = f"{y2 * 100 + 40}px"
        attack.style.top = f"{x2 * 100 + 40}px"
        attack.style.backgroundImage = f'url("assets/img/weapon/{name}.png")'
        attack.style.backgroundRepeat = "no-repeat"
        map = js.document.querySelector(".map-container")
        map.appendChild(attack)
        setTimeout(create_once_callable(lambda: (map.removeChild(attack))), 1000)


    def _attack_hp_animation(self, mob_obj, mob_name):
        mob = js.document.querySelector(f'#{mob_name}.mob')
        if mob_obj and mob:
            mob_obj.hp -= self.power
            # mob_obj.draw_hp()
            if(mob_obj.hp<=0):
                setTimeout(create_once_callable(lambda: self._remove_mob(mob_obj,mob)), 1000)
                
    def _remove_mob(self, mob_obj, mob):
        if mob:
            mob.parentNode.removeChild(mob)
        del mob_obj


    def pick(self):
        self.running_time += 1000 * running_speed
        self._pick()
        # setTimeout(create_once_callable(lambda: (self._pick())), self.running_time)
        # setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)

    def _pick(self):
        """
        발 아래 아이템을 주워서 아이템을 가지고 있는지 확인하고,
        가지고 있으면 주인공이 소유한 아이템 개수를 1 증가시키고, 맵에 있는 아이템은 1 감소시킨다.

        모든 아이템이 다 감소되면 document에서 해당 아이템을 삭제한다.
        """
        
        x = character_data[0]["x"]
        y = character_data[0]["y"]
        item = item_data.get((x, y))
        
        if item:
            item_count = item.get("count", 0)
            item_count -= 1
            item["count"] = item_count
            item_data[(x, y)] = item
            # TODO: 0번째에서 꺼내는 것이 아니라 자신의 아이템에서 꺼내야 함.
            if item["item"] in character_data[0]["items"].keys():
                character_data[0]["items"][item["item"]] += 1
            else:
                character_data[0]["items"][item["item"]] = 1
            
            if item_count == 0:
                item_data.pop((x, y))
                
            setTimeout(create_once_callable(lambda: (self._pick_animation(x, y ,item_count))), self.running_time)

        else:
            setTimeout(create_once_callable(lambda: (self._alert_error('NoItem'))), self.running_time)
            

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
        self._put(item_name)
        

    def _put(self, item_name):
        """
        주인공 발 아래 동일한 아이템을 내려놓는 함수
        """
        x = character_data[0]["x"]
        y = character_data[0]["y"]
        item = self.check_bottom()
        find_item_from_character = character_data[0]["items"].get(item_name, 0)
        
        # 발 아래 아이템이 없을 경우,
        if not item:
            if find_item_from_character > 0:
                
                character_data[0]["items"][item_name] -= 1
                if character_data[0]["items"][item_name] == 0:
                    character_data[0]["items"].pop(item_name)
                
                item_data[(x,y)]= {"item":item_name,"count":1}
                setTimeout(create_once_callable(lambda: (self._put_animation(item, x,y,item_name,1))), self.running_time)
                
            else:
                setTimeout(create_once_callable(lambda: (self._alert_error('NoItem'))), self.running_time)
        else:
            # 발 아래 아이템이 있다면
            bottom_item_name = item_data[(x, y)]["item"]

            if bottom_item_name != item_name and find_item_from_character > 0:
                setTimeout(create_once_callable(lambda: (self._alert_error('AnotherItemInBottom'))), self.running_time)
                

            # 주인공 발 아래 아이템과 동일한 아이템이 있다면
            elif find_item_from_character > 0 and bottom_item_name == item_name:
                character_data[0]["items"][item_name] -= 1

                if character_data[0]["items"][item_name] == 0:
                    character_data[0]["items"].pop(item_name)
                    item_data[(x, y)]["count"] += 1
                setTimeout(create_once_callable(lambda: (self._put_animation(item,x,y,item_name,item_data[(x, y)]["count"]))), self.running_time)
                    
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
        x = character_data[0]["x"]
        y = character_data[0]["y"]

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

    def draw_move_line(self, x, y, next_x, next_y,directions):
        """
        주인공이 이동할 경로를 그려주는 함수
        """
        line = js.document.createElement("div")
        # directions = character_data[0]["directions"]

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

    def _is_clear(self, target="front"):
        # target_direction = self.directions
        global wall_data
        target_direction = character_data[0]["directions"]

        if target == "front":
            pass
        elif target == "left":
            target_direction += 1
        elif target == "back":
            target_direction += 2
        elif target == "right":
            target_direction += 3

        if target_direction > 3:
            target_direction -= 4

        posX, posY = (0, 0)

        # 캐릭터 기준 벽은 0.5만큼 떨어져있음
        if target_direction == 0:  # 동
            posX, posY = (self.x, self.y + 0.5)
        elif target_direction == 1:  # 북
            posX, posY = (self.x - 0.5, self.y)
        elif target_direction == 2:  # 서
            posX, posY = (self.x, self.y - 0.5)
        elif target_direction == 3:  # 남
            posX, posY = (self.x + 0.5, self.y)

        if (posX, posY) not in wall_data["world"].keys():
            return False

        if wall_data["world"][(posX, posY)]:
            return False
        return True

    def directions(self):
        pass

    def init_time(self):
        self.running_time = 0

    def open_door(self):
        self.running_time += 1000 * running_speed
        self._open_door()
        # setTimeout(create_once_callable(lambda: (self._open_door())), self.running_time)
        # setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)

    def _open_door(self):
        wall_pos = self._front_wall()
        if self.typeof_wall() == "door":
            
            self._set_wall_data(wall_pos, "")
            setTimeout(create_once_callable(lambda: (self._open_door_animation(wall_pos))), self.running_time)

        elif self.typeof_wall() != "":
            setTimeout(create_once_callable(lambda: self._alert_error('CannotOpenDoor')), self.running_time)
            

    def _open_door_animation(self,wall_pos):
        self._set_wall_screen(wall_pos,"")

    def typeof_wall(self):
        global wall_data

        pos = self._front_wall()
        if pos not in wall_data['world'].keys():
            return 'OutOfWorld'
            
        return wall_data["world"][pos]

    def _front_wall(self):
        directions = character_data[0]["directions"]

        if directions == 0:  # 동
            posX, posY = (self.x, self.y + 0.5)
        elif directions == 1:  # 북
            posX, posY = (self.x - 0.5, self.y)
        elif directions == 2:  # 서
            posX, posY = (self.x, self.y - 0.5)
        elif directions == 3:  # 남
            posX, posY = (self.x + 0.5, self.y)

        return (posX, posY)

    def _set_wall_data(self, pos, type):
        wall_data["world"][pos] = type

    def _set_wall_screen(self, pos, type):
        js.document.querySelector(
            f'.wall[data-x="{pos[0]}"][data-y="{pos[1]}"]'
        ).dataset.type = type
        
    def _alert_error(self, error_type):
        if(error_type=='OutOfWorld'):
            js.alert("맵을 벗어납니다.")
            raise OutOfWorld
        elif(error_type=='WallIsExist'):
            js.alert("이런! 벽에 부딪혔습니다.")
            raise WallIsExist
        elif (error_type=='CannotOpenDoor'):
            js.alert('문이 아닌 벽은 열 수 없습니다.')
            raise CannotOpenWall   
        elif(error_type=='NoItem'):
            js.alert('아이템이 없습니다.')
            raise Exception('NoItem')
        elif(error_type=='AnotherItemInBottom'):
            js.alert('다른 아이템이 있습니다.')
            raise Exception('AnotherItemInBottom')
        elif(error_type=='CharacterIsExist'):
            js.alert('이동하려는 위치에 캐릭터가 있습니다.')
            raise Exception('CharacterIsExist')
        else:
            js.alert('new error',error_type)
            raise Exception('new error',error_type)