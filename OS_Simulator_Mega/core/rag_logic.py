class RAGLogic:
    def __init__(self):
        self.nodes = {}
        self.edges = []  # (from, to)

    def add_process(self, name, pos):
        self.nodes[name] = pos

    def add_resource(self, name, pos):
        self.nodes[name] = pos

    def add_request(self, p, r):
        self.edges.append((p, r))

    def add_allocation(self, r, p):
        self.edges.append((r, p))

    def undo(self):
        if self.edges:
            self.edges.pop()

    def clear(self):
        self.nodes.clear()
        self.edges.clear()

    # Return cycle instead of just True/False
    def find_cycle(self):
        graph = {}

        for a, b in self.edges:
            if a not in graph:
                graph[a] = []
            graph[a].append(b)

        visited = set()
        stack = []
        active = set()

        def dfs(node):
            visited.add(node)
            active.add(node)
            stack.append(node)

            for nxt in graph.get(node, []):
                if nxt not in visited:
                    result = dfs(nxt)
                    if result:
                        return result
                elif nxt in active:
                    # cycle found → extract cycle
                    idx = stack.index(nxt)
                    return stack[idx:]

            active.remove(node)
            stack.pop()
            return None

        for node in self.nodes:
            result = dfs(node)
            if result:
                return result

        return None

    def explain_deadlock(self, cycle):
        explanation = []

        explanation.append("A circular wait was detected:")
        explanation.append(" → ".join(cycle))

        explanation.append("\nDeadlock Conditions:")
        explanation.append("1. Mutual Exclusion: Resources can only be held by one process at a time.")
        explanation.append("2. Hold and Wait: Processes hold resources while waiting for others.")
        explanation.append("3. No Preemption: Resources cannot be forcibly taken away.")
        explanation.append("4. Circular Wait: A cycle exists in the RAG.")

        return "\n".join(explanation)

    def suggest_solutions(self, cycle):
        solutions = []
        edges = self.edges

        # Find resource → process edges
        owners = {}
        for r, p in edges:
            if r.startswith("R") and p.startswith("P"):
                owners[r] = p

        # Suggest preemption for resources in cycle
        for node in cycle:
            if node.startswith("R"):
                owner = owners.get(node, None)
                if owner:
                    solutions.append(f"📌 Ask {owner} to release {node}")
                else:
                    solutions.append(f"📌 Preempt resource {node}")

        # Suggest killing a process
        procs_in_cycle = [n for n in cycle if n.startswith("P")]
        if procs_in_cycle:
            p = procs_in_cycle[-1]
            solutions.append(f"🚨 Kill process {p} to break the cycle")

        # Suggest removing edges
        solutions.append("✂ Remove any one of the edges in the cycle to break circular wait.")

        return solutions
