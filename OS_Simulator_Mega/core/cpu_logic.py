class CPULogic:
    def __init__(self):
        self.processes = []

    def add_process(self, pid, arrival, burst, priority=0):
        self.processes.append({
            "pid": pid,
            "arrival": arrival,
            "burst": burst,
            "priority": priority
        })

    # ---------- FCFS ----------
    def fcfs(self):
        procs = sorted(self.processes, key=lambda x: x["arrival"])
        time = 0
        gantt = []
        result = []

        for p in procs:
            if time < p["arrival"]:
                time = p["arrival"]

            start = time
            end = time + p["burst"]
            gantt.append((p["pid"], start, end))

            wt = start - p["arrival"]
            tat = end - p["arrival"]
            result.append({"pid": p["pid"], "wt": wt, "tat": tat})

            time = end

        return gantt, result

    # ---------- SJF (Non-preemptive) ----------
    def sjf(self):
        time = 0
        gantt = []
        result = []
        procs = self.processes.copy()

        while procs:
            available = [p for p in procs if p["arrival"] <= time]
            if not available:
                time += 1
                continue

            p = min(available, key=lambda x: x["burst"])
            procs.remove(p)

            start = time
            end = time + p["burst"]
            gantt.append((p["pid"], start, end))

            wt = start - p["arrival"]
            tat = end - p["arrival"]
            result.append({"pid": p["pid"], "wt": wt, "tat": tat})

            time = end

        return gantt, result

    # ---------- PRIORITY (Non-preemptive, lower value = higher priority) ----------
    def priority(self):
        time = 0
        gantt = []
        result = []
        procs = self.processes.copy()

        while procs:
            available = [p for p in procs if p["arrival"] <= time]
            if not available:
                time += 1
                continue

            p = min(available, key=lambda x: x["priority"])
            procs.remove(p)

            start = time
            end = time + p["burst"]
            gantt.append((p["pid"], start, end))

            wt = start - p["arrival"]
            tat = end - p["arrival"]
            result.append({"pid": p["pid"], "wt": wt, "tat": tat})

            time = end

        return gantt, result

    # ---------- ROUND ROBIN ----------
    def round_robin(self, quantum):
        time = 0
        gantt = []
        result = {}
        queue = []
        procs = sorted(self.processes, key=lambda x: x["arrival"])
        remaining = {p["pid"]: p["burst"] for p in procs}
        arrived = []

        while procs or queue:
            while procs and procs[0]["arrival"] <= time:
                queue.append(procs.pop(0))

            if not queue:
                time += 1
                continue

            p = queue.pop(0)
            pid = p["pid"]
            exec_time = min(quantum, remaining[pid])

            start = time
            end = time + exec_time
            gantt.append((pid, start, end))

            remaining[pid] -= exec_time
            time = end

            while procs and procs[0]["arrival"] <= time:
                queue.append(procs.pop(0))

            if remaining[pid] > 0:
                queue.append(p)
            else:
                tat = time - p["arrival"]
                wt = tat - p["burst"]
                result[pid] = {"pid": pid, "wt": wt, "tat": tat}

        return gantt, list(result.values())
