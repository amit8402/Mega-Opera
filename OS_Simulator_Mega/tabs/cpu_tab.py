import tkinter as tk
from tkinter import ttk, messagebox
from core.cpu_logic import CPULogic
from theme import theme_manager
import time


class CPUTab:
    def __init__(self, parent):
        self.logic = CPULogic()
        self.pid_count = 1

        theme = theme_manager.get()
        self.frame = tk.Frame(parent, bg=theme["bg"])

        # 🔥 IMPORTANT: ProcessTab NEEDS THIS
        self.processes = {}

        # -------- TOP BAR --------
        top = tk.Frame(self.frame, bg=theme["bg"])
        top.pack(fill="x", padx=8, pady=6)

        tk.Label(top, text="Arrival", bg=theme["bg"], fg=theme["text"]).pack(side="left")
        self.arrival = tk.Entry(top, width=5)
        self.arrival.pack(side="left", padx=4)

        tk.Label(top, text="Burst", bg=theme["bg"], fg=theme["text"]).pack(side="left")
        self.burst = tk.Entry(top, width=5)
        self.burst.pack(side="left", padx=4)

        tk.Label(top, text="Priority", bg=theme["bg"], fg=theme["text"]).pack(side="left")
        self.priority = tk.Entry(top, width=5)
        self.priority.pack(side="left", padx=4)

        tk.Button(top, text="Add Process", command=self.add_process).pack(side="left", padx=6)

        tk.Label(top, text="Algorithm", bg=theme["bg"], fg=theme["text"]).pack(side="left", padx=4)
        self.algo = tk.StringVar(value="FCFS")
        self.algo_box = ttk.Combobox(
            top,
            textvariable=self.algo,
            values=["FCFS", "SJF", "Priority", "Round Robin"],
            state="readonly",
            width=12
        )
        self.algo_box.pack(side="left", padx=6)
        self.algo_box.bind("<<ComboboxSelected>>", self.on_algo_change)

        self.q_label = tk.Label(top, text="Quantum", bg=theme["bg"], fg=theme["text"])
        self.q_entry = tk.Entry(top, width=5)

        tk.Button(top, text="Run", command=self.run).pack(side="left", padx=6)
        tk.Button(top, text="Reset", bg="#ff6b6b", command=self.reset).pack(side="left", padx=6)

        # -------- TABLE --------
        self.table = ttk.Treeview(
            self.frame,
            columns=("PID", "Arrival", "Burst", "Priority"),
            show="headings",
            height=5
        )
        for c in ("PID", "Arrival", "Burst", "Priority"):
            self.table.heading(c, text=c)
        self.table.pack(fill="x", padx=8, pady=6)

        # -------- CANVAS --------
        self.canvas = tk.Canvas(self.frame, bg=theme["canvas"], height=220)
        self.canvas.pack(fill="x", padx=8, pady=8)

        # -------- RESULT --------
        self.result = ttk.Treeview(
            self.frame,
            columns=("PID", "WT", "TAT"),
            show="headings",
            height=5
        )
        for c in ("PID", "WT", "TAT"):
            self.result.heading(c, text=c)
        self.result.pack(fill="x", padx=8, pady=6)

    # -------- ADD PROCESS --------
    def add_process(self):
        try:
            a = int(self.arrival.get())
            b = int(self.burst.get())
            p = int(self.priority.get() or 0)
        except:
            messagebox.showwarning("Invalid", "Enter valid numbers")
            return

        pid = f"P{self.pid_count}"
        self.pid_count += 1

        self.logic.add_process(pid, a, b, p)

        # 🔥 Process State integration
        self.processes[pid] = {"state": "New"}

        self.table.insert("", "end", values=(pid, a, b, p))

        self.arrival.delete(0, tk.END)
        self.burst.delete(0, tk.END)
        self.priority.delete(0, tk.END)

    # -------- ALGO CHANGE --------
    def on_algo_change(self, e=None):
        if self.algo.get() == "Round Robin":
            self.q_label.pack(side="left", padx=4)
            self.q_entry.pack(side="left", padx=4)
        else:
            self.q_label.pack_forget()
            self.q_entry.pack_forget()

    # -------- RUN --------
    def run(self):
        self.canvas.delete("all")
        for i in self.result.get_children():
            self.result.delete(i)

        algo = self.algo.get()

        # 🔥 Move processes to READY
        for p in self.processes.values():
            if p["state"] == "New":
                p["state"] = "Ready"

        if algo == "FCFS":
            gantt, res = self.logic.fcfs()
        elif algo == "SJF":
            gantt, res = self.logic.sjf()
        elif algo == "Priority":
            gantt, res = self.logic.priority()
        else:
            try:
                q = int(self.q_entry.get())
            except:
                messagebox.showwarning("Quantum", "Enter time quantum")
                return
            gantt, res = self.logic.round_robin(q)

        self.animate_gantt(gantt)

        # 🔥 Update process states
        for pid, _, _ in gantt:
            self.processes[pid]["state"] = "Terminated"

        for r in res:
            self.result.insert("", "end", values=(r["pid"], r["wt"], r["tat"]))

    # -------- GANTT ANIMATION --------
    def animate_gantt(self, gantt):
        theme = theme_manager.get()
        x, y, h, scale = 30, 90, 40, 40

        for pid, s, e in gantt:
            w = (e - s) * scale

            # Running state
            self.processes[pid]["state"] = "Running"

            for i in range(0, w + 1, 5):
                self.canvas.delete("temp")
                self.canvas.create_rectangle(
                    x, y, x + i, y + h,
                    fill=theme["node_process"],
                    outline=theme["text"],
                    tags="temp"
                )
                self.canvas.update()
                time.sleep(0.01)

            self.canvas.delete("temp")
            self.canvas.create_rectangle(
                x, y, x + w, y + h,
                fill=theme["node_process"],
                outline=theme["text"]
            )
            self.canvas.create_text(x + w / 2, y + h / 2, text=pid, fill=theme["text"])
            self.canvas.create_text(x, y + h + 18, text=str(s), fill=theme["text"], anchor="w")
            x += w

        self.canvas.create_text(x, y + h + 18, text=str(gantt[-1][2]), fill=theme["text"], anchor="w")

    # -------- RESET --------
    def reset(self):
        self.logic.processes.clear()
        self.processes.clear()
        self.pid_count = 1
        self.canvas.delete("all")

        for t in (self.table, self.result):
            for i in t.get_children():
                t.delete(i)
