import os
import json
import flet as ft
from utils import extras
from datetime import datetime, timedelta

class Config(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page
        self.expand = True
        self.divider = ft.Divider(height=1, thickness=2, color=extras.divider_color)

        self.timing_txt = ft.Text("Timing :", size=16, weight=ft.FontWeight.W_400)
        self.start_tf = ft.TextField(label="Start", width=55, input_filter=ft.InputFilter(regex_string=r"[0-9]"), label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.start_dd = ft.Dropdown(label="AM/PM", width=55, options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.end_tf = ft.TextField(label="End", width=55, input_filter=ft.InputFilter(regex_string=r"[0-9]"), label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.end_dd = ft.Dropdown(label="AM/PM", width=55, options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.timing_container = ft.Container(content=ft.Row([self.start_tf, self.start_dd, self.end_tf, self.end_dd], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), width=250, height=48, border=ft.border.all(1, ft.colors.BLACK), border_radius=5, bgcolor=ft.colors.BLUE_GREY_900)
        self.timing_add_btn = ft.ElevatedButton("Add", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.timing_add_clicked)

        self.fees_txt = ft.Text("    Fees :", size=16, weight=ft.FontWeight.W_400)
        self.fees_tf = ft.TextField(label="Enter Fees", width=250, input_filter=ft.InputFilter(regex_string=r"[0-9]"), on_submit=self.fees_add_clicked)
        self.fees_add_btn = ft.ElevatedButton("Add", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.fees_add_clicked)

        self.reciept_position_txt = ft.Text("Reciept Position :", size=16, weight=ft.FontWeight.W_400)
        self.reciept_position_radio = ft.RadioGroup(content=ft.Row([
                                                    ft.Radio(value="Top", label="Top", label_position=ft.LabelPosition.LEFT, label_style=ft.TextStyle(size=18, weight="bold"), active_color=ft.colors.LIGHT_BLUE_ACCENT_700),
                                                    ft.Radio(value="Bottom", label="Bottom", label_position=ft.LabelPosition.LEFT, label_style=ft.TextStyle(size=18, weight="bold"), active_color=ft.colors.LIGHT_BLUE_ACCENT_700),
                                                    ]))
        self.reciept_position_update_btn = ft.ElevatedButton("Update", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.reciept_position_update_clicked)

        self.seat_txt = ft.Text("Total Seats :", size=16, weight=ft.FontWeight.W_400)
        self.seat_tf = ft.TextField(label="Enter Total Seat", width=200, input_filter=ft.InputFilter(regex_string=r"[0-9]"), on_submit=self.seat_update_clicked)
        self.seat_update_btn = ft.ElevatedButton("Update", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.seat_update_clicked)

        self.top_container_column_1 = ft.Column([ft.Row([self.timing_txt, self.timing_container, self.timing_add_btn], alignment=ft.MainAxisAlignment.SPACE_EVENLY, width=550),
                                           ft.Row([self.fees_txt, self.fees_tf, self.fees_add_btn], alignment=ft.MainAxisAlignment.SPACE_EVENLY, width=550)],
                                           spacing=25)
        
        self.top_container_column_2 = ft.Column([ft.Row([self.reciept_position_txt, self.reciept_position_radio, self.reciept_position_update_btn], alignment=ft.MainAxisAlignment.SPACE_EVENLY, width=550),
                                           ft.Row([self.seat_txt, self.seat_tf, self.seat_update_btn], alignment=ft.MainAxisAlignment.SPACE_EVENLY, width=550)],
                                           spacing=25)

        self.top_container = ft.Container(ft.Row([self.top_container_column_1, self.top_container_column_2], expand=True, alignment=ft.MainAxisAlignment.SPACE_AROUND),
                                          border=ft.Border(bottom=ft.BorderSide(1, ft.colors.GREY)),
                                          padding=ft.Padding(bottom=30, top=20, left=0, right=0))


        self.timing_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=50,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Shift", size=17, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Timing", size=17, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=17, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.timing_list_view = ft.ListView([self.timing_data_table], expand=True)
        self.timing_container = ft.Container(self.timing_list_view, margin=10, width=500, height=300, border=ft.border.all(2, "grey"), border_radius=10)
        self.total_seat_txt = ft.Text("    Total Seat : ", size=20, weight=ft.FontWeight.W_400)


        self.fees_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=50,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Fees", size=17, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=17, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.fees_list_view = ft.ListView([self.fees_data_table], expand=True)
        self.fees_container = ft.Container(self.fees_list_view, margin=10, width=300, height=300, border=ft.border.all(2, "grey"), border_radius=10)
        self.bottom_reciept_position_txt = ft.Text("    Reciept Position : ", size=20, weight=ft.FontWeight.W_400)
        
        self.bottom_container_column_1 = ft.Column([self.timing_container, self.total_seat_txt], spacing=40, alignment=ft.MainAxisAlignment.CENTER)
        self.bottom_container_column_2 = ft.Column([self.fees_container, self.bottom_reciept_position_txt], spacing=40, alignment=ft.MainAxisAlignment.CENTER)
        
        
        self.fetch_data()
        self.controls = [self.top_container, ft.Row([self.bottom_container_column_1, self.bottom_container_column_2], expand=True, alignment=ft.MainAxisAlignment.SPACE_AROUND)]

# fetch data from json and update the UI
    def fetch_data(self):
        if not os.path.exists(f'{self.session_value[1]}.json'):
            data = {
                "shifts": {},
                "fees": [],
                "receipt_position": "Top",
                "seats": []
            }
            with open(f'{self.session_value[1]}.json', "w") as json_file:
                json.dump(data, json_file, indent=4)

        
        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)

        fees_options = config["fees"]
        receipt_position = config["receipt_position"].capitalize()
        total_seats = len(config["seats"])
        shift_option = config["shifts"]

        if receipt_position == "Top":
            self.reciept_position_radio.value = "Top"
        elif receipt_position == "Bottom":
            self.reciept_position_radio.value = "Bottom"

        self.total_seat_txt.value = f"    Total Seat :   {total_seats}"
        self.bottom_reciept_position_txt.value = f"    Reciept Position :   {receipt_position}"



        self.timing_data_table.rows.clear()
        for shift in shift_option:
            for timing in shift_option[shift]:
                cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in [shift, timing]]
                action_cell = ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.icons.EDIT_ROUNDED, icon_color=ft.colors.GREEN_400, on_click=lambda e, timing=timing, shift=shift: self.timing_edit_clicked(shift, timing)),
                    ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=extras.icon_button_color, on_click=lambda e, timing=timing, shift=shift: self.timing_delete_clicked(shift, timing))
                ]))
                cells.append(action_cell)
                self.timing_data_table.rows.append(ft.DataRow(cells=cells))

        self.fees_data_table.rows.clear()
        for fees in fees_options:
            cells = [ft.DataCell(ft.Text(str(f"       {fees}"), size=16))]
            action_cell = ft.DataCell(ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=extras.icon_button_color, on_click=lambda _: self.fees_delete_clicked(fees)))
            cells.append(action_cell)
            self.fees_data_table.rows.append(ft.DataRow(cells=cells))

        self.update()

