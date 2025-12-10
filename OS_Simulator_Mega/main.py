# main.py
import tkinter as tk
from tkinter import ttk

from tabs.rag_tab import RAGTab
from tabs.memory_tab import MemoryTab
from tabs.tools_tab import ToolsTab
from theme import theme_manager


class OSSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Mega Simulator")
        self.root.geometry("1200x750")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook.Tab", padding=[15, 6], font=("Segoe UI", 11))

        # Notebook
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        # Tabs
        self.rag_tab = RAGTab(notebook)
        self.memory_tab = MemoryTab(notebook)
        self.tools_tab = ToolsTab(notebook)

        notebook.add(self.rag_tab.frame, text="Resource Graph")
        notebook.add(self.memory_tab.frame, text="Memory Manager")
        notebook.add(self.tools_tab.frame, text="Tools")

        # Register theme refresh
        def refresh_theme():
            theme = theme_manager.get()
            root.configure(bg=theme["bg"])
            self.rag_tab.redraw()
            try:
                self.memory_tab.redraw()
            except:
                pass

        theme_manager.refresh = refresh_theme


def main():
    root = tk.Tk()
    OSSimulatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
