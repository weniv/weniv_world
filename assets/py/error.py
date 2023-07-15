class front_is_not_clear(Exception):
    def __init__(self):
        super().__init__('front is not clear')

class character_is_not_exist(Exception):
    def __init__(self):
        super().__init__('character is not exist')

class character_is_not_selected(Exception):
    def __init__(self):
        super().__init__('character is not selected')

class character_is_not_movable(Exception):
    def __init__(self):
        super().__init__('character is not movable')

class character_is_not_attackable(Exception):
    def __init__(self):
        super().__init__('character is not attackable')

class bottom_is_clear(Exception):
    '''
    물건 집을 때 바닥에 물건이 없을 때 출력하는 애러
    '''
    def __init__(self):
        super().__init__('bottom is clear')

