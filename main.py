import flet as ft
from pages.registration import Registration
from pages.login import Login
from pages.dashboard import Dashboard
import utils.cred as cred

def main(page: ft.Page):
    page.title = "Routes Example"

    def route_change(e):
        page.views.clear()
        page.views.append(
            ft.View(route="/login",
                    controls=[Login(page, view="/registration")],
                    appbar=ft.AppBar(),
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
        )

        if page.route == "/registration":
            page.views.append(
                ft.View(route="/registration",
                        controls=[Registration(page, view="/login")],
                        appbar=ft.AppBar(toolbar_height=27),
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                        )
            )
        if page.route == "/dashboard":
            if page.session.get(key=cred.login_session_key) != None:
                page.views.clear()
                page.views.append(
                    ft.View(route="/dashboard",
                            controls=[Dashboard(page)],
                            appbar=ft.AppBar()
                            )
            )
            else:
                page.go("/login")

        page.update()


    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)
    
ft.app(target=main)