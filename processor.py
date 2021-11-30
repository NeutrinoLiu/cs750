# core states
IDLE = 0
RUNNING = 1
SPINNING = 2
SWITCH = 3

class pool:
    def __init__(self):
        pass
    def enroll(self):
        pass
    def select(self):
        pass
    
class core:
    def __init__(self, idx):
        self.idx = idx
        self.pool = pool()
        self.running = None
        self.state = IDLE

# simulator modules 
class task_launcher:
    def __init__(self, tasks):
        self.tasks = tasks
    def tick(self):
        return None

class task_mapper:
    def __init__(self, mapping):
        self.mapping = mapping
    def map(self, task):
        return self.mapping[task.idx]