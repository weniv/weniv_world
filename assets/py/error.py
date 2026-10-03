from coordinate import error_message, error_hint


class WorldError(Exception):
    """
    위니브 월드에서 발생하는 오류의 기본 클래스

    key로 coordinate.error_message / error_hint에서 한글 메시지와 해결 힌트를 찾습니다.
    학습자는 try/except로 각각의 오류를 잡을 수 있습니다.
        try:
            move()
        except OutOfWorld:
            turn_left()
    """

    key = "WorldError"

    def __init__(self, message=None):
        self.message = message or error_message.get(self.key, self.key)
        self.hint = error_hint.get(self.key, "")
        super().__init__(self.message)


class OutOfWorld(WorldError):
    """밖으로 나갔을 때 발생하는 오류"""

    key = "OutOfWorld"


class FrontIsNotClear(WorldError):
    key = "FrontIsNotClear"


class CharacterIsNotExist(WorldError):
    key = "CharacterIsNotExist"


class CharacterIsNotSelected(WorldError):
    key = "CharacterIsNotSelected"


class CharacterIsNotMovable(WorldError):
    key = "CharacterIsNotMovable"


class CharacterIsNotAttackable(WorldError):
    key = "CharacterIsNotAttackable"


class CharacterIsDead(WorldError):
    """기본 캐릭터의 체력이 0이 된 경우"""

    key = "CharacterIsDead"


class ItemIsNotExist(WorldError):
    """아이템이 없을 때 발생하는 오류"""

    key = "ItemIsNotExist"


class AnotherItemIsExist(WorldError):
    """다른 아이템이 이미 있을 때 발생하는 오류"""

    key = "AnotherItemIsExist"


class InvalidItem(WorldError):
    """아이템이 아닌 다른 것을 사용하려고 할 때 발생하는 오류"""

    key = "InvalidItem"


class InedibleItem(WorldError):
    """먹을 수 없는 아이템을 먹을 때 발생하는 오류"""

    key = "InedibleItem"


class WallIsExist(WorldError):
    """이동 경로에 벽이 있어 이동이 불가능한 경우"""

    key = "WallIsExist"


class CannotOpenWall(WorldError):
    """door가 아닌 벽에 open_door()를 사용한 경우"""

    key = "CannotOpenWall"


class DoorIsNotExist(WorldError):
    """앞에 벽이 없는데 open_door()를 사용한 경우"""

    key = "DoorIsNotExist"


class ObstacleExist(WorldError):
    """해당 위치에 다른 캐릭터 또는 몹이 있는 경우"""

    key = "ObstacleExist"


class MobIsExist(WorldError):
    """몹 이름이 중복되는 경우"""

    key = "MobIsExist"


class MobIsNotExist(WorldError):
    """삭제되었거나 쓰러진 몹을 사용하려는 경우"""

    key = "MobIsNotExist"


class CharacterIsExist(WorldError):
    """캐릭터 이름이 중복되는 경우"""

    key = "CharacterIsExist"


class ArgumentsError(WorldError):
    """함수의 인자가 잘못된 경우"""

    key = "ArgumentsError"


class NotEnoughMana(WorldError):
    """마나가 부족한 경우"""

    key = "NotEnoughMana"


class InvalidSkill(WorldError):
    """스킬이 아닌 다른 것을 사용하려는 경우"""

    key = "InvalidSkill"


class InvalidCharacter(WorldError):
    """캐릭터가 아닌 다른 것을 사용하려는 경우"""

    key = "InvalidCharacter"


class InvalidMob(WorldError):
    """몹이 아닌 다른 것을 사용하려는 경우"""

    key = "InvalidMob"


class InvalidSyntax(WorldError):
    """잘못된 문법을 사용하려는 경우"""

    key = "InvalidSyntax"


class TooManyActions(WorldError):
    """한 번의 실행에서 동작이 너무 많은 경우 (무한 반복 방지)"""

    key = "TooManyActions"


class InputNotAllowed(WorldError):
    """input() 입력창에서 취소를 누른 경우"""

    key = "InputNotAllowed"
