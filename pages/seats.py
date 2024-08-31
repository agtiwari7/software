import flet as ft
import json
from utils import extras
from datetime import datetime, timedelta
import sqlite3

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
        
        self.submit_btn = ft.ElevatedButton("Submit", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.fetch_seat)

        self.top_container = ft.Container(ft.Row(controls=[self.shift_dd, self.timing_dd, self.submit_btn], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                                          border=ft.Border(bottom=ft.BorderSide(1, ft.colors.GREY)),
                                          padding=ft.Padding(bottom=20, top=10, left=0, right=0))


        self.controls = [self.top_container]

# triggered when shift dropdown changes, means when user select a shift.
    def shift_dd_change(self, e):
        self.timing_dd.options=[ft.dropdown.Option(timing) for timing in self.shift_options[self.shift_dd.value]]
        self.timing_dd.update()

# in behalf of shift and timing, fetch available seats from database. And show them using alert dialogue box
    def fetch_seat(self, e):


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
        if not all([self.shift_dd.value, self.timing_dd.value]):
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

                self.available_seats = self.seats_options.copy()
                self.reserve_seats = []
                for seat, existing_range in reserved_seats:
                    if has_conflict(existing_range, self.timing_dd.value):
                        if seat in self.available_seats:
                            self.available_seats.remove(seat)
                            self.reserve_seats.append(seat)

                max_columns = 8  # Maximum number of columns in a row
                rows = divide_into_rows(len(self.seats_options), max_columns)

                for row in rows:
                    container_row = ft.Row(
                        controls=[
                            ft.Container(
                                width=75,
                                height=75,
                                bgcolor=ft.colors.GREEN if f"s{num}" in self.available_seats else 
                                        ft.colors.RED_ACCENT_200 if f"s{num}" in self.reserve_seats else 
                                        ft.colors.BLUE,
                                border_radius=ft.border_radius.all(5),
                                alignment=ft.alignment.center,
                                content=ft.Text(f"s{num}", color=ft.colors.BLACK, weight=ft.FontWeight.BOLD, size=18),
                                on_click=lambda e, seat_no=f"s{num}": self.container_clicked(seat_no)
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
            print(f"{seat} is filled.")


            # try:
            #     con = sqlite3.connect(f"{self.session_value[1]}.db")
            #     cursor = con.cursor()
            #     sql = f"select * from users_{self.session_value[1]} where timing=? and seat=?"
            #     value = (self.timing_dd.value, seat)
            #     cursor.execute(sql, value)
                
            #     row = cursor.fetchone()
            #     self.current_view_popup(row)
            # except sqlite3.OperationalError:
            #     self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            #     self.dlg_modal.title = extras.dlg_title_error
            #     self.dlg_modal.content = ft.Text("Database not found.")
            #     self.page.open(self.dlg_modal)
            # except Exception as e:
            #     self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            #     self.dlg_modal.title = extras.dlg_title_error
            #     self.dlg_modal.content = ft.Text(e)
            #     self.page.open(self.dlg_modal)
            # finally:
            #     con.close()

        else:
            print(f"{seat} is empty.")


# show all total detail of users using alert dialogue box from user_(contact) table of database
    def current_view_popup(self, row):
        img = ft.Image(src=row[14], height=200, width=250)
        name_field = ft.TextField(label="Name", value=row[1], width=300, read_only=True, label_style=extras.label_style)
        father_name_field = ft.TextField(label="Father Name", value=row[2], width=300, read_only=True, label_style=extras.label_style)
        contact_field = ft.TextField(label="Contact", value=row[3], width=300, read_only=True, label_style=extras.label_style)
        aadhar_field = ft.TextField(label="Aadhar", value=row[4], width=300, read_only=True, label_style=extras.label_style)
        address_field = ft.TextField(label="Address", value=row[5], width=440, read_only=True, label_style=extras.label_style)
        gender_field = ft.TextField(label="Gender", value=row[6], width=160, read_only=True, label_style=extras.label_style)
        shift_field = ft.TextField(label="Shift", value=row[7], width=225, read_only=True, label_style=extras.label_style)
        timing_field = ft.TextField(label="Timing", value=row[8], width=225, read_only=True, label_style=extras.label_style)
        seat_field = ft.TextField(label="Seat", value=row[9], width=225, read_only=True, label_style=extras.label_style)
        fees_field = ft.TextField(label="Fees", value=row[10], width=225, read_only=True, label_style=extras.label_style)
        joining_field = ft.TextField(label="Joining", value=row[11], width=225, read_only=True, label_style=extras.label_style)
        enrollment_field = ft.TextField(label="Enrollment No.", value=row[12], width=225, read_only=True, label_style=extras.label_style)
        payed_till_field = ft.TextField(label="Fees Payed Till", value=row[13], width=225, read_only=True, label_style=extras.label_style)
        due_fees_field = ft.TextField(label="Due Fees", width=225, text_style=ft.TextStyle(color=ft.colors.ORANGE_ACCENT_400, weight=ft.FontWeight.BOLD), read_only=True, label_style=extras.label_style)
        
        payed_till_formatted_date = datetime.strptime(row[13], "%d-%m-%Y")
        difference = (datetime.now() - payed_till_formatted_date).days
        if difference > 0:
            due_fees = int(difference * (int(row[10])/30))
            due_fees_field.value = due_fees
        else:
            due_fees_field.value = 0

        name_father_name_row = ft.Row([name_field, father_name_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        contact_aadhar_row = ft.Row([contact_field, aadhar_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        address_gender_row = ft.Row([address_field, gender_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        shift_timing_seat_fees_row = ft.Row([shift_field, timing_field, seat_field, fees_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        joining_enrollment_payed_till_due_fees_row = ft.Row([joining_field, enrollment_field, payed_till_field, due_fees_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        container_1 = ft.Container(content=ft.Column(controls=[img], horizontal_alignment=ft.CrossAxisAlignment.CENTER), width=350)
        container_2 = ft.Container(content=ft.Column(controls=[name_father_name_row, contact_aadhar_row, address_gender_row], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER ), padding=20, expand=True)
        container_3 = ft.Container(content=ft.Column(controls=[shift_timing_seat_fees_row, joining_enrollment_payed_till_due_fees_row], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER ), expand=True, padding=20)
        
        main_container = ft.Container(content=ft.Column(controls=[
                                                                    ft.Container(ft.Row([container_1, container_2])),
                                                                    self.divider,
                                                                    container_3,
                                                                    ], spacing=15
                                                            ),
                                                            width=1050, 
                                                            height=430,
                                                            padding=10,
                                                            border_radius=extras.main_container_border_radius, 
                                                            bgcolor=extras.main_container_bgcolor,
                                                            border=extras.main_container_border
                                            )
        self.dlg_modal.title = ft.Text("View Details", weight=ft.FontWeight.BOLD, color=ft.colors.LIGHT_BLUE_ACCENT_700, size=19)
        self.dlg_modal.content = main_container
        
        self.dlg_modal.actions = [ft.Container(ft.ElevatedButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True, 
                                                                 width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor), width=150, alignment=ft.alignment.center)]
        self.page.open(self.dlg_modal)
        self.update()