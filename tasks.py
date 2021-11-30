class res:
    def __init__(self, idx, length):
        self.idx = idx
        self.holder = None
        self.length = length
        

class task:
    def __init__(self, idx, sections):
        self.idx = idx
        self.section_list = sections
    def new_instance(self):
        instance_life = []
        for (res, len) in self.section_list:
            for i in range(0, len):
                instance_life.append(res)
        return instance(self.idx, instance_life)

class instance:
    def __init__(self, idx, life):
        self.idx = idx
        self.progress = 0
        self.life_cycle = life
    def tick(self):
        pass



