import os
import re
import json
import base64
import openpyxl
import sqlite3
import hashlib
import requests
import tempfile
import threading
import subprocess
import flet as ft
import pandas as pd
from PIL import Image
import mysql.connector
from io import BytesIO
from utils import cred
from utils import extras
from pages.fees import Fees
from pages.data import Data
from pages.login import Login
from pages.seats import Seats
from pages.income import Income
from pages.history import History
import mysql.connector.locales.eng
from datetime import datetime, date
from pages.admission import Admission
from pages.dashboard import Dashboard
from datetime import datetime, timedelta
from pages.registration import Registration

# # fetch latest version from conf/versoin.json file
# with open('conf/version.json', 'r') as f:
#     data = json.load(f)

# latest_version = data["versions"][-1]["version"]

# Your current version (major.miner.patch)
version = "1.2.2"
current_page = None
current_view = None
# URL to your version.json file on the server
VERSION_URL = "https://agmodal.serv00.net/version.json"
AD_URL = "https://agmodal.serv00.net/ad.json"

temp_dir = tempfile.gettempdir()
modal_dir_path = os.path.join(os.getenv('LOCALAPPDATA'), "Programs", "modal")
main_file_path = os.path.join(os.getenv('LOCALAPPDATA'), "Programs", "modal", "modal.exe")
path = os.path.join(os.getenv('LOCALAPPDATA'), "Programs", "modal", "config")
os.makedirs(path, exist_ok=True)
os.chdir(path)

ad_path = os.path.join(path, "advertisement")
os.makedirs(ad_path, exist_ok=True)

# it is used for check the update of software and if update available, then downlaod and install
def check_and_update(page):
# function, used for check the update
    def check_for_updates():
        try:
            response = requests.get(VERSION_URL, timeout=10)
            server_data = response.json()
            versions = server_data["versions"]

            # Find the latest version in the list
            latest_version_info = None
            for version_info in versions:
                if version_info["version"] > version:
                    if latest_version_info is None or version_info["version"] > latest_version_info["version"]:
                        latest_version_info = version_info
            return latest_version_info  # Return the latest version info if an update is available
        except Exception:
            return None
# used to create a updater script, which install updates.
    def create_updater_script(update_file, main_file_path):
        batch_script_path = os.path.join(tempfile.gettempdir(), "update_modal.bat")
        vbs_script_path = os.path.join(tempfile.gettempdir(), "run_update_silently.vbs")

        with open(batch_script_path, 'w') as script:
            script.write(f"@echo off\n")
            script.write(f"timeout /t 1 /nobreak >nul\n")  # Wait 2 seconds
            script.write(f"move /y \"{update_file}\" \"{main_file_path}\"\n")
            script.write(f"del \"{vbs_script_path}\"\n")  # Delete the VBScript file
            script.write(f"del \"%~f0\" & exit\n")  # Delete the script after execution

        with open(vbs_script_path, 'w') as script:
            script.write(f'Set WshShell = CreateObject("WScript.Shell")\n')
            script.write(f'WshShell.Run chr(34) & "{batch_script_path}" & chr(34), 0\n')
            script.write(f'Set WshShell = Nothing\n')

        return vbs_script_path

# Function to handle update download and restart
    def restart(update_file):
        try:
            page.close(dlg_modal)
        except Exception:
            pass
        if update_file:
            vbs_script_path = create_updater_script(update_file, main_file_path)
            try:
                page.window.destroy()
            except Exception:
                pass
            os.startfile(vbs_script_path)
    
# function to download update
    def download_update(e):
        page.close(dlg_modal)
        try:
            download_url = update_info["url"]
            # Download the update
            response = requests.get(download_url, stream=True, timeout=10)
            update_file = os.path.join(modal_dir_path, f"modal_{update_info['version'].replace('.', '_')}.exe")

            # Save the downloaded file
            with open(update_file, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            try:
                dlg_modal.content = ft.Text("Software updated.\nPlease start the software.")
                dlg_modal.actions = [
                                    ft.ElevatedButton("Okey", color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=lambda _: restart(update_file)),
                                    ft.TextButton("Cancel", on_click=lambda e: page.close(dlg_modal))
                ]
                page.open(dlg_modal)
            except Exception:
                restart(update_file)

        except Exception:
            pass

    update_info = check_for_updates()
    if update_info:
        # Display update available dialog
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=extras.dlg_title_alert,
            surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700,
            content=ft.Text(f"New update is available.\nVersion : {update_info['version']}"),
            actions=[
                ft.ElevatedButton("Download", color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=download_update),
                                  ft.TextButton("Cancel", on_click=lambda e: page.close(dlg_modal))
            ]
        )
        page.open(dlg_modal)
