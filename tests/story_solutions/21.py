class TribeMember:
    def __init__(self, name):
        self.name = name

class PortalQueue:
    def __init__(self):
        self.queue = []

    def enter_portal(self, member):
        self.queue.append(member)

    def transport_all(self):
        moved = 0
        while self.queue:
            self.queue.pop(0)
            moved += 1
        if moved == 5:
            return '모든 부족원이 안전하게 이동되었습니다.'
        return '이동하지 못한 부족원이 있습니다.'

tribe_members = [TribeMember(f'member{i}') for i in range(1, 6)]
portal_queue = PortalQueue()
for member in tribe_members:
    portal_queue.enter_portal(member)
result = portal_queue.transport_all()
print(result)
