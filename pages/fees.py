import flet as ft

class Fees(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.controls = [ft.Text("Fees page")]