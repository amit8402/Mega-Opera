# tabs/rag_tab.py

import tkinter as tk
from tkinter import ttk, messagebox
from core.rag_logic import RAGLogic
import time
from theme import theme_manager



class RAGTab:
    def __init__(self, parent):
        theme = theme_manager.get()

        self.frame = tk.Frame(parent, bg=theme["bg"])
        self.logic = RAGLogic()
        self.process_count = 0
        self.resource_count = 0

        # Layout: Left Canvas + Right Info Panel
        self.left = tk.Frame(self.frame, bg=theme["bg"])
        self.left.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        self.right = tk.Frame(self.frame, bg=theme["bg"], width=320)
        self.right.pack(side="right", fill="y", padx=8, pady=8)

        self.canvas = tk.Canvas(self.left, bg=theme["canvas"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.create_controls()
        self.create_info_panel()

    # -------------------------------------------------------------
    # Top Control Bar
    # -------------------------------------------------------------
    def create_controls(self):
        theme = theme_manager.get()

        bar = tk.Frame(self.left, bg=theme["bg"])
        bar.place(relx=0.01, rely=0.01, relwidth=0.98, height=52)

        tk.Button(bar, text="Add Process", command=self.add_process).pack(side="left", padx=4, pady=6)
        tk.Button(bar, text="Add Resource", command=self.add_resource).pack(side="left", padx=4, pady=6)

        self.pvar = tk.StringVar()
        self.rvar = tk.StringVar()

        self.pmenu = ttk.Combobox(bar, textvariable=self.pvar, width=10)
        self.rmenu = ttk.Combobox(bar, textvariable=self.rvar, width=10)
        self.pmenu.pack(side="left", padx=6)
        self.rmenu.pack(side="left", padx=6)

        tk.Button(bar, text="Request", command=self.request).pack(side="left", padx=4)
        tk.Button(bar, text="Allocate", command=self.allocate).pack(side="left", padx=4)
        tk.Button(bar, text="Undo", command=self.undo).pack(side="left", padx=6)
        tk.Button(bar, text="Clear", command=self.clear).pack(side="left", padx=6)

        tk.Button(bar, text="Check Deadlock", command=self.check_deadlock, bg="#ffde7a").pack(side="right", padx=6)

    # -------------------------------------------------------------
    # Info Panel (Right Side)
    # -------------------------------------------------------------
    def create_info_panel(self):
        theme = theme_manager.get()

        header = tk.Label(
            self.right,
            text="Deadlock Solver",
            font=("Segoe UI", 12, "bold"),
            bg=theme["bg"],
            fg=theme["text"]
        )
        header.pack(pady=8)

        self.info_text = tk.Text(
            self.right,
            width=40,
            height=22,
            bg=theme["info_bg"],
            fg=theme["text"],
            font=("Segoe UI", 10)
        )
        self.info_text.pack(padx=8, pady=6)

        self.apply_btn = tk.Button(
            self.right,
            text="Apply Suggested Fix",
            command=self.apply_fix,
            state="disabled"
        )
        self.apply_btn.pack(pady=6)

    # -------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------
    def update_menus(self):
        items = list(self.logic.nodes.keys())
        self.pmenu["values"] = [i for i in items if i.startswith("P")]
        self.rmenu["values"] = [i for i in items if i.startswith("R")]

    # -------------------------------------------------------------
    # Node Creation
    # -------------------------------------------------------------
    def add_process(self):
        self.process_count += 1
        name = f"P{self.process_count}"
        x, y = 120, 80 + self.process_count * 70
        self._animate_node("P", name, x, y)
        self.logic.add_process(name, (x, y))
        self.update_menus()

    def add_resource(self):
        self.resource_count += 1
        name = f"R{self.resource_count}"
        x, y = 420, 80 + self.resource_count * 70
        self._animate_node("R", name, x, y)
        self.logic.add_resource(name, (x, y))
        self.update_menus()

    # -------------------------------------------------------------
    # Node Animation (Pop-in Effect)
    # -------------------------------------------------------------
    def _animate_node(self, typ, name, x, y):
        theme = theme_manager.get()
        size = 2
        tag = f"node_{name}"

        while size <= 28:
            self.canvas.delete(tag)
            if typ == "P":
                self.canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    fill=theme["node_process"],
                    outline=theme["node_border_p"], width=2, tags=tag
                )
            else:
                self.canvas.create_rectangle(
                    x - size, y - size, x + size, y + size,
                    fill=theme["node_resource"],
                    outline=theme["node_border_r"], width=2, tags=tag
                )

            self.canvas.update()
            time.sleep(0.01)
            size += 4

        # final node
        if typ == "P":
            self.canvas.create_oval(
                x - 28, y - 28, x + 28, y + 28,
                fill=theme["node_process"],
                outline=theme["node_border_p"], width=2
            )
        else:
            self.canvas.create_rectangle(
                x - 28, y - 28, x + 28, y + 28,
                fill=theme["node_resource"],
                outline=theme["node_border_r"], width=2
            )

        self.canvas.create_text(x, y, text=name, fill=theme["text"], font=("Segoe UI", 10, "bold"))

    # -------------------------------------------------------------
    # Arrow Animation
    # -------------------------------------------------------------
    def _animate_arrow(self, x1, y1, x2, y2, color):
        steps = 18
        for i in range(1, steps + 1):
            t = i / steps
            cx = x1 + (x2 - x1) * t
            cy = y1 + (y2 - y1) * t

            tag = "anim_arrow"
            self.canvas.delete(tag)
            self.canvas.create_line(
                x1, y1, cx, cy,
                arrow=tk.LAST,
                fill=color,
                width=3,
                tags=tag
            )
            self.canvas.update()
            time.sleep(0.01)

        self.canvas.delete("anim_arrow")
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill=color, width=2)

    # -------------------------------------------------------------
    # Request & Allocate Edges
    # -------------------------------------------------------------
    def request(self):
        theme = theme_manager.get()
        p = self.pvar.get()
        r = self.rvar.get()

        if not p or not r:
            messagebox.showwarning("Missing", "Select process and resource")
            return

        x1, y1 = self.logic.nodes[p]
        x2, y2 = self.logic.nodes[r]

        self._animate_arrow(x1, y1, x2, y2, theme["arrow_request"])
        self.logic.add_request(p, r)

    def allocate(self):
        theme = theme_manager.get()
        p = self.pvar.get()
        r = self.rvar.get()

        if not p or not r:
            messagebox.showwarning("Missing", "Select process and resource")
            return

        x1, y1 = self.logic.nodes[r]
        x2, y2 = self.logic.nodes[p]

        self._animate_arrow(x1, y1, x2, y2, theme["arrow_alloc"])
        self.logic.add_allocation(r, p)

    # -------------------------------------------------------------
    # Undo & Clear
    # -------------------------------------------------------------
    def undo(self):
        self.logic.undo()
        self.redraw()

    def clear(self):
        self.logic.clear()
        self.canvas.delete("all")
        self.update_menus()
        self.info_text.delete("1.0", tk.END)
        self.apply_btn.config(state="disabled")

    # -------------------------------------------------------------
    # Redraw
    # -------------------------------------------------------------
    def redraw(self):
        theme = theme_manager.get()
        self.canvas.delete("all")
        self.canvas.configure(bg=theme["canvas"])

        for node, (x, y) in self.logic.nodes.items():
            if node.startswith("P"):
                self.canvas.create_oval(
                    x - 28, y - 28, x + 28, y + 28,
                    fill=theme["node_process"],
                    outline=theme["node_border_p"],
                    width=2
                )
            else:
                self.canvas.create_rectangle(
                    x - 28, y - 28, x + 28, y + 28,
                    fill=theme["node_resource"],
                    outline=theme["node_border_r"],
                    width=2
                )

            self.canvas.create_text(x, y, text=node, fill=theme["text"])

        for a, b in self.logic.edges:
            x1, y1 = self.logic.nodes[a]
            x2, y2 = self.logic.nodes[b]
            color = theme["arrow_request"] if a.startswith("P") else theme["arrow_alloc"]

            self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill=color, width=2)

    # -------------------------------------------------------------
    # Deadlock Detection
    # -------------------------------------------------------------
    def check_deadlock(self):
        cycle = self.logic.find_cycle()

        if not cycle:
            messagebox.showinfo("Safe", "No deadlock found")
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert("1.0", "System is in a safe state.")
            self.apply_btn.config(state="disabled")
            return

        self.redraw()
        self._blink_cycle(cycle)

        explanation = self.logic.explain_deadlock(cycle)
        solutions = self.logic.suggest_solutions(cycle)

        info = explanation + "\n\nFixes:\n"
        for s in solutions:
            info += f"- {s}\n"

        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", info)

        self.suggested_actions = solutions
        self.apply_btn.config(state="normal")

        messagebox.showerror("Deadlock", "⚠ Deadlock detected!")

    # -------------------------------------------------------------
    # Blinking Highlight on Cycle
    # -------------------------------------------------------------
    def _blink_cycle(self, cycle, times=6):
        theme = theme_manager.get()

        edge_pairs = [(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))]

        def blink_on():
            for a, b in edge_pairs:
                x1, y1 = self.logic.nodes[a]
                x2, y2 = self.logic.nodes[b]
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    arrow=tk.LAST,
                    fill="#ff3b30",
                    width=4,
                    tags="blink"
                )
            for n in cycle:
                x, y = self.logic.nodes[n]
                self.canvas.create_oval(
                    x - 34, y - 34, x + 34, y + 34,
                    outline="#ff3b30",
                    width=3, tags="blink"
                )

        def blink_off():
            self.canvas.delete("blink")

        def step(i=0):
            if i >= times * 2:
                self.canvas.delete("blink")
                return

            if i % 2 == 0:
                blink_on()
            else:
                blink_off()

            self.frame.after(220, lambda: step(i + 1))

        step()

    # -------------------------------------------------------------
    # Automatic Fix Suggestion
    # -------------------------------------------------------------
    def apply_fix(self):
        if not hasattr(self, "suggested_actions"):
            return

        applied = False

        for s in self.suggested_actions:
            txt = s

            # Kill process
            if "Kill process" in txt:
                proc = txt.split()[2]
                self.logic.edges = [(u, v) for (u, v) in self.logic.edges if proc not in (u, v)]
                applied = True
                break

            # Ask P to release R
            if "release" in txt:
                words = txt.split()
                proc = words[1]
                res = words[-1]
                self.logic.edges = [(u, v) for (u, v) in self.logic.edges if not (u == res and v == proc)]
                applied = True
                break

        if not applied:
            # fallback: remove last edge
            if self.logic.edges:
                self.logic.edges.pop()
                applied = True

        if applied:
            messagebox.showinfo("Fix Applied", "Fix applied. Re-run check.")
            self.apply_btn.config(state="disabled")
            self.redraw()
