from built_in_functions import print, _show_modal
from coordinate import error_message
import js

class OutOfWorld(Exception):
    """
    밖으로 나갔을 때 출력하는 애러
    """
    def __init__(self):
        print("error.OutOfWorld: out of world", type="error")
        super().__init__("out of world")


class FrontIsNotClear(Exception):
    def __init__(self):
        print("error.FrontIsNotClear: front is not clear", type="error")
        super().__init__("front is not clear")


class CharacterIsNotExist(Exception):
    def __init__(self):
        print("error.CharacterIsNotExist: character is not exist", type="error")
        super().__init__("character is not exist")


class CharacterIsNotSelected(Exception):
    def __init__(self):
        print("error.CharacterIsNotSelected: character is not selected", type="error")
        super().__init__("character is not selected")


class CharacterIsNotMovable(Exception):
    def __init__(self):
        print("error.CharacterIsNotMovable: character is not movable", type="error")
        super().__init__("character is not movable")


class CharacterIsNotAttackable(Exception):
    def __init__(self):
        print(
            "error.CharacterIsNotAttackable: character is not attackable", type="error"
        )
        super().__init__("character is not attackable")


class ItemIsNotExist(Exception):
    """
    아이템이 없을 때 발생하는 에러
    """

    def __init__(self):
        print("error.ItemISNotExist: Item is not exist", type="error")
        super().__init__("Item is not exist")


class AnotherItemIsExist(Exception):
    """
    다른 아이템이 이미 있을 때 발생하는 에러
    """

    def __init__(self):
        print("error.AnotherItemIsExist: Another item is exist", type="error")
        super().__init__("Another item is exist")
        
class InvalidItem(Exception):
    """
    아이템이 아닌 다른 것을 사용하려고 할 때 발생하는 에러
    """

    def __init__(self):
        print("error.InvalidItem: Invalid item", type="error")
        super().__init__("Invalid item")
        
class InedibleItem(Exception):
    """
    먹을 수 없는 아이템을 먹을 때 발생하는 에러
    """

    def __init__(self):
        print("error.InedibleItem: Inedible item", type="error")
        super().__init__("Inedible item")
        

class WallIsExist(Exception):
    """
    이동 경로에 벽이 있어 이동이 불가능한 경우에 발생하는 오류
    """

    def __init__(self):
        print("error.WallIsExist: wall is exist", type="error")
        super().__init__("wall is exist")

class CannotOpenWall(Exception):
    """
    door가 아닌 벽에 open_door 메서드 사용 시 발생하는 오류
    """

    def __init__(self):
        print("error.CannotOpenWall: you cannot open wall", type="error")
        super().__init__("cannot open wall")

class ObstacleExist(Exception):
    """
    해당 위치에 장애물이 존재하는 경우
    """

    def __init__(self):
        print("error.Obstacle Exist: another character or mob is exist", type="error")
        super().__init__("cannot add")

        
class MobIsExist(Exception):
    """
    몬스터 이름이 중복되는 경우에 발생하는 오류
    """

    def __init__(self):
        print("error.MobIsExist: mob is aleready exist. use another name", type="error")
        super().__init__("cannot move forward")
    
class CharacterIsExist(Exception):
    """
    캐릭터 이름이 중복되는 경우에 발생하는 오류
    """

    def __init__(self):
        print("error.CharacterIsExist: character is already exist." , type="error")
        super().__init__("cannot move forward")
        
class ArgumentsError(Exception):
    """
    함수의 인자가 잘못된 경우에 발생하는 오류
    """

    def __init__(self):
        print("error.ArgumentsError: arguments is x`wrong." , type="error")
        super().__init__("arguments is wrong")
        
def alert_error(error_type):
    if error_type not in error_message.keys():
        _show_modal("알 수 없는 에러가 발생했습니다.")
        raise Exception(error_type)
    _show_modal(error_message[error_type])
    
class NotEnoughMana(Exception):
    """
    마나가 부족한 경우에 발생하는 오류
    """

    def __init__(self):
        print("error.NotEnoughMana: not enough mana" , type="error")
        super().__init__("not enough mana")
        
class InvalidSkill(Exception):
    """
    스킬이 아닌 다른 것을 사용하려고 할 때 발생하는 에러
    """

    def __init__(self):
        print("error.InvalidSkill: Invalid skill", type="error")
        super().__init__("Invalid skill")
        
class InvalidCharacter(Exception):
    """
    캐릭터가 아닌 다른 것을 사용하려고 할 때 발생하는 에러
    """

    def __init__(self):
        print("error.InvalidCharacter: Invalid character", type="error")
        super().__init__("Invalid character")
        
class InvalidMob(Exception):
    """
    몬스터가 아닌 다른 것을 사용하려고 할 때 발생하는 에러
    """

    def __init__(self):
        print("error.InvalidMob: Invalid mob", type="error")
        super().__init__("Invalid mob")
        
class InvalidSyntax(Exception):
    """
    잘못된 문법을 사용하려고 할 때 발생하는 에러
    """

    def __init__(self):
        print("error.InvalidSyntax: Invalid syntax", type="error")
        super().__init__("Invalid syntax")
        
class InvalidCharacter(Exception):
    """
    캐릭터가 아닌 다른 것을 사용하려고 할 때 발생하는 에러
    """
    def __init__(self):
        print("error.InvalidCharacter: Invalid character", type="error")
        super().__init__("Invalid character")