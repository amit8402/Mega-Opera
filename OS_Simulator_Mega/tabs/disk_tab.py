import tkinter as tk
from tkinter import ttk, messagebox
from core.disk_logic import fcfs, sstf, scan
from theme import theme_manager
import math


class DiskTab:
    def __init__(self, notebook):
        self.outer = tk.Frame(notebook)
        self.outer.pack(fill="both", expand=True)

        self.canvas_scroll = tk.Canvas(self.outer, highlightthickness=0)
        self.canvas_scroll.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.outer, orient="vertical", command=self.canvas_scroll.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas_scroll.configure(yscrollcommand=self.scrollbar.set)

        self.frame = tk.Frame(self.canvas_scroll)
        self.canvas_window = self.canvas_scroll.create_window(
            (0, 0), window=self.frame, anchor="nw"
        )

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))
        )

        self.canvas_scroll.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.itemconfig(self.canvas_window, width=e.width)
        )

        self.title = tk.Label(self.frame, text="Disk Scheduling", font=("Segoe UI", 16, "bold"))
        self.title.pack(pady=8)

        self.container = tk.Frame(self.frame)
        self.container.pack(padx=20, pady=5, fill="x")

        form = ttk.Frame(self.container)
        form.pack(pady=5)

        ttk.Label(form, text="Request Queue").grid(row=0, column=0, sticky="w")
        self.req_entry = ttk.Entry(form, width=35)
        self.req_entry.grid(row=0, column=1, padx=8)

        ttk.Label(form, text="Head Position").grid(row=1, column=0, sticky="w")
        self.head_entry = ttk.Entry(form, width=15)
        self.head_entry.grid(row=1, column=1, sticky="w", padx=8)

        ttk.Label(form, text="Algorithm").grid(row=2, column=0, sticky="w")
        self.algo = ttk.Combobox(form, values=["FCFS", "SSTF", "SCAN"], state="readonly", width=12)
        self.algo.current(0)
        self.algo.grid(row=2, column=1, sticky="w", padx=8)

        ttk.Label(form, text="Direction").grid(row=3, column=0, sticky="w")
        self.direction = ttk.Combobox(form, values=["left", "right"], state="readonly", width=12)
        self.direction.current(1)
        self.direction.grid(row=3, column=1, sticky="w", padx=8)

        ttk.Button(self.frame, text="Simulate", command=self.simulate).pack(pady=6)

        self.seq_box = tk.Listbox(self.frame, height=6, width=40)
        self.seq_box.pack(pady=5)

        # -------- Visual Section (RESTORED) --------
        self.visual_frame = tk.Frame(self.frame)
        self.visual_frame.pack(pady=5)

        self.canvas_v = tk.Canvas(self.visual_frame, width=120, height=300, highlightthickness=0)
        self.canvas_v.grid(row=0, column=0, padx=20)

        self.canvas_c = tk.Canvas(self.visual_frame, width=300, height=300, highlightthickness=0)
        self.canvas_c.grid(row=0, column=1, padx=20)

        # -------- ONLY ONE GRAPH (2D) --------
        self.graph2d = tk.Canvas(self.frame, width=720, height=260, highlightthickness=0)
        self.graph2d.pack(pady=10)

        self.redraw()

    def redraw(self):
        theme = theme_manager.get()
        bg = theme.get("bg", "#ffffff")
        fg = theme.get("fg", "#000000")
        accent = theme.get("accent", fg)

        self.frame.configure(bg=bg)
        self.container.configure(bg=bg)
        self.visual_frame.configure(bg=bg)
        self.title.configure(bg=bg, fg=accent)
        self.seq_box.configure(bg=bg, fg=fg)
        self.canvas_v.configure(bg=bg)
        self.canvas_c.configure(bg=bg)
        self.graph2d.configure(bg=bg)

    def draw_vertical_disk(self, requests):
        self.canvas_v.delete("all")
        self.canvas_v.create_rectangle(50, 20, 70, 280, width=3)
        for r in requests:
            y = 20 + (r / 199) * 260
            self.canvas_v.create_line(45, y, 75, y, fill="blue")

    def draw_vertical_head(self, pos):
        y = 20 + (pos / 199) * 260
        self.canvas_v.delete("head")
        self.canvas_v.create_rectangle(42, y-5, 78, y+5, fill="red", tags="head")

    def draw_circular_disk(self):
        self.canvas_c.delete("all")
        self.canvas_c.create_oval(40, 40, 260, 260, width=3)

    def draw_circular_head(self, pos):
        angle = (pos / 199) * 2 * math.pi
        cx, cy = 150, 150
        r = 100
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        self.canvas_c.delete("chead")
        self.canvas_c.create_oval(x-6, y-6, x+6, y+6, fill="red", tags="chead")

    def animate_heads(self, seq, i=0):
        if i >= len(seq):
            return
        self.draw_vertical_head(seq[i])
        self.draw_circular_head(seq[i])
        self.frame.after(400, lambda: self.animate_heads(seq, i+1))

    # -------- FINAL CORRECT 2D GRAPH --------
    def draw_2d_graph(self, seq):
        self.graph2d.delete("all")

        gx, gy, gw, gh = 80, 20, 600, 200

        self.graph2d.create_line(gx, gy, gx, gy + gh, width=2)
        self.graph2d.create_line(gx, gy + gh, gx + gw, gy + gh, width=2)

        for t in range(0, 201, 20):
            x = gx + (t / 199) * gw
            self.graph2d.create_line(x, gy + gh - 5, x, gy + gh + 5)
            self.graph2d.create_text(x, gy + gh + 18, text=str(t), font=("Segoe UI", 8))

        self.points = []
        step_y = gh / (len(seq) - 1)

        for i, pos in enumerate(seq):
            x = gx + (pos / 199) * gw
            y = gy + i * step_y
            self.points.append((x, y))

        self.animate_2d_graph(0)

    def animate_2d_graph(self, i):
        if i >= len(self.points) - 1:
            return

        x1, y1 = self.points[i]
        x2, y2 = self.points[i + 1]

        color = "green" if x2 > x1 else "red"

        self.graph2d.create_line(
            x1, y1,
            x2, y2,
            width=2,
            fill=color,
            arrow=tk.LAST,
            arrowshape=(10, 12, 6)
        )

        self.graph2d.create_oval(x1-3, y1-3, x1+3, y1+3, fill="black")
        self.frame.after(400, lambda: self.animate_2d_graph(i + 1))

    def simulate(self):
        try:
            requests = list(map(int, self.req_entry.get().replace(" ", "").split(",")))
            head = int(self.head_entry.get())
        except:
            messagebox.showerror("Error", "Invalid Input")
            return

        algo = self.algo.get()
        direction = self.direction.get()

        if algo == "FCFS":
            seq, _ = fcfs(requests, head)
        elif algo == "SSTF":
            seq, _ = sstf(requests, head)
        else:
            seq, _ = scan(requests, head, direction)

        self.seq_box.delete(0, tk.END)
        for s in seq:
            self.seq_box.insert(tk.END, s)

        self.draw_vertical_disk(requests)
        self.draw_circular_disk()
        self.animate_heads(seq)
        self.draw_2d_graph(seq)