##############################################################################################################################
# check and download ad template from server.
def advertisement():
# fuction , used for remove old ad template.
    def remove_template(new_names_list):
        for file in os.listdir(ad_path):
            if file not in new_names_list:
                os.remove(os.path.join(ad_path, file))

# function, used for check the update
    def check_and_download_template():
        try:
            response = requests.get(AD_URL, timeout=10)
            server_data = response.json()
            names = server_data.keys()
            remove_template(names)
            for name in names:
                if not os.path.exists(os.path.join(ad_path, name)):
                    url = server_data[name]
                    response = requests.get(url, stream=True, timeout=10)
                    file_name = os.path.join("advertisement", name)

            #     # Save the downloaded file
                with open(file_name, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"{name} is saved.")

        except Exception:
            None
    
    check_and_download_template()
##############################################################################################################################

# main flet page app
def main(page: ft.Page):
    page.title = "Modal - Data Management Software"
    is_light_theme = False
    page.theme_mode = "dark"
    page.window.maximized = True

    # create the database tables, user template icon
    if not os.path.exists(f"{path}/template/user.png"):
        os.makedirs(f"{path}/template", exist_ok=True)
        os.makedirs(f"{path}/advertisement", exist_ok=True)
        base64_string = "iVBORw0KGgoAAAANSUhEUgAAAJsAAACdCAYAAACjOAqRAAAP10lEQVR4nO2df2wT5R/HP37ZtATWObIViTuHiIWRCglEulUw0URrrAlCdRqzf2yMLhpSkxL+MNbvwqhf0kkkGX9pLPqHMyFoNf7CGvij6LqhI3IbmXZ0XF3M4q7ZshsLs5257x9LCde7duN+PM89t+eV3B/PB3jufb03z+97njtEURSBQkHAf3ALoKwcqNkoyKBmoyCDmo2CDGo2CjKo2SjIoGajIIOajYIMajYKMqjZKMigZqMgg5qNgowq3AJIolAowPz8PAAA2Gw2qK6uxqyILKjZFMjlcjAyMgJXr16Fixcvwvj4OExPT4MgCJDP5wEA4M477wS73Q51dXXAMAzs3r0bNm/eDM3NzVBfX4/5CczJHXSJ0SJDQ0Nw9uxZ6OnpgfHxcU15MQwDBw8ehKeeegoeeughnRRaAHEFw/O8GIvFRJfLJQKAIZfT6RRPnvxA5Hke9+NiZ0Wajed5MRwOG2awclc4HF7RpltR1WihUIATJ07A4cOHl/X3i22xnTt3wv333w+rV6+GqqrFZu7CwgLcuHEDrl27BpcuXbrZtlsO0WgU3nzzzZXXwcDtdlSkUimRYZiKJY/D4RCDwaCYSCREjuNu+x4cx4mJREIMBoNL3othGDGZTBrwpOZlRZgtGo1WfPE+n09MJBKiIAi63VMQBDGRSIh+v7/ivSORiG73NDuWNpsgCKLX661oMpZlDdfBsmxF03m9Xl2NblYsazaO40SHw6H4cl0uF5YqLJlMlu352u12VVU3SVjSbOn0qGi328v2CPP5PDZt+Xy+Yk84nR7Fps1oLGc2juPKGi2RSOCWd5NEIlHWcJlMBrc8Q7DU0Mfs7Cw0NjaCIAiyP+M4DpqamjCoKk82m4Xt27fL9NrtduA4Durq6jApMwZLrfp4/vnnZS+OYRjged50RgMAaGpqgkwmA06nUxIXBAGeeeYZTKoMBHfRqheRSESx0U3CiD3P84pVfzgcxi1NVyxhtmQyqdj2Ial3x3Gc6duZWiG+zVYoFKCxsREmJycl8UQiAU888QQmVeq4cOECPProo5KY3W6HXC5niakt4tts3d3dMqN1dnYSZzQAgL1790IkEpHEBEGAd999F5MifSG6ZMtms7Bx40ZJzO12w4ULF4guCVpaWmBgYEASM2Nv+nYhumTr6emRxU6cOEG00QAWn6GU999/H70QvcHbZFQPz/OyxrTf78ctSzfa29uJ7vAoQWzJdurUKVksGo1iUGIMR48elcU+/fRTDEp0BLfb1ZDP52WT7O3t7bhl6U5p6Wa327HO62qFyJJtcHBQ1gN99dVXMakxjjfeeEOSFgQB+vv7ManRDpFm++677yRpp9MJLS0tmNQYx65du8DlckliX331FSY12iHSbF1dXZL0Cy+8QHwPVInq6mrYv3+/JHb8+HFMarRDnNmy2awsRuIA7nJ5+umnZbGxsTEMSrRDnNnS6bQs1tzcjEEJGrZs2SKLZTIZDEq0Q5zZfvvtN0na6XRaeruDuro6Wbutr68PkxptEGc2lmUl6T179mBSgo7SZxwaGsKkRBvEma20vbISzLZ7925JemJiApMSbRBltkKhIFuJa7Wl00qUPqMgCFAoFDCpUQ9RZpufn4eZmRlJbM2aNZjUoKP0GWdmZuD69euY1KiHKLMtLCzAP//8I4nZbDZMatBR+owzMzPw77//YlKjHqLMRiEbosxWVVUFd911lyRW3HbUypQ+o81mg1WrVmFSox6izGaz2aC2tlYSm5ubw6QGHaXP6HA4YO3atZjUqIcos1VXV4PdbpfEpqenMalBR+kz2u12IueCiTIbAMCGDRsk6YsXL2JSgo7Lly9L0qW/ASkQZ7adO3dK0j/99BMmJeg4d+6cJL1t2zZMSrRBnNkefvhhSXp4eNjSVens7CwMDw9LYqUzCqRAnNkeeOABWeyPP/7AoAQNV65ckcW2bNmKQYl2iDPbpk2bZLEffvgBgxI0nD9/XhZ78MHNGJRohzizAQCEQiFJ+syZM0TOFS5FoVCAzz77TBILBoOY1GiHSLPt27dPkh4eHobBwUFMaoxjcHBQ1l7z+/2Y1GiHSLMpfdzy4YcfYlBiLJ988oksRvSHPbi/JVSL0nbzpH8xfitKW2iRvo09kSUbAEBbW5ssduTIEQxKjOHYsWOy2IsvvohBiY7gdrsWOjo6ZP/7UZxrYDQsy8qeq6OjA7cszVhuyyyPxwM///wzHkE68cgjj8g+aslkMorDPiRBbDUKsLgBcjgclsT6+vqgu7sbkyLtdHd3y4wWCoWINxoA4ZsBAixO55SuBAEASKVSxPXc+vv7obW1VRYXBAFqamowKNIXoks2AICamhpIJBKyeGtrK+RyOQyK1JHL5RSN9vXXX1vCaAAWMBvA4vYLpbMKAIttHxIMNz09DY899pgsHgqFrHUeAt7+iX7k83nR7XbLenFut1ucmprCLa8sgiCIHo9HUTfJe7EpQXyb7VZyuRw0NDTI4gzDwKVLl0y3TcP09DTs2LFD8QRmnudNp1crlqhGi9TX10M6PSqLj4+PQ0NDg6k20uvv74d169YpGi2dHrWc0QAsZjaAxeU3pfuBFGltbTXFsEh3d7diZwBgcS8TUpcQLQnuetwo0unRskcsut1uLDMNLMsqts+Kl5XPGhVFi5xdVQ6e5yu+3EAggORsT47jxEAgUFaHx+Mh4kA3rVjabKK49MnFRdMlk0nde3+pVKqiyQBADIVClut1lsPyZitS6eTi4uV0OsVwOKzaePl8Xkwmk2JnZ6fodDqXvJ+VTtxbDpYa+liKQqEAXV1dsg2gy8EwDBw4cAB27NgBNpsN6uvrb27yMj8/D7lcDubn5+Hy5cvwxRdfKPYslQiHwxAOh4n80FgTuN2Og0wmIwaDwSVLHr2vYDBo+U5AJVak2YpwHKd4ArPeVyQSsdQqYrUQX40WCgXo7++He++9V9MynP7+fjhz5gycPn162dVhORiGgba2Nti3bx/s3btXdT5jY2Pw119/QUtLiyWqXGLNls1m4fTp09DT03PTHHqdnjw6ehU47hr09fXBn3/+CX///Tdks1mYnJy8eYyRw+EAh8MBTU1NsH79erjvvvvA4/HAxo336zIo++OPP8KTTz4JAIvmPXjwILS1tZF95ijegvX2YVm24nBCNBo15L75fF4UBEGcmpoSp6amREEQDBuyUPqYp3gFAgFil74TYzaWZUWfz7esNpLb7SayIZ5OjyquXFG6fD4fcaYzvdmWGn2vdEWjUVEQBNyPsCSCIFQszSpdqGZB9MDUZltOTzEQCFScIWAYRuzt7cX9KGXp7e0VGYYpqz8UCil+RVZ6RSIR089EmNJsqVSq4gsovoRbhxOSyWTFv180nRleSD6fX9JkANIZBo7jlpx2YxhGTKVSGJ+sMqYyWz6fFzs7Oyv+oOFwuOyktSAIyxqsjUajWKoejuOWVV12dHSUrf55nl/SdOFw2BT/qUoxjdk4jltyhcZyB0ZTqdSyGtper1eMxWKGdibS6VExFouJXq93ST0ul2vZJdNyVpKYbSDZFGarVAU6HA4xmUyqyjcej4t2u33Jl1ysgoLBoBiPx0WWZVVPxLMsK8bjcTEYDC5ZTRYvu92uul2ZTCZFh8NRNm+1v50RYB/UPXXqFAQCAcU/02vC+ssvv4Rjx47BwMDAbf9br9cLW7duBYfDIdNRKBRgcnISfv/9d1UbErpcLujq6oJnn332tv9tqY5KCwxisRi8/PLLmu6hCzidXqm3acTym1QqtayendFXR0eHIQ35SsuoOjs7db/f7YLNbOUa8m632/BVq4IgiPF4XPT7/cgM5vP5xN7eXsPH/XieL9texb05DRazlStdcPwYxQWP0WhU9Hq9y25nVboYhhG9Xq8YiUQMWQG8HMr9Zw4EAsi1FEHeZjt06BAcP35cFo9EIvDWW2+hlKLI7Ows8DwPk5OTMDIyAhMTEzA1NQVzc3Nw/fp1uHHjBgAArF69GtauXQtr1qyBdevWwYYNG6C5uRkcDgc0NDSYYsuE7u5uOHz4sCweCoXgvffeQy8IpbPLjTGdPPkBShkrilgspvib49jFEpnZent7FR86FouhkrBiKWc41L89ErOlUinFhzVqORBFzsmTHyi+A5TTW4abjed5xYHVcDhs9K0pJZSb5kL1zarhZlOapmlvbzf6tpQyKE1xeTweJPc21GxKHQKn02nKSeKVQj6fF10uF5YmjWFDH2NjY4qHmqXTo9bdOIUQcL0bw3Yxeumll2SxeDxOjWYCNm3aBPF4XBY/cGC/sTc2orhU6mrTdpr5UGq/GTkcons1Wm73R6vseG0lyu20btSul7pXo0rH4PT29lKjmZCamhrF6vTo0aPG3FDPYlLpcC+v16vnLSgGoDQ8ZcQqX11LNqVSrbOzU89bUAxA6R0ZcuicXq5VKtX8fr9e2VMMpr29Xfb+9P4oSLeS7aOPPpLF/vc/eUlHMSfvvPNfWezjjz/W9R669EaVejU+nw+++eYbrVlTEPLcc8/B559/LolNTU1BXV2dLvnrUrIpmertt9/WI2sKQg4dOiSLnT17Vr8b6FEXl37v6Xa79ciWggEj36Xmki2bzcrOx3zttde0ZkvBxCuvvCJJDwwMwNjYmC55azbb+fPnZbHHH39ca7YUTCi9u++/P6dP5lqLxtLlKnS4g3xKP3F0Op265KupZMtmszA8PCyJ+f1+LVlSTEB7e7sknU6nIZvNas5Xk9nS6bQs5vF4tGRJMQF79uyRxYaGhjTnq8ls3377rSRd3NCYQjb19fXAMIwkVvqu1aDJbL/88osk/frrr2sSQzEPHR0dkjTLslAoFDTlqdpsuVxONuSxa9cuTWIo5mH79u2SdF9fH8zMzGjKU7XZJiYmZLGWlhZNYijmQeldXr16VVOeqs3266+/ymK1tbWaxFDMQ21trWy+e2RkRFOeupVsPp/PEkfeUBaprq6WnZajVJvdDqrNVnq+09atWzUJoZiPbdu2SdKZTEZTfqrNxrKsJL1+/XpNQijmo/S7kStXrmjKT7XZSmcOGhsbNQmhmI/Sd6pmT+JbUW02QRAkaSM+/aLgRe8CRJXZlAb37rnnHs1iKObi7rvvlsW0DOzq9g2CzbZar6woJkHpnc7Pz6vOT5XZlG64apVh24ZQMKH0ThcWFlTnRx1CQQY1GwUZ1GwUZOhmtlWrVumVFcUk6P1Oq/TK6MiRI7p9zEoxB3Nzc7rmp+qL+HL7elGsj5Yv5GmbjYIMajYKMlS32fx+P10sucKYmZmBqir1zXzsJylTVg60GqUgg5qNggxqNgoyqNkoyKBmoyCDmo2CDGo2CjKo2SjIoGajIIOajYIMajYKMqjZKMigZqMgg5qNggxqNgoyqNkoyKBmoyCDmo2CjP8D/3euqQtzNYoAAAAASUVORK5CYII="
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        image.save(f"{path}/template/user.png")
 
        con = sqlite3.connect(cred.auth_db_name)
        cur = con.cursor()
        cur.execute("create table if not exists soft_reg (bus_name varchar(30), bus_contact bigint unique, bus_password varchar(30), valid_till varchar(15), sys_hash varchar(100), bus_address varchar(50));")
        cur.execute("create table if not exists act_key (soft_reg_contact bigint, act_key varchar(50) unique, valid_till varchar(15), sys_hash varchar(100), FOREIGN KEY (soft_reg_contact) REFERENCES soft_reg(bus_contact));")
        con.commit()
        con.close()
    

    # # Start the update check thread as a daemon
    update_thread = threading.Thread(target=check_and_update, args=(page,))
    update_thread.daemon = True  # Make it a daemon thread
    update_thread.start()

    # # Start the deamon thread for check ad.json file and download ad template.
    update_thread = threading.Thread(target=advertisement)
    update_thread.daemon = True  # Make it a daemon thread
    update_thread.start()

    dlg_modal = ft.AlertDialog(
                modal=True,
                actions=[
                    ft.TextButton("Okay", on_click=lambda e: page.close(dlg_modal), autofocus=True),
                ],
                actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)



    # function handle the page routing of software
    def route_change(e):
        if page.route == "/login":
            page.session.clear()
            page.views.clear()
            os.chdir(path)
            page.views.append(
                ft.View(route="/login",
                        controls=[Login(page, view="/registration")],
                        # appbar=ft.AppBar(actions=[ft.Container(ft.Row([change_theme_btn],alignment=ft.MainAxisAlignment.CENTER, width=100))]),
                        appbar=ft.AppBar(actions=[ft.Container(ft.Row([help_btn],alignment=ft.MainAxisAlignment.CENTER, width=100))]),
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        )
            )

        elif page.route == "/registration":
            page.session.clear()
            page.views.append(
                ft.View(route="/registration",
                        controls=[Registration(page, view="/login")],
                        # appbar=ft.AppBar(actions=[ft.Container(ft.Row([change_theme_btn],alignment=ft.MainAxisAlignment.CENTER, width=100))]),
                        appbar=ft.AppBar(actions=[ft.Container(ft.Row([help_btn],alignment=ft.MainAxisAlignment.CENTER, width=100))]),
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                    )
            )

        elif page.route == "/fees":
            update_content("fees")

        elif page.route == "/data":
            update_content("data")

        elif page.route == "/income":
            update_content("income")

        elif page.route == "/dashboard":
            excel_import_btn.disabled = True
            excel_import_btn.icon_color = ft.colors.GREY_600
            excel_import_btn.tooltip = None
            global session_value
            session_value = page.session.get(key=cred.login_session_key)
            remaining_days = remaining_days_calculate(session_value[3])
            if session_value:
                dashboard = (Dashboard(page, session_value))
                page.views.clear()
                page.views.append(
                    ft.View(route="/dashboard",
                        controls=[ft.Stack([img, dashboard], expand=True)],         # show the dashboard page by default, 
                        # controls=[Dashboard(page, session_value)],         # show the dashboard page by default, 
                        horizontal_alignment = ft.CrossAxisAlignment.CENTER,

                        appbar=ft.AppBar(
                            leading=ft.IconButton(icon=ft.icons.MENU, on_click=open_dashboard_drawer, icon_color=ft.colors.GREY_400),
                            title=ft.Text(session_value[0], size=30, weight=ft.FontWeight.BOLD, color=ft.colors.LIGHT_BLUE_ACCENT_700),
                            bgcolor=extras.main_appbar_color,
                            actions=[container]
                        ),
                        # bgcolor=ft.colors.BLUE_GREY,
                        drawer=ft.NavigationDrawer(
                            controls=[
                                ft.Row(controls=[ft.Text("Drawer", size=28, weight=ft.FontWeight.BOLD),
                                                ft.IconButton("close", on_click=close_dashboard_drawer)
                                                ],
                                                alignment=ft.MainAxisAlignment.SPACE_AROUND, height=50),

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
                                                ft.ListTile(title=ft.TextButton("Data", on_click=lambda _: update_content("data"))),
                                                ft.ListTile(title=ft.TextButton("Fees", on_click=lambda _: update_content("fees"))),
                                            ]),
                                        ),

                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("UTILITIES", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.TextButton("Seats", on_click=lambda _: update_content("seats"))),
                                                ft.ListTile(title=ft.TextButton("History", on_click=lambda _: update_content("history"))),
                                            ]),
                                        ),

                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("INCOME", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.TextButton("Income", on_click=lambda _: update_content("income"))),
                                            ]),
                                        ),

                                        ft.ExpansionPanel(
                                            header=ft.ListTile(title=ft.Text("SOFTWARE", size=16, weight=ft.FontWeight.BOLD)), 
                                            content=ft.Column([
                                                ft.ListTile(title=ft.Text(f"{remaining_days} Day(s) left", size=14, color=ft.colors.RED_300, text_align="center", weight=ft.FontWeight.BOLD)),
                                                ft.ListTile(title=ft.TextButton("Activate", on_click=lambda _: software_activation(remaining_days))),
                                                ft.ListTile(title=ft.TextButton("Help", on_click=lambda _: help_dialogue_box())),
                                                ft.Container(ft.Text(f"Version: {version}", color=ft.colors.GREY), margin=20)
                                            ]),
                                        ),
                                    ]
                                )
                            ]
                        )
                    )
                )
                if remaining_days <=7:
                    software_activation(remaining_days)
            else:
                page.go("/login")
        page.update()

    # remove the last view from view stack
    def view_pop(e):
        try:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        except Exception:
            pass

    # handles the logout functionality and clear the sessoin
    def on_logout(e):
        page.session.clear()
        page.go("/login")

    # used to open the dashboard drawer
    def open_dashboard_drawer(e):
        page.views[-1].drawer.open = True
        page.update()
    
    # used to close the dashboard drawer
    def close_dashboard_drawer(e):
        page.views[-1].drawer.open = False
        page.update()

    # # used to change the all over theme
    # def theme_btn_clicked(e):
    #     nonlocal is_light_theme
    #     if is_light_theme:
    #         page.theme_mode = "dark"
    #         change_theme_btn.icon = ft.icons.WB_SUNNY_OUTLINED
    #     else:
    #         page.theme_mode = "light"
    #         change_theme_btn.icon = ft.icons.BRIGHTNESS_4
    #     is_light_theme = not is_light_theme
    #     page.update()
    
    # remaining days calculate of software activation
    def remaining_days_calculate(valid_date):
        user_date = datetime.strptime(valid_date, "%d-%m-%Y").date()
        remaining_days = (user_date - date.today()).days
        return remaining_days
    
    # generate the system hash for software activation
    def get_sys_hash():
        result = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'], capture_output=True, text=True)
        uuid = result.stdout.strip().split('\n')[-1].strip()
        hash = hashlib.sha256(uuid.encode()).hexdigest()
        return hash

    # help dialogue box, appears when help button is clicked of drawer
    def help_dialogue_box():
        dlg_modal.title = extras.dlg_title_help
        dlg_modal.content = ft.Column([ft.Text("If you have any query or suggestion. Contact us:", size=18),
                                        ft.Divider() ,
                                        ft.Row([ft.Text("Name:", size=16, color=ft.colors.GREEN_400), ft.Text(cred.help_dlg_name, size=16)], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                                        ft.Row([ft.Text("Contact:", size=16, color=ft.colors.GREEN_400), ft.Text(cred.help_dlg_contact, size=16)], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                                        # ft.Row([ft.Text("Email-Id", size=16, color=ft.colors.GREEN_400), ft.Text("agtiwari7@gmail.com", size=16)])
                                ], height=150, width=330)
        try:
            page.views[-1].drawer.open = False
        except Exception:
            pass
        page.update()
        page.open(dlg_modal)

    # show the softawre activation alert dialogue box
    def software_activation(days):
        dlg_title = extras.dlg_title_alert
        dlg_content_heading = ft.Text(f"{days} Day(s) left. Activate now.", size=18)
        global key_tf
        key_tf = ft.TextField(label="Activation Key", max_length=28, prefix_icon=ft.icons.KEY,input_filter=ft.InputFilter(regex_string=r"[a-z, A-Z, 0-9]"))
        dlg_content = ft.Column([dlg_content_heading,
                                        ft.Divider() ,
                                        ft.Container(key_tf, margin=10)
                                        ], height=150, width=360)
        submit_btn = ft.ElevatedButton("Submit", color=extras.main_eb_color, width=extras.main_eb_width, bgcolor=extras.main_eb_bgcolor, on_click=activate_submit_btn_clicked)
        close_btn = ft.TextButton("Close", on_click=lambda e: page.close(dlg_modal))
        # when days is less then equal to zero, then change the heading and hide the close button.
        if days <=0:
            dlg_content_heading.value = "Activate Now."
            close_btn.visible = False
        dlg_modal = ft.AlertDialog(
            title=dlg_title,
            content=dlg_content,
            modal=True,
            actions=[submit_btn, close_btn],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color="#44CCCCCC")
        
        page.views[-1].drawer.open = False
        page.update()
        page.open(dlg_modal)

    # handles the software activation process
    def activate_submit_btn_clicked(e):
        sys_hash = get_sys_hash()
        if key_tf.value != "" and len(key_tf.value) == 28:
            key = key_tf.value
            try:
                str_2 = key[::-1]
                str_1 = str_2.swapcase()
                no_pad = len(str_1)%3
                b64encode = (str_1 + str(no_pad*"=")).encode("utf-8")
                binary = base64.b64decode(b64encode)
                key_format = binary.decode()
                pattern = r'^KEY-\d{8}-\d{4}-\d{3}$'
                result = re.match(pattern, key_format)
                if result is not None:
                    current_date = datetime.now()
                    future_date = current_date + timedelta(days=int(key_format[-3:]))
                    valid_till = future_date.strftime('%d-%m-%Y')
                    try:
                        # remote mysql server data update
                        connection = mysql.connector.connect(
                            host = cred.host,
                            user = cred.user,
                            password = cred.password,
                            database = cred.database
                        )
                        cursor = connection.cursor()

                        soft_reg_sql = "update soft_reg set valid_till=%s where bus_contact=%s AND bus_password=aes_encrypt(%s, %s) AND sys_hash=%s"
                        soft_reg_value = (valid_till, session_value[1], session_value[2], cred.encrypt_key, sys_hash)
                        cursor.execute(soft_reg_sql, soft_reg_value)

                        act_key_sql = "insert into act_key (soft_reg_contact, act_key, valid_till, sys_hash) values (%s, %s, %s, %s)"
                        act_key_value = (session_value[1], key, valid_till, sys_hash)
                        cursor.execute(act_key_sql, act_key_value)

                        connection.commit()
                    except Exception:
                        pass
                    finally:
                        cursor.close()
                        connection.close()

                    try:
                        os.chdir(path)
                        # local mysqlite server data update
                        con = sqlite3.connect(cred.auth_db_name)
                        cur = con.cursor()
                        soft_reg_sql = "update soft_reg set valid_till=? where bus_contact=? AND bus_password=? AND sys_hash=?"
                        soft_reg_value = (valid_till, session_value[1], session_value[2], sys_hash)
                        cur.execute(soft_reg_sql, soft_reg_value)
                        con.commit()

                        act_key_sql = "insert into act_key (soft_reg_contact, act_key, valid_till, sys_hash) values (?, ?, ?, ?)"
                        act_key_value = (session_value[1], key, valid_till, sys_hash)
                        cur.execute(act_key_sql, act_key_value)

                        con.commit()

                        page.session.clear()
                        page.go("/login")
                    except Exception:
                        pass
                    finally:
                        cur.close()
                        con.close()

            except Exception:
                pass
            finally:
                key_tf.value = ""                
        else:
            key_tf.value = ""    
        page.update()

    # used to export database tables data into excel, data carries from different pages.
    def export_to_excel(e):
        def save_file(filename):
            if filename:
                try:
                    download_file_path = os.path.join(os.getenv('userprofile'), "Downloads", filename)
                    df = current_page.get_export_data()
                    df.to_excel(f"{download_file_path}.xlsx", index=False, engine='openpyxl')
                    page.close(dlg_modal)
                except Exception:
                    pass
                

        if current_page:
            alert_text = ft.Text("File will saved in Downloads folder.", weight=ft.FontWeight.W_500, size=16)
            filename_field = ft.TextField(label="File Name", autofocus=True, on_submit=lambda _: save_file(filename_field.value), suffix_text=".xlsx")

            dlg_modal = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Download in Excel", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400),
                        content=ft.Container(content=ft.Column([alert_text, filename_field], spacing=20), width=400, height=100),
                        actions=[
                            ft.ElevatedButton("Download", on_click= lambda _: save_file(filename_field.value), color=ft.colors.GREEN_400),
                            ft.TextButton("Cancel", on_click= lambda _: page.close(dlg_modal)),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700
                    )
            page.open(dlg_modal)
            
        else:
            print("page not found")

    # used to update the content of main dashboard page, according to page user switch
    def update_content(view):
        # Clear existing controls and add new content
        dashboard_view = page.views[-1]
        dashboard_view.controls.clear()
        if view == "admission":
            new_content = Admission(page, session_value)
        elif view == "fees":
            new_content = Fees(page, session_value)
        elif view == "data":
            new_content = Data(page, session_value)
        elif view == "history":
            new_content = History(page, session_value)
        elif view == "seats":
            new_content = Seats(page, session_value)
        elif view == "income":
            new_content = Income(page, session_value)
        elif view == "dashboard":
            new_content = Dashboard(page, session_value)


        global current_page, current_view
        current_view = view
        current_page = new_content

        # changes the excel import button prorperties, based on different pages.
        if (current_view=="admission" or current_view=="seats" or current_view=="dashboard"):
            excel_import_btn.disabled = True
            excel_import_btn.icon_color = ft.colors.GREY_600
            excel_import_btn.tooltip = None
        else:
            excel_import_btn.disabled = False
            excel_import_btn.icon_color = ft.colors.LIME
            excel_import_btn.tooltip="Download in Excel"


        dashboard_view.controls.append(ft.Stack([img, new_content], expand=True))
        page.views[-1].drawer.open = False
        page.update()

    # handles the software close event, it shows the software close popup
    def window_close_event(e):
        if e.data == "close":
            dlg_modal = ft.AlertDialog(
                                    modal=True,
                                    title=extras.dlg_title_alert,
                                    content=ft.Text("Do you want to close the software?"),
                                    actions=[
                                        ft.TextButton("Yes", on_click= lambda _: page.window.destroy()),
                                        ft.TextButton("No", on_click= lambda _: page.close(dlg_modal)),
                                    ],
                                    actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700
                                )
            page.open(dlg_modal)
            page.update()

    def on_resize(event):
        img.width = page.window_width
        img.height = page.window_height
        page.update()

    page.window.prevent_close = True
    page.on_window_event = window_close_event

    img = ft.Image(src="template/bg.png", fit=ft.ImageFit.COVER, width=page.window_width, height=page.window_height)

    excel_import_btn = ft.IconButton(ft.icons.ARROW_DOWNWARD_OUTLINED, on_click=export_to_excel)
    dashboard_page_btn = ft.IconButton(ft.icons.HOME_ROUNDED, on_click=lambda _: update_content("dashboard"), icon_color=ft.colors.LIGHT_BLUE_ACCENT_700, tooltip="Go To Dashboard")
    # change_theme_btn = ft.IconButton(ft.icons.WB_SUNNY_OUTLINED, on_click=theme_btn_clicked, icon_color=ft.colors.GREEN_400, tooltip="Light / Dark Theme")
    help_btn = ft.ElevatedButton("Help", color=ft.colors.DEEP_ORANGE_400, on_click=lambda _: help_dialogue_box())
    logout_btn = ft.IconButton("logout", on_click=on_logout, icon_color=ft.colors.DEEP_ORANGE_400, tooltip="Logout")
    container = ft.Container(content=ft.Row(controls=[excel_import_btn, dashboard_page_btn, logout_btn], width=270, alignment=ft.MainAxisAlignment.SPACE_EVENLY))

    page.on_resize = on_resize
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/login")

ft.app(target=main, assets_dir="assets")