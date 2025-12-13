import tkinter as tk
import random
from theme import theme_manager


class ProcessTab:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)

        self.canvas = tk.Canvas(self.frame, height=430)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        bar = tk.Frame(self.frame)
        bar.pack(fill="x")

        tk.Button(bar, text="Create Process", command=self.create_process).pack(side="left", padx=6)
        tk.Button(bar, text="GO (Next Step)", command=self.next_step).pack(side="left", padx=6)
        tk.Button(bar, text="Reset", bg="#ff6b6b", command=self.reset).pack(side="left", padx=6)

        # STATES
        self.states = ["New", "Ready", "Running", "Waiting", "Terminated"]
        self.positions = {}

        # PROCESS DATA
        self.processes = {}        # pid -> state
        self.ready_queue = []
        self.pid_count = 1
        self.exec_order = []
        self.current_index = 0

        self.redraw()

    # ================= DRAW =================
    def redraw(self):
        theme = theme_manager.get()
        self.canvas.configure(bg=theme["canvas"])
        self.canvas.delete("all")

        self.draw_layout(theme)
        self.draw_ready_queue(theme)
        self.draw_processes(theme)

    # ================= LAYOUT =================
    def draw_layout(self, theme):
        x = 40
        y = 80

        self.positions.clear()

        for state in self.states:
            self.canvas.create_rectangle(
                x, y, x+180, y+90,
                outline=theme["node_border_p"],
                width=2,
                fill=theme["bg"]
            )
            self.canvas.create_text(
                x+90, y+15,
                text=state,
                fill=theme["arrow_request"],
                font=("Segoe UI", 11, "bold")
            )
            self.positions[state] = (x+20, y+40)
            x += 200

        # READY QUEUE
        self.canvas.create_rectangle(
            40, 220, 420, 350,
            outline=theme["node_border_r"],
            width=2,
            fill=theme["bg"]
        )
        self.canvas.create_text(
            230, 235,
            text="READY QUEUE",
            fill=theme["arrow_alloc"],
            font=("Segoe UI", 11, "bold")
        )

    # ================= READY QUEUE =================
    def draw_ready_queue(self, theme):
        x = 60
        y = 260

        for pid in self.ready_queue:
            self.canvas.create_oval(
                x, y, x+50, y+40,
                fill=theme["node_process"],
                outline=theme["node_border_p"]
            )
            self.canvas.create_text(
                x+25, y+20,
                text=pid,
                fill=theme["arrow_request"]
            )
            x += 60

    # ================= PROCESSES =================
    def draw_processes(self, theme):
        offsets = {s: 0 for s in self.states}

        for pid, state in self.processes.items():
            if state not in self.positions:
                continue

            x, y = self.positions[state]
            off = offsets[state]

            self.canvas.create_oval(
                x+off, y,
                x+off+50, y+40,
                fill=theme["node_process"],
                outline=theme["node_border_p"]
            )
            self.canvas.create_text(
                x+off+25, y+20,
                text=pid,
                fill=theme["arrow_request"]
            )

            offsets[state] += 55

    # ================= CREATE PROCESS =================
    def create_process(self):
        pid = f"P{self.pid_count}"
        self.pid_count += 1

        self.processes[pid] = "New"
        self.exec_order.append(pid)

        self.redraw()

    # ================= STEP LOGIC =================
    def next_step(self):
        if not self.exec_order:
            return

        pid = self.exec_order[self.current_index]
        state = self.processes[pid]

        if state == "New":
            self.processes[pid] = "Ready"
            self.ready_queue.append(pid)

        elif state == "Ready":
            self.processes[pid] = "Running"
            if pid in self.ready_queue:
                self.ready_queue.remove(pid)

        elif state == "Running":
            if random.choice([True, False]):
                self.processes[pid] = "Waiting"
            else:
                self.processes[pid] = "Terminated"

        elif state == "Waiting":
            self.processes[pid] = "Ready"
            self.ready_queue.append(pid)

        # Move to next process
        self.current_index = (self.current_index + 1) % len(self.exec_order)

        self.redraw()

    # ================= RESET =================
    def reset(self):
        self.processes.clear()
        self.ready_queue.clear()
        self.exec_order.clear()
        self.pid_count = 1
        self.current_index = 0
        self.redraw()
