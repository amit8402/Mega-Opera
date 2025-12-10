# tabs/memory_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from core.memory_logic import MemoryManager

class MemoryTab:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#f7f9fc")
        self.manager = MemoryManager(total_kb=1000, frame_kb=20)  # adjust sizes if you want

        self.mode = tk.StringVar(value="paging")  # paging / segmentation
        self.policy = tk.StringVar(value="first")  # for segmentation

        self.create_controls()
        self.create_canvas_area()
        self.redraw()

    def create_controls(self):
        ctrl = tk.Frame(self.frame, bg="#f7f9fc")
        ctrl.pack(side="left", fill="y", padx=12, pady=12)

        tk.Label(ctrl, text="Memory Mode:", bg="#f7f9fc", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Radiobutton(ctrl, text="Paging", variable=self.mode, value="paging", bg="#f7f9fc", command=self.redraw).pack(anchor="w")
        tk.Radiobutton(ctrl, text="Segmentation", variable=self.mode, value="segmentation", bg="#f7f9fc", command=self.redraw).pack(anchor="w")

        # Paging controls
        tk.Label(ctrl, text="\nProcess Name:", bg="#f7f9fc").pack(anchor="w")
        self.proc_entry = tk.Entry(ctrl)
        self.proc_entry.pack(fill="x")

        tk.Label(ctrl, text="Size (KB):", bg="#f7f9fc").pack(anchor="w")
        self.size_entry = tk.Entry(ctrl)
        self.size_entry.pack(fill="x")

        tk.Button(ctrl, text="Allocate", command=self.allocate).pack(fill="x", pady=6)
        tk.Button(ctrl, text="Free Process", command=self.free_process).pack(fill="x", pady=2)

        # Segmentation policies
        tk.Label(ctrl, text="\nSegmentation Policy:", bg="#f7f9fc").pack(anchor="w", pady=(8,0))
        ttk.Combobox(ctrl, textvariable=self.policy, values=["first","best","worst"]).pack(fill="x")

        tk.Button(ctrl, text="Reset Memory", command=self.reset_memory).pack(fill="x", pady=(12,0))

        # Info box
        self.info = tk.Text(ctrl, width=30, height=12, bg="#ffffff")
        self.info.pack(pady=8)
        self.info.insert("1.0", "Memory Info:\n")

    def create_canvas_area(self):
        canvas_frame = tk.Frame(self.frame, bg="#eef2f7")
        canvas_frame.pack(side="right", fill="both", expand=True, padx=12, pady=12)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

    def allocate(self):
        proc = self.proc_entry.get().strip()
        try:
            size = int(self.size_entry.get().strip())
        except:
            messagebox.showwarning("Input", "Enter valid numeric size (KB)")
            return
        if not proc:
            messagebox.showwarning("Input", "Enter process name")
            return

        if self.mode.get() == "paging":
            ok, info = self.manager.allocate_paging(proc, size)
            if not ok:
                messagebox.showerror("Allocation Failed", info)
            else:
                # animate: just update canvas with small highlight
                self.animate_paging_allocation(proc, info)
        else:
            ok, info = self.manager.allocate_segment(proc, size, policy=self.policy.get())
            if not ok:
                messagebox.showerror("Allocation Failed", info)
            else:
                self.animate_segmentation_allocation(proc, info)
        self.update_info()
        self.redraw()

    def free_process(self):
        proc = self.proc_entry.get().strip()
        if not proc:
            messagebox.showwarning("Input", "Enter process name")
            return
        ok1 = self.manager.free_paging(proc)
        ok2 = self.manager.free_segments_of(proc)
        if not ok1 and not ok2:
            messagebox.showinfo("Free", "No allocation found for process")
        else:
            messagebox.showinfo("Free", f"Freed memory for {proc}")
        self.update_info()
        self.redraw()

    def reset_memory(self):
        self.manager.reset()
        self.update_info()
        self.redraw()

    # ---------------- animations (simple) ----------------
    def animate_paging_allocation(self, proc, frames):
        # flash the allocated frames
        def flash(i, times=6):
            if times <= 0:
                self.redraw()
                return
            self.canvas.delete("flash")
            h = self.canvas.winfo_height()
            w = self.canvas.winfo_width()
            frame_h = max(8, (h-20) / len(self.manager.frames) - 4)
            y = 10 + frames[0] * (frame_h + 4)
            for f in frames:
                y = 10 + f * (frame_h + 4)
                self.canvas.create_rectangle(10, y, w-10, y+frame_h, fill="#ffd9b3", tags="flash")
                self.canvas.create_text(20, y + frame_h/2, text=f"Frame {f}: {proc}", anchor="w", tags="flash")
            self.frame.after(80, lambda: flash(i+1, times-1))

        flash(0)

    def animate_segmentation_allocation(self, proc, seg_info):
        # seg_info is dict with start_kb and size_kb
        # temporary highlight
        def flash(times=6):
            if times <= 0:
                self.redraw()
                return
            self.canvas.delete("flash")
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            total = self.manager.total_kb
            # draw highlight rectangle proportionally
            start = seg_info["start_kb"]
            size = seg_info["size_kb"]
            x0 = 10 + (start / total) * (w-20)
            x1 = 10 + ((start + size) / total) * (w-20)
            self.canvas.create_rectangle(x0, 40, x1, 80, fill="#b3ffd9", tags="flash")
            self.canvas.create_text((x0+x1)/2, 60, text=f"{proc}:{seg_info['seg_id']}", tags="flash")
            self.frame.after(80, lambda: flash(times-1))
        flash(6)

    # ---------------- drawing ----------------
    def redraw(self):
        self.canvas.delete("all")
        if self.mode.get() == "paging":
            self._draw_paging()
        else:
            self._draw_segmentation()

    def _draw_paging(self):
        frames = self.manager.frames
        h = self.canvas.winfo_height() or 600
        w = self.canvas.winfo_width() or 400
        frame_h = max(8, (h-20) / len(frames) - 4)
        y = 10
        for i, owner in enumerate(frames):
            color = "#87cefa" if owner else "#ffffff"
            self.canvas.create_rectangle(10, y, w-10, y+frame_h, fill=color, outline="#cfcfcf")
            text = f"Frame {i}: {owner if owner else 'free'}"
            self.canvas.create_text(20, y+frame_h/2, text=text, anchor="w")
            y += frame_h + 4

    def _draw_segmentation(self):
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 200
        total = self.manager.total_kb
        # draw free / used on a horizontal bar
        self.canvas.create_rectangle(10, 20, w-10, 80, fill="#f7f7f7", outline="#cfcfcf")
        # draw segments
        colors = ["#ffd6a5", "#d1e7dd", "#cfe2ff", "#f8d7da", "#e2e3e5"]
        for idx, seg in enumerate(self.manager.segments):
            start = seg["start_kb"]
            size = seg["size_kb"]
            x0 = 10 + (start / total) * (w-20)
            x1 = 10 + ((start + size) / total) * (w-20)
            color = colors[idx % len(colors)]
            self.canvas.create_rectangle(x0, 20, x1, 80, fill=color, outline="#999999")
            self.canvas.create_text((x0+x1)/2, 50, text=f"{seg['process']}:{seg['seg_id']} ({seg['size_kb']}KB)")

        # draw free blocks
        for start, size in self.manager.free_blocks:
            x0 = 10 + (start / total) * (w-20)
            x1 = 10 + ((start + size) / total) * (w-20)
            self.canvas.create_rectangle(x0, 82, x1, 110, fill="#ffffff", outline="#cccccc")
            self.canvas.create_text((x0+x1)/2, 96, text=f"free {size}KB")

    def update_info(self):
        self.info.delete("1.0", tk.END)
        st = ""
        if self.mode.get() == "paging":
            s = self.manager.get_paging_state()
            st += f"Paging mode\nFrames: {s['num_frames']} (frame size {s['frame_kb']}KB)\n\nPage Table:\n"
            for p, fr in s["page_table"].items():
                st += f"{p} -> frames {fr}\n"
        else:
            s = self.manager.get_segmentation_state()
            st += f"Segmentation mode\nTotal: {s['total_kb']}KB\n\nSegments:\n"
            for seg in s["segments"]:
                st += f"{seg['process']} {seg['seg_id']} @ {seg['start_kb']}KB size {seg['size_kb']}KB\n"
            st += "\nFree blocks:\n"
            for start, size in s["free_blocks"]:
                st += f"{start}KB, {size}KB\n"

        self.info.insert("1.0", st)
