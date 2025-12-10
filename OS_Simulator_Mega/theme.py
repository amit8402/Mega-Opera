class ThemeManager:
    def __init__(self):
        self.current = "light"
        self.colors = {
            "light": {
                "bg": "#ffffff",
                "canvas": "#ffffff",
                "text": "#000000",
                "node_process": "#e8f4ff",
                "node_resource": "#fef4e6",
                "node_border_p": "#6ea8ff",
                "node_border_r": "#ffb86b",
                "arrow_request": "#2b88ff",
                "arrow_alloc": "#28a745",
                "info_bg": "#ffffff"
            },
            "dark": {
                "bg": "#2b2b2b",
                "canvas": "#1e1e1e",
                "text": "#ffffff",
                "node_process": "#333333",
                "node_resource": "#3f3f3f",
                "node_border_p": "#8ab4ff",
                "node_border_r": "#ffc46b",
                "arrow_request": "#76a9fa",
                "arrow_alloc": "#4ade80",
                "info_bg": "#2b2b2b"
            },
            "ocean": {
                "bg": "#c2e9fb",
                "canvas": "#c8e4ff",
                "text": "#003049",
                "node_process": "#d9f1ff",
                "node_resource": "#c7efff",
                "node_border_p": "#0077b6",
                "node_border_r": "#0096c7",
                "arrow_request": "#0077b6",
                "arrow_alloc": "#00a8e8",
                "info_bg": "#d0f3ff"
            },
            "hacker": {
                "bg": "#000000",
                "canvas": "#000000",
                "text": "#00ff00",
                "node_process": "#003300",
                "node_resource": "#001a00",
                "node_border_p": "#00ff00",
                "node_border_r": "#00cc00",
                "arrow_request": "#00ff00",
                "arrow_alloc": "#00cc00",
                "info_bg": "#000000"
            }
        }

    def set_theme(self, name):
        self.current = name

    def get(self):
        return self.colors[self.current]


theme_manager = ThemeManager()
