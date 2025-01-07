import os
import json
import sqlite3
import flet as ft
from utils import extras
from datetime import datetime, timedelta

class Seats(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page
        self.expand = True
        self.divider = ft.Divider(height=1, thickness=3, color=extras.divider_color)
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)

        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)

        self.shift_options = config["shifts"]
        self.shift_options["Custom (Timing)"] = ""

        self.seats_options = config["seats"]

        self.shift_dd = ft.Dropdown(
            label="Shift",
            bgcolor=ft.colors.BLUE_GREY_900,
            width=250,
            options=[ft.dropdown.Option(shift) for shift in self.shift_options],
            on_change=self.shift_dd_change,
            label_style=extras.label_style)
        
        self.timing_dd = ft.Dropdown(
            label="Timing",
            bgcolor=ft.colors.BLUE_GREY_900,
            width=250,
            label_style=extras.label_style)
        
        self.start_tf = ft.TextField(label="Start", width=55, input_filter=ft.InputFilter(regex_string=r"[0-9]"), label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.start_dd = ft.Dropdown(label="AM/PM", width=55, options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.end_tf = ft.TextField(label="End", width=55, input_filter=ft.InputFilter(regex_string=r"[0-9]"), label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.end_dd = ft.Dropdown(label="AM/PM", width=55, options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.timing_container = ft.Container(content=ft.Row([self.start_tf, self.start_dd, self.end_tf, self.end_dd], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), width=250, height=48 , visible=False, border=ft.border.all(1, ft.colors.BLACK), border_radius=5, bgcolor=ft.colors.BLUE_GREY_900)


        self.submit_btn = ft.ElevatedButton("Submit", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.fetch_seat)

        self.top_container = ft.Container(ft.Row(controls=[self.shift_dd, self.timing_dd, self.timing_container, self.submit_btn], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                                          border=ft.Border(bottom=ft.BorderSide(1, ft.colors.GREY)),
                                          padding=ft.Padding(bottom=20, top=10, left=0, right=0))


        self.controls = [self.top_container]

# triggered when shift dropdown changes, means when user select a shift.
    def shift_dd_change(self, e):
        self.timing_dd.value = None
        self.start_tf.value = ""
        self.start_dd.value = None
        self.end_tf.value = ""
        self.end_dd.value = None

        if self.shift_dd.value == "Custom (Timing)":
            self.timing_dd.value = None
            self.timing_dd.visible = False
            self.timing_container.visible = True
            self.start_tf.focus()
        else:
            self.timing_dd.options=[ft.dropdown.Option(timing) for timing in self.shift_options[self.shift_dd.value]]
            self.timing_container.visible = False
            self.timing_dd.visible=True

        self.update()
        
# in behalf of shift and timing, fetch available seats from database. And show them using alert dialogue box
    def fetch_seat(self, e):
        # dividing container into number of rows and columns
        def divide_into_rows(number, max_columns):
            rows = []
            for i in range(0, number, max_columns):
                rows.append(list(range(i + 1, min(i + max_columns + 1, number + 1))))
            return rows

        # it check for conflict timing between new time and olds
        def has_conflict(existing_range, new_student_timing):
            new_start, new_end = new_student_timing.split(" - ")
            existing_start, existing_end = existing_range.split(" - ")
            try:
                existing_start = datetime.strptime(existing_start.strip(), '%I:%M %p')
                existing_end = datetime.strptime(existing_end.strip(), '%I:%M %p')
                new_start = datetime.strptime(new_start.strip(), '%I:%M %p')
                new_end = datetime.strptime(new_end.strip(), '%I:%M %p')
            except ValueError:
                print("Error in time format")
                return False

            # Adjust for overnight shifts
            if existing_end <= existing_start:
                existing_end += timedelta(days=1)
            if new_end <= new_start:
                new_end += timedelta(days=1)

            # Overlap detection
            return not (new_end <= existing_start or new_start >= existing_end)

        # start the main fetch_seat function.
        if self.shift_dd.value != "Custom (Timing)" and not all([self.shift_dd.value, self.timing_dd.value]):
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Please select Shift and Timing.")
            self.page.open(self.dlg_modal)
            self.update()

        elif self.shift_dd.value == "Custom (Timing)" and not all([self.start_tf.value, self.start_dd.value, self.end_tf.value, self.end_dd.value]):
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Please select Shift and Timing.")
            self.page.open(self.dlg_modal)
            self.update()
            
        else:
            try:
                self.controls.clear()
                self.controls.append(self.top_container)

                con = sqlite3.connect(f"{self.session_value[1]}.db")
                cursor = con.cursor()
                cursor.execute(f"select seat, timing from users_{self.session_value[1]}")
                reserved_seats = cursor.fetchall()



                if self.shift_dd.value == "Custom (Timing)":
                    try:
                        start_time = datetime.strptime(f"{self.start_tf.value} {self.start_dd.value}", "%I %p").strftime("%I:%M %p")
                        end_time = datetime.strptime(f"{self.end_tf.value} {self.end_dd.value}", "%I %p").strftime("%I:%M %p")
                    except Exception:
                        return
                    new_student_timing = f"{start_time} - {end_time}"
                else:
                    new_student_timing = self.timing_dd.value

                self.available_seats = self.seats_options.copy()
                self.reserve_seats = dict()
                for seat, existing_range in reserved_seats:
                    if has_conflict(existing_range, new_student_timing):
                        if seat in self.available_seats:
                            self.available_seats.remove(seat)

                        if seat in self.reserve_seats:
                            self.reserve_seats[seat].append(existing_range)
                        else:
                            self.reserve_seats[seat] = [existing_range]

                max_columns = 8  # Maximum number of columns in a row
                rows = divide_into_rows(len(self.seats_options), max_columns)

                for row in rows:
                    container_row = ft.Row(
                        controls=[
                            ft.Container(
                                width=75,
                                height=75,
                                bgcolor=ft.colors.GREEN if f"S{num}" in self.available_seats else 
                                        ft.colors.RED_ACCENT_200 if f"S{num}" in self.reserve_seats else 
                                        ft.colors.BLUE,
                                border_radius=ft.border_radius.all(5),
                                alignment=ft.alignment.center,
                                content=ft.Text(f"S{num}", color=ft.colors.BLACK, weight=ft.FontWeight.BOLD, size=18),
                                on_click=lambda e, seat_no=f"S{num}": self.container_clicked(seat_no)
                            )
                            for num in row
                        ],
                        spacing=10, alignment=ft.MainAxisAlignment.SPACE_EVENLY, expand=True
                    )
                    self.controls.append(container_row)


            except Exception as e:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)
            finally:
                con.close()
                self.update()


    def container_clicked(self, seat):
        if seat in self.reserve_seats:

            try:
                con = sqlite3.connect(f"{self.session_value[1]}.db")
                cursor = con.cursor()

                student_cards = []
                for timing in self.reserve_seats[seat]:
                    sql = f"select * from users_{self.session_value[1]} where timing=? and seat=?"
                    value = (timing, seat)
                    cursor.execute(sql, value)

                    row = cursor.fetchone()
                    card = ft.Card(
                        content=ft.Container(
                            padding=ft.padding.all(10),
                            content=ft.Column(
                                [
                                    ft.Image(src=os.getcwd()+row[14], width=150, height=150, fit=ft.ImageFit.COVER, border_radius=10),
                                    ft.Text(row[1], weight=ft.FontWeight.BOLD, size=18),
                                    ft.Row([ft.Icon(name=ft.icons.PERSON, size=16), ft.Text(f"Mr. {row[2]}", size=14)], spacing=10),
                                    ft.Row([ft.Icon(name=ft.icons.PHONE, size=16), ft.Text(row[3], size=14)], spacing=10),
                                    ft.Row([ft.Icon(name=ft.icons.SWAP_HORIZ, size=16), ft.Text(row[7], size=14)], spacing=10),
                                    ft.Row([ft.Icon(name=ft.icons.ACCESS_TIME, size=16), ft.Text(row[8], size=14)], spacing=10),
                                    ft.Row([ft.Icon(name=ft.icons.EVENT_SEAT, size=16), ft.Text(row[9], size=14)], spacing=10),
                                ],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                        ),
                        elevation=4,
                        margin=ft.margin.all(10),
                        height=420,
                        width=250
                    )
                    student_cards.append(card)

                self.dlg_modal.content = ft.Row(
                    controls=student_cards,
                    spacing=10,
                    scroll="always"
                )

                self.dlg_modal.title = ft.Text("View Details", weight=ft.FontWeight.BOLD, color=ft.colors.LIGHT_BLUE_ACCENT_700, size=19)
                
                self.dlg_modal.actions = [ft.Container(ft.ElevatedButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True, 
                                                                        width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor), width=150, alignment=ft.alignment.center)]
                self.page.open(self.dlg_modal)
                self.update()

            except Exception as e:
                self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)
            finally:
                con.close()

        else:
            self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(f"{seat} is Empty.")
            self.page.open(self.dlg_modal)
