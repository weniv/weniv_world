import js

class Map:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def drawMap(self):
        '''
        html문서 내 X x Y 격자무늬 map을 그려주는 함수
        '''
        container = js.document.createElement('div')
        container.setAttribute('class', 'map-container')
        for i in range(0, self.X):
            flex = js.document.createElement('div')
            flex.setAttribute('class', 'map-flex')
            for j in range(0, self.Y):
                item = js.document.createElement('div')
                item.setAttribute('class', 'map-item')
                flex.appendChild(item)
            container.appendChild(flex)
        return container