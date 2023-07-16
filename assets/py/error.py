from built_in_functions import print

class OutOfWorld(Exception):
    '''
    밖으로 나갔을 때 출력하는 애러
    '''
    def __init__(self):
        print('error.OutOfWorld: out of world')
        super().__init__('out of world')

class FrontIsNotClear(Exception):
    def __init__(self):
        print('error.FrontIsNotClear: front is not clear')
        super().__init__('front is not clear')

class CharacterIsNotExist(Exception):
    def __init__(self):
        print('error.CharacterIsNotExist: character is not exist')
        super().__init__('character is not exist')

class CharacterIsNotSelected(Exception):
    def __init__(self):
        print('error.CharacterIsNotSelected: character is not selected')
        super().__init__('character is not selected')

class CharacterIsNotMovable(Exception):
    def __init__(self):
        print('error.CharacterIsNotMovable: character is not movable')
        super().__init__('character is not movable')

class CharacterIsNotAttackable(Exception):
    def __init__(self):
        print('error.CharacterIsNotAttackable: character is not attackable')
        super().__init__('character is not attackable')

class BottomIsClear(Exception):
    '''
    물건 집을 때 바닥에 물건이 없을 때 출력하는 애러
    '''
    def __init__(self):
        print('error.BottomIsClear: bottom is clear')
        super().__init__('bottom is clear')