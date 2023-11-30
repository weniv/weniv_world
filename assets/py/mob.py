import js
from js import setTimeout
from pyodide.ffi import create_once_callable

from built_in_functions import print, say
from coordinate import (
    character_data,
    default_character,
    mob_data,
    map_data,
    item_data,
    blockingWallType,
    wall_data,
    running_speed,
)
from item import Item
from error import OutOfWorld, WallIsExist, CannotOpenWall


class Mob:
    def __init__(
        self,
        x,
        y,
        mob,
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
        self.mob = mob
        self.name = name
        self.directions = directions
        self.width = width
        self.height = height
        self.initHp = initHp
        self.dropRate = dropRate
        self.power = power
        self.hp = initHp
        self.img = f"assets/img/characters/{mob}-0.png"
        self.running_time = 0
        self.rotate = rotate

    def draw(self):
        """
        x좌표, y좌표에 character를 생성하는 함수
        """
        mob = js.document.createElement("div")
        mob.setAttribute("class", "mob")
        mob.classList.add(f"{self.mob}")
        mob.setAttribute('id', self.name)
        mob.style.backgroundImage = f'url("assets/img/characters/{self.mob}-{self.directions}.png")'
        mob.style.transition = f"all {running_speed}s"
        # mob.style.top = f"{self.x * 100 + 2 + (50 - 32)}px"
        # mob.style.left = f"{self.y * 100 + 2 + (50 - 32)}px"
        # hp = self.draw_hp()
        # mob.appendChild(hp)
        
        if self.mob == 'lion':
            mob.style.top = f"{self.x * 100 + 2 + (50 - 32) + 8}px"
            mob.style.left = f"{self.y * 100 + 2 + (50 - 32) + 13}px"
        elif self.mob[:3]=='mob':
            mob.style.top = f"{self.x * 100 + 2 + (50 - 32) + 23}px"
            mob.style.left = f"{self.y * 100 + 2 + (50 - 32) + 21}px"
            
        finder = False
    
        # mob_data = [{"name":"라이언킹", "mob":"lion","x":4,"y":4,"directions":0}]
        for m in mob_data:
            if m["name"] == self.name:
                m["mob"]=self.mob
                m["x"] = self.x
                m["y"] = self.y
                m["directions"] = self.directions
                m["hp"] = self.hp
                m["power"] = self.power
                finder = True
        if not finder:
            mob_data.append(
                {
                    "name": self.name,
                    "mob": self.mob,
                    "x": self.x,
                    "y": self.y,
                    "directions": self.directions,
                    "hp":self.hp,
                    "power":self.power,
                }
            )
        return mob
    
    def draw_hp(self):
        hp_container = js.document.getElementById(f'hp-{self.name}')
        if not hp_container:
            hp_container = js.document.createElement("div")
            hp_container.setAttribute('class','hp-container')
            hp_container.setAttribute('id',f'hp-{self.name}')
        
        hp = hp_container.querySelector('.hp')
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
    

    def set_speed(self, speed):
        m = js.document.getElementById(f"mob-{self.name}")
        m.style.transition = f"all {speed}s"
        global running_speed
        running_speed = speed

    
    # TODO: 경로를 dict에 저장해놓고, dict에 따라 keyframes animation을 만드는 작업 필요. 애니메이션이 한 번에 움직이기 때문.
    def move(self):
        self.running_time += 1000 * running_speed
        self._move()
        
        
    def _move(self):
        x, y= self.x, self.y
        directions = self.directions
        error_check = ''
        # js.alert(f"현재 x위치= {x} 현재 y위치 = {y} 방향 = {directions}")
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
            
        error_check = self._movable(x, y, nx, ny)
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
        self._update_mob_data('x', self.x)
        self._update_mob_data('y', self.y)
       
        setTimeout(create_once_callable(lambda: (self._move_animation(x, y, directions))), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)

        
    def _move_animation(self, x, y, directions):
        c = js.document.querySelector(f"#{self.name}.mob")
       
        if self.mob =='lion':
        #     mob.style.top = f"{self.x * 100 + 2 + (50 - 32) + 8}px"
        #     mob.style.left = f"{self.y * 100 + 2 + (50 - 32) + 13}px"
            if directions == 0:
                c.style.left = f"{(y + 1) * 100 + 2 + (50 - 32) + 13}px"
                self.draw_move_line(x, y, x, y + 1, directions)
            elif directions == 1:
                c.style.top = f"{(x - 1) * 100 + 2 + (50 - 32) + 8}px"
                self.draw_move_line(x, y, x-1, y, directions)
            elif directions == 2:
                c.style.left = f"{(y - 1) * 100 + 2 + (50 - 32) + 13}px"
                self.draw_move_line(x, y, x, y - 1, directions)
            elif directions == 3:
                c.style.top = f"{(x + 1) * 100 + 2 + (50 - 32) + 8}px"
                self.draw_move_line(x, y, x + 1, y, directions)
        
        elif self.mob[:3]=='mob':
            # top = (x+1)*100 + 2 + (50-32) + 23
            # left = (y+1)*100 + 2 + (50-32) + 21
            if directions == 0:
                c.style.left = f"{(y + 1) * 100 + 2 + (50 - 32) + 21}px"
                self.draw_move_line(x, y, x, y + 1, directions)
            elif directions == 1:
                c.style.top = f"{(x - 1) * 100 + 2 + (50 - 32) + 23}px"
                self.draw_move_line(x, y, x-1, y, directions)
            elif directions == 2:
                c.style.left = f"{(y - 1) * 100 + 2 + (50 - 32) + 21}px"
                self.draw_move_line(x, y, x, y - 1, directions)
            elif directions == 3:
                c.style.top = f"{(x + 1) * 100 + 2 + (50 - 32) + 23}px"
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
        
        if wall_data['world'].get((wall_x, wall_y), None) in (blockingWallType+['door']):
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
        
        self.directions += 1
        if(self.directions >= 4):
            self.directions = 0
        self._update_mob_data('directions', self.directions)
        
        setTimeout(create_once_callable(lambda: (self._turn_left_animation(directions))), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)

    def _turn_left_animation(self, directions):
        c = js.document.querySelector(f'#{self.name}.mob')
        c.style.transformOrigin = "center center"

        if directions == 0:
            c.style.backgroundImage = (
                f'url("assets/img/characters/{self.mob}-{directions+1}.png")'
            )
        elif directions == 1:
            c.style.backgroundImage = (
                f'url("assets/img/characters/{self.mob}-{directions+1}.png")'
            )
        elif directions == 2:
            c.style.backgroundImage = (
                f'url("assets/img/characters/{self.mob}-{directions+1}.png")'
            )
        elif directions == 3:
            c.style.backgroundImage = f'url("assets/img/characters/{self.mob}-0.png")'

    def init_time(self):
        self.running_time = 0
        
    def attack(self):
        self.running_time += 1000 * running_speed
        self._attack()

    def _attack(self):
        directions = self.directions
        x = self.x
        y = self.y

        # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
        nx , ny = x , y
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

        c_obj=None
        for c in character_data:
            if (c['x'],c['y'])==(nx,ny):
                c_obj = c['character_obj']
                c['hp']-=self.power
                if(c['hp']<=0 and c['character'] != default_character):
                    print('die')
                    character_data.remove(c)
                    break
            
        setTimeout(create_once_callable(lambda: (self.draw_attack(x,y,nx,ny))), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)
        setTimeout(create_once_callable(lambda: self._attack_hp_animation(c_obj, c['character'])), self.running_time)
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


    def _attack_hp_animation(self,char_obj,char_name):
        global _character_data
        char = js.document.querySelector(f'.{char_name}')
        if char_obj and char:
            char_obj.hp -= self.power
            # char_obj.draw_hp()
            if char_obj.hp <= 0:
                if char_name == default_character:
                   life = js.confirm('기본 캐릭터의 체력이 0이 되었습니다. 캐릭터를 부활시키겠습니까?')
                   if life:
                       full_hp = character_data[0]['character_obj'].initHp
                       character_data[0]['hp'] = full_hp
                       character_data[0]['character_obj'].hp = full_hp
                   else:
                        setTimeout(create_once_callable(lambda: self._remove_char(char_obj, char)), 1000)
                        character_data[0] = {}
                        return
                
    def _remove_char(self, char_obj, char):
        if char:
            char.parentNode.removeChild(char)
        del char_obj
                
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

    def _update_mob_data(self, key, value):
        global mob_data
        for m in mob_data:
            if m['name'] == self.name:
                m[key] = value
                break