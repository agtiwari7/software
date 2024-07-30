import flet as ft
import utils.cred as cred

class Dashboard(ft.Column):
    def __init__(self, page):
        super().__init__()

        self.page = page
        self.session_value = page.session.get(key=cred.login_session_key)
        
        
        self.text = ft.Text("dashboard home page")
        
        self.controls=[self.text]


    # def on_logout(self, e):
    #     self.page.session.clear()
    #     self.page.go("/login")
        