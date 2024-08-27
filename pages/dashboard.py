import flet as ft

class Dashboard(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page
        self.controls = [ft.Text("Dashboard page")]