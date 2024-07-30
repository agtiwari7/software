import flet as ft
from pages.registration import Registration
from pages.login import Login
from pages.dashboard import Dashboard
import utils.cred as cred
import requests
import time

def main(page: ft.Page):
    page.title = "Data Management Software"
    # page routing starts from here
    def route_change(e):
        if page.route == "/login":
            page.session.clear()
            page.views.clear()
            page.views.append(
                ft.View(route="/login",
                        controls=[Login(page, view="/registration")],
                        appbar=ft.AppBar(),
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        )
            )

        if page.route == "/registration":
            page.session.clear()
            page.views.append(
                ft.View(route="/registration",
                        controls=[Registration(page, view="/login")],
                        appbar=ft.AppBar(toolbar_height=27),
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                        )
            )


        if page.route == "/dashboard":
            session_value = page.session.get(key=cred.login_session_key)
            if session_value != None:
                page.views.clear()
                page.views.append(
                    ft.View(route="/dashboard",
                            controls=[Dashboard(page)],
                            drawer=dashboard_drawer ,
                            appbar=ft.AppBar(leading=ft.IconButton(icon=ft.icons.MENU, on_click=open_dashboard_drawer),
                            title=ft.Text(session_value[0],size=30, weight=ft.FontWeight.BOLD, color=ft.colors.LIGHT_BLUE_ACCENT_700),
                            bgcolor="#44CCCCCC",
                            actions=[container]
                            
                                ),
                                  
                            ),
                            )
            else:
                page.go("/login")
        page.update()


    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def on_logout(e):
        page.session.clear()
        page.go("/login")

    def check_internet_connection():
        try:
            while True:
                try:
                    _ = requests.get(url="http://www.google.com", timeout=5)
                    internet_icon.bgcolor=ft.colors.GREEN
                    status.value ="Online"
                except Exception:
                    internet_icon.bgcolor=ft.colors.RED
                    status.value = "Offline"
                page.update()
                time.sleep(2)
        except AssertionError:
            pass

    def open_dashboard_drawer(e):
        page.views[-1].drawer.open = True
        page.update()
    
    def close_dashboard_drawer(e):
        page.views[-1].drawer.open = False
        page.update()

    def handle_change(e: ft.ControlEvent):
        print(f"change on panel with index {e.data}")

    def handle_delete(e: ft.ControlEvent):
        panel.controls.remove(e.control.data)
        page.update()


    panel = ft.ExpansionPanelList(
    expand_icon_color=ft.colors.AMBER,
    elevation=2,
    divider_color=ft.colors.AMBER,
    on_change=handle_change,
    controls=[
        ft.ExpansionPanel(
            header=ft.Text("Panel 1"),
            content=ft.Row([
                ft.Text("This is the content of Panel 1."),
                ft.ElevatedButton("Button 1"),
            ]),
        ),
        ft.ExpansionPanel(
            header=ft.Text("Panel 2"),
            content=ft.Row([
                ft.Text("This is the content of Panel 2."),
                ft.ElevatedButton("Button 2"),
            ]),
        ),
        ft.ExpansionPanel(
            header=ft.Text("Panel 3"),
            content=ft.Row([
                ft.Text("This is the content of Panel 3."),
                ft.ElevatedButton("Button 3"),
            ]),
        )
        ]
    )

    dashboard_drawer = ft.NavigationDrawer(controls=[
                                ft.Row(controls=[ft.Text("Dashboard", size=20, weight=ft.FontWeight.BOLD), ft.IconButton("close", on_click=close_dashboard_drawer)], 
                                       alignment=ft.MainAxisAlignment.SPACE_AROUND, height=50),
                                ft.Divider(),
                                ft.NavigationDrawerDestination("item - 2"),
                                panel
                            ])

    
    
    
    
    
    
    
    
    # adding the STATUS text, internet icon and status text which contains value (online or offline)
    internet_icon = ft.CircleAvatar(radius=7)
    status = ft.Text(size=15)
    logut_btn = ft.IconButton("logout", on_click=on_logout)
    status_row = ft.Row(controls=[internet_icon, status])
    container = ft.Container(content=ft.Row(controls=[status_row, logut_btn], width=200, alignment=ft.MainAxisAlignment.SPACE_EVENLY))
    page.run_thread(handler=check_internet_connection)
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/login")
    
ft.app(target=main)