class Item:
    def __init__(self, name, description={}, count=0, x=0, y=0):
        self.name = name
        self.description = description
        self.count = count
        self.x = x
        self.y = y

    def get_count(self):
        return self.count
    
    def set_count(self, count):
        self.count = count

    def set_map(self, x, y):
        self.x = x
        self.y = y