# used to add the fees in json file
    def fees_add_clicked(self, e):
        if not self.fees_tf.value:
            return
        
        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)

        fees_options = config["fees"]
        fees_options.append(self.fees_tf.value)

        config["fees"] = fees_options
        with open(f'{self.session_value[1]}.json', "w") as json_file:
            json.dump(config, json_file, indent=4)
        
        self.fees_tf.value = ""
        self.fetch_data()

# used to remove the existing fees value from json  
    def fees_delete_clicked(self, fees):
        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)

        fees_options = config["fees"]
        fees_options.remove(fees)

        config["fees"] = fees_options
        with open(f'{self.session_value[1]}.json', "w") as json_file:
            json.dump(config, json_file, indent=4)
        
        self.fetch_data()

# used to change the position of fee reciept
    def reciept_position_update_clicked(self, e):
        if not self.reciept_position_radio.value:
            return
        
        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)
        
        config["receipt_position"] = self.reciept_position_radio.value.capitalize()

        with open(f'{self.session_value[1]}.json', "w") as json_file:
            json.dump(config, json_file, indent=4)
        
        self.fetch_data()

# used to update the total number seats
    def seat_update_clicked(self, e):
        if not self.seat_tf.value:
            return
        
        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)
        
        config["seats"] = [f'S{i+1}' for i in range(int(self.seat_tf.value))]
    
        with open(f'{self.session_value[1]}.json', "w") as json_file:
            json.dump(config, json_file, indent=4)
        
        self.seat_tf.value = ""
        self.fetch_data()

