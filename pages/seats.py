import flet as ft
import json
from utils import extras

class Seats(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page
        self.expand = True

        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)

        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)

        self.shift_options = config.get("shift", [])
        self.timing_options = config.get("timing", [])
        self.seats_options = config.get("seats", [])
        self.fees_options = config.get("fees", [])

        self.shift_dd = ft.Dropdown(
            label="Shift",
            bgcolor=ft.colors.BLUE_GREY_900,
            width=250,
            options=[ft.dropdown.Option(shift) for shift in self.shift_options],
            label_style=extras.label_style)
        
        self.timing_dd = ft.Dropdown(
            label="Timing",
            bgcolor=ft.colors.BLUE_GREY_900,
            width=250,
            options=[ft.dropdown.Option(timing) for timing in self.timing_options],
            label_style=extras.label_style)
        
        self.submit_btn = ft.ElevatedButton("Submit", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.submit_btn_clicked)

        self.top_container = ft.Container(ft.Row(controls=[self.shift_dd, self.timing_dd, self.submit_btn], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                                          border=ft.Border(bottom=ft.BorderSide(1, ft.colors.GREY)),
                                          padding=ft.Padding(bottom=20, top=10, left=0, right=0))


        self.controls = [self.top_container]

    def submit_btn_clicked(self, e):
        pass