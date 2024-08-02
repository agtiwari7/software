import flet as ft
import requests
import time
import os
from datetime import datetime, date
import utils.cred as cred
from pages.registration import Registration
from pages.login import Login
from pages.dashboard import Dashboard
from pages.admission import Admission
from pages.fees import Fees
from pages.help import Help

def main(page: ft.Page):
    page.title = "Data Management Software"
    is_light_theme = False

    path = os.path.join("config")
    os.makedirs(path, exist_ok=True)
    os.chdir(path)

    def route_change(e):
        if page.route == "/login":
            page.session.clear()
            page.views.clear()
            page.views.append(
                ft.View(route="/login",
                        controls=[Login(page, view="/registration")],
                        appbar=ft.AppBar(actions=[ft.Container(ft.Row([change_theme_btn],alignment=ft.MainAxisAlignment.CENTER, width=100))]),
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        )
            )

        if page.route == "/registration":
            page.session.clear()
            page.views.append(
                ft.View(route="/registration",
                        controls=[Registration(page, view="/login")],
                        appbar=ft.AppBar(actions=[ft.Container(ft.Row([change_theme_btn],alignment=ft.MainAxisAlignment.CENTER, width=100))]),
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                    )
            )

        if page.route == "/dashboard":
            session_value = page.session.get(key=cred.login_session_key)
            if session_value:
                page.views.clear()
                page.views.append(
                    ft.View(route="/dashboard",
                        controls=[Dashboard(page)],         # show the dashboard page by default, 
                        horizontal_alignment = ft.CrossAxisAlignment.CENTER,

                        appbar=ft.AppBar(
                            leading=ft.IconButton(icon=ft.icons.MENU, on_click=open_dashboard_drawer),
                            title=ft.Text(session_value[0], size=30, weight=ft.FontWeight.BOLD, color=ft.colors.LIGHT_BLUE_ACCENT_700),
                            bgcolor="#44CCCCCC",
                            actions=[container]
                        ),

                        drawer=ft.NavigationDrawer(
                            controls=[
                                ft.Row(controls=[
                                    ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
                                    ft.IconButton("close", on_click=close_dashboard_drawer)
                                ], alignment=ft.MainAxisAlignment.SPACE_AROUND, height=50),

                                ft.Divider(),
                                ft.ExpansionPanelList(
                                    expand_icon_color=ft.colors.LIGHT_BLUE_ACCENT_700,
                                    elevation=8,
                                    divider_color=ft.colors.LIGHT_BLUE_ACCENT_700,
                                    controls=[
                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("STUDENTS", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.TextButton("Admission", on_click=lambda _: update_content("admission"))),
                                                ft.ListTile(title=ft.TextButton("Fees", on_click=lambda _: update_content("fees"))),
                                                ft.ListTile(title=ft.TextButton("Attendance")),
                                                ft.ListTile(title=ft.TextButton("View Data")),
                                            ]),
                                        ),

                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("UTILITIES", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.TextButton("Send SMS")),
                                                ft.ListTile(title=ft.TextButton("Seats")),
                                            ]),
                                        ),

                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("INCOME", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.TextButton("")),
                                                ft.ListTile(title=ft.TextButton("")),
                                            ]),
                                        ),

                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("EXPENSE", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.TextButton("")),
                                                ft.ListTile(title=ft.TextButton("")),
                                            ]),
                                        ),

                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("SOFTWARE", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.Text(remaining_days_calculate(session_value[3]), size=14, color=ft.colors.RED_300, text_align="center", weight=ft.FontWeight.BOLD)),
                                                ft.ListTile(title=ft.TextButton("Activation")),
                                                ft.ListTile(title=ft.TextButton("Help", on_click=lambda _: update_content("help"))),
                                            ]),
                                        ),
                                    ]
                                )
                            ]
                        )
                    )
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
                    internet_icon.bgcolor = ft.colors.GREEN
                    status.value = "Online"
                except Exception:
                    internet_icon.bgcolor = ft.colors.RED
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

    def theme_btn_clicked(e):
        nonlocal is_light_theme
        if is_light_theme:
            page.theme_mode = "dark"
            change_theme_btn.icon = ft.icons.WB_SUNNY_OUTLINED
        else:
            page.theme_mode = "light"
            change_theme_btn.icon = ft.icons.BRIGHTNESS_4
        is_light_theme = not is_light_theme
        page.update()
    
    def remaining_days_calculate(valid_date):
        user_date = datetime.strptime(valid_date, "%d-%m-%Y").date()
        remaining_days = f"{(user_date - date.today()).days} Day(s) left"
        return remaining_days

    def update_content(view):
        # Clear existing controls and add new content
        dashboard_view = page.views[-1]
        dashboard_view.controls.clear()
        if view == "admission":
            new_content = Admission(page)
            # dashboard_view.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        elif view == "fees":
            new_content = Fees(page)
        elif view == "help":
            new_content = Help(page)
        else:
            new_content = Dashboard(page)

        dashboard_view.controls.append(new_content)
        page.views[-1].drawer.open = False
        page.update()

    internet_icon = ft.CircleAvatar(radius=7)
    status = ft.Text(size=15)
    logout_btn = ft.IconButton("logout", on_click=on_logout)
    status_row = ft.Row(controls=[internet_icon, status])
    change_theme_btn = ft.IconButton(ft.icons.WB_SUNNY_OUTLINED, on_click=theme_btn_clicked)
    container = ft.Container(content=ft.Row(controls=[status_row, change_theme_btn, logout_btn], width=270, alignment=ft.MainAxisAlignment.SPACE_EVENLY))

    page.run_thread(handler=check_internet_connection)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/login")

ft.app(target=main, assets_dir="assets")