# used to calculate the shift/time difference in hours based on timing
    def calculate_shift_duration(self, shift_time):
        start_time, end_time = shift_time.split(" - ")
        time_format = "%I:%M %p"
        start_dt = datetime.strptime(start_time, time_format)
        end_dt = datetime.strptime(end_time, time_format)
        if end_dt <= start_dt:
            end_dt = end_dt.replace(day=start_dt.day + 1)
        duration = (end_dt - start_dt).total_seconds() / 3600  # Convert seconds to hours
        return f"{int(duration)} Hrs"

# used to add the timing in json file
    def timing_add_clicked(self, e):
        if not all ([self.start_tf.value, self.start_dd.value, self.end_tf.value, self.end_dd.value]):
            return
        try:
            start_time = datetime.strptime(f"{self.start_tf.value} {self.start_dd.value}", "%I %p").strftime("%I:%M %p")
            end_time = datetime.strptime(f"{self.end_tf.value} {self.end_dd.value}", "%I %p").strftime("%I:%M %p")
        except Exception:
            return

        timing = f"{start_time} - {end_time}"
        shift = self.calculate_shift_duration(timing)

        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)

        if shift in config["shifts"].keys():
            if timing in config["shifts"][shift]:
                return
            config["shifts"][shift].append(timing)

        else:
            config["shifts"][shift] = [timing]

        with open(f'{self.session_value[1]}.json', "w") as json_file:
            json.dump(config, json_file, indent=4)
        
        self.start_tf.value = ""
        self.start_dd.value = None
        self.end_tf.value = ""
        self.end_dd.value = None

        self.fetch_data()

# used to edit the shift and timing in json file
    def timing_edit_clicked(self, shift, timing):

        def edited_timing_save(old_shift, old_timing, new_shift, new_timing):
            if not all([old_shift, old_timing, new_shift, new_timing]):
                return
            
            with open(f'{self.session_value[1]}.json', 'r') as config_file:
                config = json.load(config_file)

            old_timing_index = config["shifts"][old_shift].index(old_timing)
            config["shifts"][old_shift][old_timing_index] = new_timing

            config["shifts"][new_shift] = config["shifts"].pop(old_shift)

            with open(f'{self.session_value[1]}.json', "w") as json_file:
                json.dump(config, json_file, indent=4)
            
            self.page.close(dlg_modal)
            self.fetch_data()

        shift_tf = ft.TextField(label="Shift", value=shift, capitalization=ft.TextCapitalization.WORDS, label_style=extras.label_style)
        timing_tf = ft.TextField(label="Timing", value=timing, capitalization=ft.TextCapitalization.CHARACTERS, label_style=extras.label_style, max_length=19)
        dlg_container = ft.Container(ft.Column([
                                                ft.Divider(),
                                                shift_tf,
                                                timing_tf
                                                ], spacing=20),
                                    width=360, height=150, margin=ft.Margin(left=0, bottom=20, top=0, right=0))

        dlg_modal = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Shift - Timing Edit", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400),
                    content=dlg_container,
                    actions=[
                        ft.ElevatedButton("Save", color=ft.colors.GREEN_400, on_click=lambda _: edited_timing_save(shift, timing, shift_tf.value, timing_tf.value)),
                        ft.TextButton("Cancel", on_click= lambda _: self.page.close(dlg_modal)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700
                )
        self.page.open(dlg_modal)

# used to delete the timing in json file
    def timing_delete_clicked(self, shift, timing):
        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)
        
        config["shifts"][shift].remove(timing)

        if config["shifts"][shift] == []:
            config["shifts"].pop(shift)

        with open(f'{self.session_value[1]}.json', "w") as json_file:
            json.dump(config, json_file, indent=4)
        
        self.fetch_data()