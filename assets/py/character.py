import engine
from actor import Actor, wall_position
from coordinate import (
    character_data,
    mob_data,
    item_data,
    valid_items,
    edible_items,
    skill_data,
    wall_data,
    character_info,
    mob_info,
)
from error import (
    CharacterIsNotExist,
    ItemIsNotExist,
    AnotherItemIsExist,
    InvalidItem,
    InedibleItem,
    CannotOpenWall,
    DoorIsNotExist,
    NotEnoughMana,
    OutOfWorld,
)
from item import place_item


class Character(Actor):
    """
    주인공 캐릭터

        licat.move()
        licat.turn_left()
    """

    kind = "character"
    not_exist_error = CharacterIsNotExist

    def _data_list(self):
        return character_data

    def _name_key(self):
        return "character"

    @property
    def mp(self):
        return self._data().get("mp")

    @property
    def items(self):
        return self._data().setdefault("items", {})

    @property
    def initHp(self):
        return character_info.get(self.name, {}).get("hp", 100)

    @property
    def initMp(self):
        return character_info.get(self.name, {}).get("mp", 100)

    def _stat(self):
        d = self._data()
        engine.emit("stat", who=self._who(), hp=d.get("hp", 0), mp=d.get("mp", 0))

    def pick(self):
        """
        발 아래 아이템을 하나 줍습니다.
        """
        d = self._data()
        pos = (d["x"], d["y"])
        bottom = item_data.get(pos)
        if not bottom:
            raise ItemIsNotExist()

        items = self.items
        items[bottom["item"]] = items.get(bottom["item"], 0) + 1
        place_item(pos[0], pos[1], bottom["item"], -1, event="pick")

    def put(self, item_name):
        """
        가지고 있는 아이템을 발 아래에 하나 내려놓습니다.
        """
        if item_name not in valid_items:
            raise InvalidItem()

        d = self._data()
        pos = (d["x"], d["y"])
        items = self.items
        if items.get(item_name, 0) <= 0:
            raise ItemIsNotExist()

        bottom = item_data.get(pos)
        if bottom and bottom["item"] != item_name:
            raise AnotherItemIsExist()

        items[item_name] -= 1
        if items[item_name] == 0:
            del items[item_name]
        place_item(pos[0], pos[1], item_name, 1, event="put")

    def eat(self, item_name):
        """
        hp-potion, mp-potion을 먹어 체력과 마나를 회복합니다.
        """
        if item_name not in valid_items:
            raise InvalidItem()
        if item_name not in edible_items:
            raise InedibleItem()

        items = self.items
        if items.get(item_name, 0) <= 0:
            raise ItemIsNotExist()

        items[item_name] -= 1
        if items[item_name] == 0:
            del items[item_name]

        d = self._data()
        effect = edible_items[item_name]
        d["hp"] = min(self.initHp, d.get("hp", 0) + effect.get("hp", 0))
        d["mp"] = min(self.initMp, d.get("mp", 0) + effect.get("mp", 0))
        self.say("냠냠")
        engine.emit("eat", who=self._who(), item=item_name, hp=d["hp"], mp=d["mp"])

    def open_door(self):
        """
        바라보는 방향에 문(door)이 있으면 엽니다.
        """
        x, y, nx, ny = self._front()
        wall_type = self.typeof_wall()
        if wall_type == "OutOfWorld":
            raise OutOfWorld()
        if wall_type is None:
            raise DoorIsNotExist()
        if wall_type != "door":
            raise CannotOpenWall()

        pos = wall_position(x, y, nx, ny)
        del wall_data["world"][pos]
        engine.emit("open_door", who=self._who(), pos=list(pos))

    def attack(self, skill="claw-yellow"):
        """
        앞에 있는 몹을 스킬로 공격합니다.
        """
        d = self._data()
        if skill in skill_data and skill_data[skill]["mana"] > d.get("mp", 0):
            raise NotEnoughMana()
        x, y, nx, ny = self._attack_target(skill)

        d["mp"] = d.get("mp", 0) - skill_data[skill]["mana"]
        victim = None
        for m in list(mob_data):
            if (m.get("x"), m.get("y")) == (nx, ny):
                m["hp"] = max(0, m.get("hp", 0) - skill_data[skill]["power"])
                victim = {
                    "kind": "mob",
                    "name": m["name"],
                    "hp": m["hp"],
                    "maxHp": mob_info.get(m.get("mob"), {}).get("hp", 50),
                    "removed": m["hp"] <= 0,
                }
                if m["hp"] <= 0:
                    mob_data.remove(m)
                break

        engine.emit(
            "attack",
            who=self._who(),
            target=[nx, ny],
            skill=skill,
            victim=victim,
            mp=d["mp"],
        )

    def show_item(self):
        """주인공이 가지고 있는 아이템"""
        return self.items
