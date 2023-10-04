import js

from coordinate import item_data, map_data


class Item:
    def __init__(self, x, y, name, count=1, description={}):
        self.name = name
        self.count = count
        self.description = description
        self.x = x
        self.y = y
        self.img = f"./assets/img/item/{name}.png"

        container = js.document.createElement("div")
        container.setAttribute("class", "item-container")
        self.container = container

        map_container = js.document.querySelector(".map-items")
        map_items = map_container.querySelectorAll(".map-item")
        index = map_data["width"] * self.x + self.y
        self.target = map_items[index]

    def item_exist(self):
        """
        해당 좌표에 아이템이 있는지 확인하는 함수
        """
        # self.target에 자식요소가 있으면 true, 없으면 false
        if self.target.hasChildNodes():
            item = self.target.querySelector(".item")
            count = self.target.querySelector(".count").innerHTML
            return {"name": list(item.classList)[1], "count": count}
        else:
            return False

    def draw(self):
        """
        x좌표, y좌표에 item을 생성하는 함수
        """

        target_item = self.item_exist()
        if target_item:
            if target_item["name"] == self.name:
                self.set_count(self.count + int(target_item["count"]))
            self.target.removeChild(self.target.querySelector(".item-container"))

        item = js.document.createElement("img")
        item.setAttribute("class", "item")
        item.classList.add(f"{self.name}")
        item.classList.add(f"item{self.x}{self.y}")
        # character.style.width = f'{self.width}px'
        item.setAttribute("src", self.img)
        item.style.position = "absolute"
        item.style.top = "50%"
        item.style.left = "50%"
        item.style.transform = "translate(-50%, -50%)"
        item_data[(self.x, self.y)] = {"item": self.name, "count": self.count}
        self.container.appendChild(item)

        self.target.appendChild(self.container)
        self.draw_count()

    def draw_count(self):
        """
        x좌표, y좌표 item에 상단 오른쪽 개수를 생성하는 함수
        """
        count = js.document.createElement("div")
        count.setAttribute("class", "count")
        count.classList.add(f"{self.name}")
        count.classList.add(f"count{self.x}{self.y}")
        count.style.position = "absolute"
        count.style.top = "15%"
        count.style.right = "15%"
        count.style.display = "flex"
        count.style.justifyContent = "center"
        count.style.alignItems = "center"
        count.style.border = "1px solid black"
        if self.count < 9:
            count.style.width = "18px"
            count.style.height = "18px"
        elif self.count < 99:
            count.style.width = "20px"
            count.style.height = "20px"
        elif self.count < 999:
            count.style.width = "22px"
            count.style.height = "22px"
        else:
            count.style.width = "24px"
            count.style.height = "24px"
        count.style.borderRadius = "50%"
        count.style.fontSize = "10px"
        count.innerHTML = f"{self.count}"
        self.container.appendChild(count)

    def get_count(self):
        return self.count

    def set_count(self, count):
        self.count = count

    def set_map(self, x, y):
        self.x = x
        self.y = y
