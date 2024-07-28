import flet as ft

class Dashboard(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.text = ft.Text("Software Home Page", size=40)
        # self.page = page
        self.logout_btn = ft.ElevatedButton("logout", on_click=self.on_logout)
        self.controls=[self.text, self.logout_btn]

    def build(self):
        self.page.session.clear()
        self.page.views.clear()


    def on_logout(self, e):
        self.page.session.clear()
        self.page.go("/login")
        