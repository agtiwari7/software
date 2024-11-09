import os
import json
import sqlite3
import flet as ft
import mysql.connector
from utils import extras
from datetime import datetime
from utils import extras, cred
import mysql.connector.locales.eng

class Config(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page
        self.expand = True

# config tab elements
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
        
        self.bottom_container_column_1 = ft.Column([self.timing_container, self.total_seat_txt], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        self.bottom_container_column_2 = ft.Column([self.fees_container, self.bottom_reciept_position_txt], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        
# registration tab elements
        self.title = ft.Row(controls=[ft.Text("Registration", size=30, weight=ft.FontWeight.BOLD)],alignment=ft.MainAxisAlignment.CENTER)
        self.divider = ft.Divider(height=1, thickness=2, color=extras.divider_color)
        # dialogue box method
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)

        # all types of text field, which takes different types of data with different parameter.
        self.name_field = ft.TextField(label="Name", max_length=25, prefix_icon=ft.icons.VERIFIED_USER_OUTLINED, on_submit=lambda e: self.address_field.focus(), capitalization=ft.TextCapitalization.WORDS)
        self.address_field = ft.TextField(label="Address", max_length=30, prefix_icon=ft.icons.VERIFIED_USER_OUTLINED, on_submit=lambda e: self.contact_field.focus(), capitalization=ft.TextCapitalization.WORDS)
        self.contact_field = ft.TextField(label="Contact (Not Changed)", prefix_text="+91 ", max_length=10, prefix_icon=ft.icons.CONTACT_PAGE,input_filter=ft.InputFilter(regex_string=r"[0-9]"), on_submit=lambda e: self.password_field.focus(), read_only=True)
        self.password_field = ft.TextField(label="Password",password=True, can_reveal_password=True, max_length=12, prefix_icon=ft.icons.PASSWORD)
        self.update_btn = ft.ElevatedButton(text="Update", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.registration_update_btn_clicked)

        # create a container, which contains a column, and column contains "name_field, contact_field, password_field".
        self.container_1 = ft.Container(content=ft.Column(controls=[self.name_field, self.address_field, self.contact_field, self.password_field]), padding=10)
        self.container_2 = ft.Container(content=ft.Row(controls=[self.update_btn],alignment=ft.MainAxisAlignment.CENTER))
        # main container, which contains all properties and other containers also.
        self.registration_main_container = ft.Container(content=
                                           ft.Column(controls=
                                                     [self.title, self.divider, self.container_1, self.container_2]),
                                                     padding=extras.main_container_padding, border_radius=extras.main_container_border_radius, bgcolor=extras.main_container_bgcolor, border=extras.main_container_border, width=460)

# Main tab property, which contains all tabs
        self.tabs = ft.Tabs(
            animation_duration=300,
            on_change=self.on_tab_change,
            tab_alignment=ft.TabAlignment.START_OFFSET,
            expand=True,
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Config",
                    content=ft.Column(controls=[self.top_container, ft.Row([self.bottom_container_column_1, self.bottom_container_column_2], expand=True, alignment=ft.MainAxisAlignment.SPACE_AROUND)])
                ),
                ft.Tab(
                    text="Registration",
                    content=ft.Column(controls=[self.registration_main_container], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ),
            ],
        )

        self.fetch_config_data()

# Main tab added to page
        self.controls = [self.tabs]

# triggered when tabs is changed
    def on_tab_change(self, e):
        if e.control.selected_index == 0:
            self.fetch_config_data()

        elif e.control.selected_index == 1:
            self.fetch_registration_details()
        
# fetch data from json and update the UI
    def fetch_config_data(self):
        self.start_tf.value = ""
        self.start_dd.value = None
        self.end_tf.value = ""
        self.end_dd.value = None
        self.fees_tf.value = ""
        self.seat_tf.value = ""

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
        
        self.fetch_config_data()

# used to remove the existing fees value from json  
    def fees_delete_clicked(self, fees):
        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)

        fees_options = config["fees"]
        fees_options.remove(fees)

        config["fees"] = fees_options
        with open(f'{self.session_value[1]}.json', "w") as json_file:
            json.dump(config, json_file, indent=4)
        
        self.fetch_config_data()

# used to change the position of fee reciept
    def reciept_position_update_clicked(self, e):
        if not self.reciept_position_radio.value:
            return
        
        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)
        
        config["receipt_position"] = self.reciept_position_radio.value.capitalize()

        with open(f'{self.session_value[1]}.json', "w") as json_file:
            json.dump(config, json_file, indent=4)
        
        self.fetch_config_data()

# used to update the total number seats
    def seat_update_clicked(self, e):
        if not self.seat_tf.value:
            return
        
        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)
        
        config["seats"] = [f'S{i+1}' for i in range(int(self.seat_tf.value))]
    
        with open(f'{self.session_value[1]}.json', "w") as json_file:
            json.dump(config, json_file, indent=4)
                
        self.fetch_config_data()

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
        
        self.fetch_config_data()

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
            self.fetch_config_data()

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
        
        self.fetch_config_data()

# fetching registration details from database
    def fetch_registration_details(self):
        self.name_field.value = self.session_value[0]
        self.address_field.value = self.session_value[4]
        self.contact_field.value = self.session_value[1]
        self.password_field.value = self.session_value[2]

        self.update()

# triggered, when registration update btn clicked.
    def registration_update_btn_clicked(self, e):
        if not all([self.name_field.value.strip(), self.address_field.value.strip(), self.contact_field.value, self.password_field.value.strip(), len(str(self.contact_field.value))>=10, len(self.password_field.value)>=5]):
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Provide all the details properly.")
            self.page.open(self.dlg_modal)
            self.update()
        else:
            name = self.name_field.value.strip()
            address = self.address_field.value.strip()
            contact = self.contact_field.value
            password = self.password_field.value.strip()

            try:
                self.mysql_server(name, contact, password, address)
            except Exception as e:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)

# used to save the updated details in server
    def mysql_server(self, name, contact, password, address):
        try:
            connection = mysql.connector.connect(
                host = cred.host,
                user = cred.user,
                password = cred.password,
                database = cred.database
            )
            cursor = connection.cursor()
            
            soft_reg_sql = "update soft_reg set bus_name=%s, bus_contact=%s, bus_password=aes_encrypt(%s, %s), bus_address=%s where bus_contact=%s"
            soft_reg_value = (name, contact, password, cred.encrypt_key, address, self.session_value[1])
            cursor.execute(soft_reg_sql, soft_reg_value)

            connection.commit()

            self.sqlite_server(name, contact, password, address)

            self.dlg_modal.title = extras.dlg_title_done
            self.dlg_modal.content = ft.Text("Registration details updated.\n Please Login Again.")
            self.page.open(self.dlg_modal)

        except Exception as e:
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Something went wrong.")
            self.page.open(self.dlg_modal)

        finally:
            cursor.close()
            connection.close()
            self.update()

# save registration details locally in sqlite server
    def sqlite_server(self, name, contact, password, address):
        try:
            path = os.path.join(os.getenv('LOCALAPPDATA'), "Programs", "modal", "config", "modal.db")

            con = sqlite3.connect(path)
            cur = con.cursor()

            soft_reg_sql = "update soft_reg set bus_name=?, bus_contact=?, bus_password=?, bus_address=? where bus_contact=?"
            soft_reg_value = (name, contact, password, address, self.session_value[1])
            cur.execute(soft_reg_sql, soft_reg_value)

            con.commit()
            con.close()
        
        except Exception as e:
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)
        
        finally:
            con.close()
