import os
import time
import base64
import sqlite3
import requests
import flet as ft
from PIL import Image
from io import BytesIO
from utils import cred
from pages.help import Help
from pages.fees import Fees
from pages.login import Login
from datetime import datetime, date
from pages.dashboard import Dashboard
from pages.admission import Admission
from pages.registration import Registration

def main(page: ft.Page):
    path = "config"
    if os.path.exists(path):
        os.chdir(path)

    else:
        os.makedirs(f"{path}/photo/current", exist_ok=True)
        os.makedirs(f"{path}/photo/delete", exist_ok=True)
        os.makedirs(f"{path}/photo/template", exist_ok=True)
        os.chdir(path)
        
        con = sqlite3.connect("software.db")
        cur = con.cursor()
        cur.execute("create table if not exists soft_reg (id INTEGER PRIMARY KEY AUTOINCREMENT, bus_name varchar(30), bus_contact bigint unique, bus_password varchar(30), act_key varchar(50) unique, valid_till varchar(15));")
        con.commit()
        con.close()

        base64_string = "iVBORw0KGgoAAAANSUhEUgAAAJsAAACdCAYAAACjOAqRAAAP10lEQVR4nO2df2wT5R/HP37ZtATWObIViTuHiIWRCglEulUw0URrrAlCdRqzf2yMLhpSkxL+MNbvwqhf0kkkGX9pLPqHMyFoNf7CGvij6LqhI3IbmXZ0XF3M4q7ZshsLs5257x9LCde7duN+PM89t+eV3B/PB3jufb03z+97njtEURSBQkHAf3ALoKwcqNkoyKBmoyCDmo2CDGo2CjKo2SjIoGajIIOajYIMajYKMqjZKMigZqMgg5qNgowq3AJIolAowPz8PAAA2Gw2qK6uxqyILKjZFMjlcjAyMgJXr16Fixcvwvj4OExPT4MgCJDP5wEA4M477wS73Q51dXXAMAzs3r0bNm/eDM3NzVBfX4/5CczJHXSJ0SJDQ0Nw9uxZ6OnpgfHxcU15MQwDBw8ehKeeegoeeughnRRaAHEFw/O8GIvFRJfLJQKAIZfT6RRPnvxA5Hke9+NiZ0Wajed5MRwOG2awclc4HF7RpltR1WihUIATJ07A4cOHl/X3i22xnTt3wv333w+rV6+GqqrFZu7CwgLcuHEDrl27BpcuXbrZtlsO0WgU3nzzzZXXwcDtdlSkUimRYZiKJY/D4RCDwaCYSCREjuNu+x4cx4mJREIMBoNL3othGDGZTBrwpOZlRZgtGo1WfPE+n09MJBKiIAi63VMQBDGRSIh+v7/ivSORiG73NDuWNpsgCKLX661oMpZlDdfBsmxF03m9Xl2NblYsazaO40SHw6H4cl0uF5YqLJlMlu352u12VVU3SVjSbOn0qGi328v2CPP5PDZt+Xy+Yk84nR7Fps1oLGc2juPKGi2RSOCWd5NEIlHWcJlMBrc8Q7DU0Mfs7Cw0NjaCIAiyP+M4DpqamjCoKk82m4Xt27fL9NrtduA4Durq6jApMwZLrfp4/vnnZS+OYRjged50RgMAaGpqgkwmA06nUxIXBAGeeeYZTKoMBHfRqheRSESx0U3CiD3P84pVfzgcxi1NVyxhtmQyqdj2Ial3x3Gc6duZWiG+zVYoFKCxsREmJycl8UQiAU888QQmVeq4cOECPProo5KY3W6HXC5niakt4tts3d3dMqN1dnYSZzQAgL1790IkEpHEBEGAd999F5MifSG6ZMtms7Bx40ZJzO12w4ULF4guCVpaWmBgYEASM2Nv+nYhumTr6emRxU6cOEG00QAWn6GU999/H70QvcHbZFQPz/OyxrTf78ctSzfa29uJ7vAoQWzJdurUKVksGo1iUGIMR48elcU+/fRTDEp0BLfb1ZDP52WT7O3t7bhl6U5p6Wa327HO62qFyJJtcHBQ1gN99dVXMakxjjfeeEOSFgQB+vv7ManRDpFm++677yRpp9MJLS0tmNQYx65du8DlckliX331FSY12iHSbF1dXZL0Cy+8QHwPVInq6mrYv3+/JHb8+HFMarRDnNmy2awsRuIA7nJ5+umnZbGxsTEMSrRDnNnS6bQs1tzcjEEJGrZs2SKLZTIZDEq0Q5zZfvvtN0na6XRaeruDuro6Wbutr68PkxptEGc2lmUl6T179mBSgo7SZxwaGsKkRBvEma20vbISzLZ7925JemJiApMSbRBltkKhIFuJa7Wl00qUPqMgCFAoFDCpUQ9RZpufn4eZmRlJbM2aNZjUoKP0GWdmZuD69euY1KiHKLMtLCzAP//8I4nZbDZMatBR+owzMzPw77//YlKjHqLMRiEbosxWVVUFd911lyRW3HbUypQ+o81mg1WrVmFSox6izGaz2aC2tlYSm5ubw6QGHaXP6HA4YO3atZjUqIcos1VXV4PdbpfEpqenMalBR+kz2u12IueCiTIbAMCGDRsk6YsXL2JSgo7Lly9L0qW/ASkQZ7adO3dK0j/99BMmJeg4d+6cJL1t2zZMSrRBnNkefvhhSXp4eNjSVens7CwMDw9LYqUzCqRAnNkeeOABWeyPP/7AoAQNV65ckcW2bNmKQYl2iDPbpk2bZLEffvgBgxI0nD9/XhZ78MHNGJRohzizAQCEQiFJ+syZM0TOFS5FoVCAzz77TBILBoOY1GiHSLPt27dPkh4eHobBwUFMaoxjcHBQ1l7z+/2Y1GiHSLMpfdzy4YcfYlBiLJ988oksRvSHPbi/JVSL0nbzpH8xfitKW2iRvo09kSUbAEBbW5ssduTIEQxKjOHYsWOy2IsvvohBiY7gdrsWOjo6ZP/7UZxrYDQsy8qeq6OjA7cszVhuyyyPxwM///wzHkE68cgjj8g+aslkMorDPiRBbDUKsLgBcjgclsT6+vqgu7sbkyLtdHd3y4wWCoWINxoA4ZsBAixO55SuBAEASKVSxPXc+vv7obW1VRYXBAFqamowKNIXoks2AICamhpIJBKyeGtrK+RyOQyK1JHL5RSN9vXXX1vCaAAWMBvA4vYLpbMKAIttHxIMNz09DY899pgsHgqFrHUeAt7+iX7k83nR7XbLenFut1ucmprCLa8sgiCIHo9HUTfJe7EpQXyb7VZyuRw0NDTI4gzDwKVLl0y3TcP09DTs2LFD8QRmnudNp1crlqhGi9TX10M6PSqLj4+PQ0NDg6k20uvv74d169YpGi2dHrWc0QAsZjaAxeU3pfuBFGltbTXFsEh3d7diZwBgcS8TUpcQLQnuetwo0unRskcsut1uLDMNLMsqts+Kl5XPGhVFi5xdVQ6e5yu+3EAggORsT47jxEAgUFaHx+Mh4kA3rVjabKK49MnFRdMlk0nde3+pVKqiyQBADIVClut1lsPyZitS6eTi4uV0OsVwOKzaePl8Xkwmk2JnZ6fodDqXvJ+VTtxbDpYa+liKQqEAXV1dsg2gy8EwDBw4cAB27NgBNpsN6uvrb27yMj8/D7lcDubn5+Hy5cvwxRdfKPYslQiHwxAOh4n80FgTuN2Og0wmIwaDwSVLHr2vYDBo+U5AJVak2YpwHKd4ArPeVyQSsdQqYrUQX40WCgXo7++He++9V9MynP7+fjhz5gycPn162dVhORiGgba2Nti3bx/s3btXdT5jY2Pw119/QUtLiyWqXGLNls1m4fTp09DT03PTHHqdnjw6ehU47hr09fXBn3/+CX///Tdks1mYnJy8eYyRw+EAh8MBTU1NsH79erjvvvvA4/HAxo336zIo++OPP8KTTz4JAIvmPXjwILS1tZF95ijegvX2YVm24nBCNBo15L75fF4UBEGcmpoSp6amREEQDBuyUPqYp3gFAgFil74TYzaWZUWfz7esNpLb7SayIZ5OjyquXFG6fD4fcaYzvdmWGn2vdEWjUVEQBNyPsCSCIFQszSpdqGZB9MDUZltOTzEQCFScIWAYRuzt7cX9KGXp7e0VGYYpqz8UCil+RVZ6RSIR089EmNJsqVSq4gsovoRbhxOSyWTFv180nRleSD6fX9JkANIZBo7jlpx2YxhGTKVSGJ+sMqYyWz6fFzs7Oyv+oOFwuOyktSAIyxqsjUajWKoejuOWVV12dHSUrf55nl/SdOFw2BT/qUoxjdk4jltyhcZyB0ZTqdSyGtper1eMxWKGdibS6VExFouJXq93ST0ul2vZJdNyVpKYbSDZFGarVAU6HA4xmUyqyjcej4t2u33Jl1ysgoLBoBiPx0WWZVVPxLMsK8bjcTEYDC5ZTRYvu92uul2ZTCZFh8NRNm+1v50RYB/UPXXqFAQCAcU/02vC+ssvv4Rjx47BwMDAbf9br9cLW7duBYfDIdNRKBRgcnISfv/9d1UbErpcLujq6oJnn332tv9tqY5KCwxisRi8/PLLmu6hCzidXqm3acTym1QqtayendFXR0eHIQ35SsuoOjs7db/f7YLNbOUa8m632/BVq4IgiPF4XPT7/cgM5vP5xN7eXsPH/XieL9texb05DRazlStdcPwYxQWP0WhU9Hq9y25nVboYhhG9Xq8YiUQMWQG8HMr9Zw4EAsi1FEHeZjt06BAcP35cFo9EIvDWW2+hlKLI7Ows8DwPk5OTMDIyAhMTEzA1NQVzc3Nw/fp1uHHjBgAArF69GtauXQtr1qyBdevWwYYNG6C5uRkcDgc0NDSYYsuE7u5uOHz4sCweCoXgvffeQy8IpbPLjTGdPPkBShkrilgspvib49jFEpnZent7FR86FouhkrBiKWc41L89ErOlUinFhzVqORBFzsmTHyi+A5TTW4abjed5xYHVcDhs9K0pJZSb5kL1zarhZlOapmlvbzf6tpQyKE1xeTweJPc21GxKHQKn02nKSeKVQj6fF10uF5YmjWFDH2NjY4qHmqXTo9bdOIUQcL0bw3Yxeumll2SxeDxOjWYCNm3aBPF4XBY/cGC/sTc2orhU6mrTdpr5UGq/GTkcons1Wm73R6vseG0lyu20btSul7pXo0rH4PT29lKjmZCamhrF6vTo0aPG3FDPYlLpcC+v16vnLSgGoDQ8ZcQqX11LNqVSrbOzU89bUAxA6R0ZcuicXq5VKtX8fr9e2VMMpr29Xfb+9P4oSLeS7aOPPpLF/vc/eUlHMSfvvPNfWezjjz/W9R669EaVejU+nw+++eYbrVlTEPLcc8/B559/LolNTU1BXV2dLvnrUrIpmertt9/WI2sKQg4dOiSLnT17Vr8b6FEXl37v6Xa79ciWggEj36Xmki2bzcrOx3zttde0ZkvBxCuvvCJJDwwMwNjYmC55azbb+fPnZbHHH39ca7YUTCi9u++/P6dP5lqLxtLlKnS4g3xKP3F0Op265KupZMtmszA8PCyJ+f1+LVlSTEB7e7sknU6nIZvNas5Xk9nS6bQs5vF4tGRJMQF79uyRxYaGhjTnq8ls3377rSRd3NCYQjb19fXAMIwkVvqu1aDJbL/88osk/frrr2sSQzEPHR0dkjTLslAoFDTlqdpsuVxONuSxa9cuTWIo5mH79u2SdF9fH8zMzGjKU7XZJiYmZLGWlhZNYijmQeldXr16VVOeqs3266+/ymK1tbWaxFDMQ21trWy+e2RkRFOeupVsPp/PEkfeUBaprq6WnZajVJvdDqrNVnq+09atWzUJoZiPbdu2SdKZTEZTfqrNxrKsJL1+/XpNQijmo/S7kStXrmjKT7XZSmcOGhsbNQmhmI/Sd6pmT+JbUW02QRAkaSM+/aLgRe8CRJXZlAb37rnnHs1iKObi7rvvlsW0DOzq9g2CzbZar6woJkHpnc7Pz6vOT5XZlG64apVh24ZQMKH0ThcWFlTnRx1CQQY1GwUZ1GwUZOhmtlWrVumVFcUk6P1Oq/TK6MiRI7p9zEoxB3Nzc7rmp+qL+HL7elGsj5Yv5GmbjYIMajYKMlS32fx+P10sucKYmZmBqir1zXzsJylTVg60GqUgg5qNggxqNgoyqNkoyKBmoyCDmo2CDGo2CjKo2SjIoGajIIOajYIMajYKMqjZKMigZqMgg5qNggxqNgoyqNkoyKBmoyCDmo2CjP8D/3euqQtzNYoAAAAASUVORK5CYII="
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        base_path = os.getcwd().replace('\\','/')
        image.save(f"{base_path}/photo/template/user.png")

    page.title = "Data Management Software"
    is_light_theme = False
    page.theme_mode = "dark"

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
            global session_value
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
                                                ft.ListTile(title=ft.TextButton("View Data")),
                                                ft.ListTile(title=ft.TextButton("Fees", on_click=lambda _: update_content("fees"))),
                                                # ft.ListTile(title=ft.TextButton("Attendance")),
                                            ]),
                                        ),

                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("UTILITIES", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.TextButton("Send SMS")),
                                                # ft.ListTile(title=ft.TextButton("Seats")),
                                            ]),
                                        ),

                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("INCOME", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.TextButton("")),
                                                # ft.ListTile(title=ft.TextButton("")),
                                            ]),
                                        ),

                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("EXPENSE", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.TextButton("")),
                                                # ft.ListTile(title=ft.TextButton("")),
                                            ]),
                                        ),

                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("SOFTWARE", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.Text(remaining_days_calculate(session_value[3]), size=14, color=ft.colors.RED_300, text_align="center", weight=ft.FontWeight.BOLD)),
                                                ft.ListTile(title=ft.TextButton("Activate")),
                                                ft.ListTile(title=ft.TextButton("Update")),
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
            new_content = Admission(page, session_value)
            # dashboard_view.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        elif view == "fees":
            new_content = Fees(page, session_value)
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
