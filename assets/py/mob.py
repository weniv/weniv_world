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
        mob.setAttribute("class", "character mob")
        mob.classList.add(f"{self.mob}")
        mob.setAttribute('id', f"mob-{self.name}")
        mob.style.backgroundImage = f'url("{self.img}")'
        mob.style.transition = f"all {running_speed}s"
        mob.style.top = f"{self.x * 100 + 2 + (50 - 32)}px"
        mob.style.left = f"{self.y * 100 + 2 + (50 - 32)}px"
        finder = False
    
        # mob_data = [{"mob":"lion","x":4,"y":4,"directions":0}]
        for m in mob_data:
            if m["name"] == self.name:
                m["mob"]=self.mob
                m["x"] = self.x
                m["y"] = self.y
                m["directions"] = self.directions
                finder = True
        if not finder:
            mob_data.append(
                {
                    "name": self.name,
                    "mob": self.mob,
                    "x": self.x,
                    "y": self.y,
                    "directions": self.directions,
                }
            )
        return mob

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
            setTimeout(create_once_callable(lambda: self._alert_error(error_check)), self.running_time)
            return None
        
        self.x = nx
        self.y = ny
        self._update_mob_data('x', self.x)
        self._update_mob_data('y', self.y)
       
        setTimeout(create_once_callable(lambda: (self._move_animation(x, y, directions))), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)

        
    def _move_animation(self, x, y, directions):
        c = js.document.getElementById(f"mob-{self.name}")
        
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
        c = js.document.getElementById(f"mob-{self.name}")
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
        setTimeout(create_once_callable(lambda: (self._attack())), self.running_time)
        setTimeout(create_once_callable(lambda: self.init_time()), self.running_time)

    def _attack(self):
        directions = self.directions
        x = self.x
        y = self.y

        # 0(동, 오른쪽), 1(북), 2(서, 왼쪽), 3(남)
        if directions == 0:
            if y >= map_data["width"] - 1:
                js.alert("공격이 맵을 벗어납니다.")
                raise OutOfWorld
            self.draw_attack(x, y, x , y+1)
        elif directions == 1:
            if x <= 0:
                js.alert("공격이 맵을 벗어납니다.")
                raise OutOfWorld
            self.draw_attack(x, y, x-1, y)
        elif directions == 2:
            if y <= 0:
                js.alert("공격이 맵을 벗어납니다.")
                raise OutOfWorld
            self.draw_attack(x, y, x, y - 1)
        elif directions == 3:
            if x >= map_data["height"] - 1:
                js.alert("공격이 맵을 벗어납니다.")
                raise OutOfWorld
            self.draw_attack(x, y, x + 1, y)

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
            js.alert('다른 캐릭터 또는 몬스터가 있습니다.')
            raise Exception('CharacterIsExist')
        else:
            js.alert('new error',error_type)
            raise Exception('new error',error_type)
    
    def _update_mob_data(self, key, value):
        global mob_data
        for m in mob_data:
            if m['mob'] == self.name:
                m[key] = value
                break