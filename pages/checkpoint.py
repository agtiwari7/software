import os
import subprocess
import flet as ft
from utils import cred, extras

class Checkpoint(ft.Column):
    def __init__(self, page, error):
        super().__init__()
        self.page = page
        self.error = error

        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)


        warning_text = ft.Text(size=26, weight=ft.FontWeight.BOLD, color=ft.colors.RED_ACCENT, text_align=ft.TextAlign.CENTER)
        instruction_text = ft.Text(size=18, color=ft.colors.GREEN_400, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD)









        if error == "SYSTEM DATE ERROR":
            warning_icon = ft.Icon(name=ft.icons.ACCESS_TIME_FILLED, size=150, color=ft.colors.RED)
            warning_text.value = "System clock is incorrect"
            instruction_text.value = "Please correct the date and time, then restart the software."
            button = ft.ElevatedButton(
                text="Open Date and Time Settings",
                on_click=lambda _: self.open_date_time_settings(),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE,
            )


        if error == "CHECKPOINT ERROR":
            warning_icon = ft.Icon(name=ft.icons.WARNING_AMBER_ROUNDED, size=150, color=ft.colors.RED)
            warning_text.value = "Checkpoint System Error"
            instruction_text.value = "Please Contact the Admin"
            button = ft.ElevatedButton(
                text="Help",
                on_click=lambda _: self.help_dialogue_box(),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE,
            )

        main_element = ft.Column([ft.Column([warning_icon,warning_text], spacing=20, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.Column([instruction_text,button], spacing=20, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=50,
                        )
        self.controls = [main_element]

# used to open the date-time edit window's popup
    def open_date_time_settings(self):
        try:
            subprocess.Popen(["cmd.exe", "/c", "start", "timedate.cpl"], shell=True)
        except Exception as e:
            print(e)

# help dialogue box, appears when help button is clicked of drawer
    def help_dialogue_box(self):
        self.dlg_modal.title = extras.dlg_title_help
        self.dlg_modal.content = ft.Column([ft.Text("If you have any query or suggestion. Contact us:", size=18),
                                        ft.Divider() ,
                                        ft.Row([ft.Text("Name:", size=16, color=ft.colors.GREEN_400), ft.Text(cred.help_dlg_name, size=16)], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                                        ft.Row([ft.Text("Contact:", size=16, color=ft.colors.GREEN_400), ft.Text(cred.help_dlg_contact, size=16)], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                                ], height=150, width=330)
        self.page.open(self.dlg_modal)