class Process:
    def __init__(self, pid):
        self.pid = pid
        self.state = "New"

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.ready_queue = []
        self.waiting = []
        self.running = None

    def create(self, pid):
        p = Process(pid)
        self.processes[pid] = p
        return p

    def admit(self, pid):
        p = self.processes[pid]
        p.state = "Ready"
        self.ready_queue.append(p)

    def dispatch(self):
        if not self.ready_queue or self.running:
            return
        p = self.ready_queue.pop(0)
        p.state = "Running"
        self.running = p

    def block(self):
        if not self.running:
            return
        p = self.running
        p.state = "Waiting"
        self.waiting.append(p)
        self.running = None

    def wakeup(self):
        if not self.waiting:
            return
        p = self.waiting.pop(0)
        p.state = "Ready"
        self.ready_queue.append(p)

    def terminate(self):
        if not self.running:
            return
        self.running.state = "Terminated"
        self.running = None
