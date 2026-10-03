import engine
from actor import Actor
from coordinate import character_data, mob_data, mob_info, skill_data, default_character, character_info
from error import MobIsNotExist, CharacterIsDead


class Mob(Actor):
    """
    몹(몬스터)

        lion = add_mob(2, 2, 'lion', 'leo')
        lion.move()
        lion.turn_left()
        lion.attack()
    """

    kind = "mob"
    not_exist_error = MobIsNotExist

    def _data_list(self):
        return mob_data

    def _name_key(self):
        return "name"

    @property
    def mob(self):
        return self._data().get("mob")

    @property
    def initHp(self):
        return mob_info.get(self.mob, {}).get("hp", 50)

    def attack(self, skill="claw-yellow"):
        """
        앞에 있는 캐릭터를 공격합니다. 몹은 마나를 쓰지 않습니다.
        """
        x, y, nx, ny = self._attack_target(skill)

        victim = None
        dead = False
        for c in list(character_data):
            if (c.get("x"), c.get("y")) == (nx, ny):
                c["hp"] = max(0, c.get("hp", 0) - skill_data[skill]["power"])
                name = c.get("character")
                removed = c["hp"] <= 0 and name != default_character
                dead = c["hp"] <= 0 and name == default_character
                victim = {
                    "kind": "character",
                    "name": name,
                    "hp": c["hp"],
                    "maxHp": character_info.get(name, {}).get("hp", 100),
                    "removed": removed,
                }
                if removed:
                    character_data.remove(c)
                break

        engine.emit("attack", who=self._who(), target=[nx, ny], skill=skill, victim=victim, mp=None)
        if dead:
            raise CharacterIsDead()
