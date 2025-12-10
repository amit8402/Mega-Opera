import tkinter as tk
from theme import theme_manager

class ToolsTab:
    def __init__(self, parent):
        theme = theme_manager.get()

        self.frame = tk.Frame(parent, bg=theme["bg"])

        tk.Label(
            self.frame,
            text="Theme Settings",
            font=("Segoe UI", 14, "bold"),
            bg=theme["bg"],
            fg=theme["text"]
        ).pack(pady=12)

        tk.Button(self.frame, text="Light Theme",
                  command=lambda: self.apply_theme("light"), width=20).pack(pady=6)
        tk.Button(self.frame, text="Dark Theme",
                  command=lambda: self.apply_theme("dark"), width=20).pack(pady=6)
        tk.Button(self.frame, text="Ocean Blue",
                  command=lambda: self.apply_theme("ocean"), width=20).pack(pady=6)
        tk.Button(self.frame, text="Hacker Theme",
                  command=lambda: self.apply_theme("hacker"), width=20).pack(pady=6)

        tk.Label(
            self.frame,
            text="\n• Theme applies instantly\n• RAG + Memory will update\n",
            bg=theme["bg"],
            fg=theme["text"]
        ).pack()

    def apply_theme(self, name):
        theme_manager.set_theme(name)
        if hasattr(theme_manager, "refresh"):
            theme_manager.refresh()   # ← THIS was missing
