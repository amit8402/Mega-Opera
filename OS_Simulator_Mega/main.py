# main.py
import tkinter as tk
from tkinter import ttk

from tabs.rag_tab import RAGTab
from tabs.memory_tab import MemoryTab
from tabs.tools_tab import ToolsTab
from tabs.cpu_tab import CPUTab
from tabs.process_tab import ProcessTab
from theme import theme_manager


class OSSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Mega Simulator")
        self.root.geometry("1200x750")

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook.Tab", padding=[15, 6], font=("Segoe UI", 11))

        # Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # Tabs
        self.rag_tab = RAGTab(self.notebook)
        self.memory_tab = MemoryTab(self.notebook)
        self.cpu_tab = CPUTab(self.notebook)
        self.process_tab = ProcessTab(self.notebook)   # ✅ FIXED
        self.tools_tab = ToolsTab(self.notebook)

        # Add Tabs
        self.notebook.add(self.rag_tab.frame, text="Resource Graph")
        self.notebook.add(self.memory_tab.frame, text="Memory Manager")
        self.notebook.add(self.cpu_tab.frame, text="CPU Scheduling")
        self.notebook.add(self.process_tab.frame, text="Process State")
        self.notebook.add(self.tools_tab.frame, text="Tools")

        # Theme refresh
        theme_manager.refresh = self.refresh_theme

    def refresh_theme(self):
        theme = theme_manager.get()
        self.root.configure(bg=theme["bg"])

        try: self.rag_tab.redraw()
        except: pass

        try: self.memory_tab.redraw()
        except: pass

        try: self.cpu_tab.reset()
        except: pass

        try: self.process_tab.redraw()
        except: pass


def main():
    root = tk.Tk()
    OSSimulatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
