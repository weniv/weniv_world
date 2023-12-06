import js

from coordinate import map_data, map_size, border_size


class Wall:
    def __init__(self):
        self.width = map_data["width"]
        self.height = map_data["height"]
        self.wall_data = {}
        self.initWall = self.initWallData(self.width, self.height)

    def initWallData(self, width, height):
        initWall = []
        x = 0
        
        while x <= height - 1:
            if x == int(x):  # x가 정수일 때
                y = 0.5
                while y <= width - 1:
                    initWall.append((x, y))
                    y += 1
            else:  # x가 정수가 아닐 때
                y = 0
                while y <= width - 1:
                    initWall.append((x, y))
                    y += 1
            x += 0.5
            
        return initWall

    def drawWall(self):
        box_size = map_size + border_size * 2
        container = js.document.createElement("div")
        container.setAttribute("class", "wall-container")

        for (x, y) in self.initWall:
            wall = js.document.createElement("div")
            wall.setAttribute("class", "wall")
            wall.setAttribute("data-type", self.wall_data.get((x, y), ''))
            wall.setAttribute("data-X", x)
            wall.setAttribute("data-Y", y)
            wall.style.top = f"{(x+0.5)*box_size}px"
            wall.style.left = f"{(y+0.5)*box_size+1}px"
            if int(x) == x:
                wall.setAttribute("data-direction", "portrait")
            else:
                wall.setAttribute("data-direction", "landscape")
            container.appendChild(wall)
        return container

    def resizeWall(self, width, height):
        """
        map의 크기가 변경될 때, wall_data를 갱신합니다.
        """
        # 새로운 wall_data를 생성
        self.initWall = self.initWallData(width, height)
        new_wall_data = {}
        
        for key in self.initWall:
            if key in self.wall_data.keys():
                new_wall_data[key] = self.wall_data[key]
                

        self.width = width
        self.height = height
        
        # 2차원 배열에 맞춰 정렬
        self.wall_data = new_wall_data
        return new_wall_data

    def resetWall(self, width, height):
        """
        wall_data를 초기화합니다.
        """
        self.width = width
        self.height = height
        self.wall_data = {}
        return self.wall_data
