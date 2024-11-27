
import os
import re
import time
import sqlite3
import flet as ft
import pandas as pd
from utils import extras
from pages.receipt import Receipt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Fees(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.page = page
        self.expand = True
        self.session_value = session_value
        self.sort_ascending_days = False
        self.sort_ascending_name = True
        self.divider = ft.Divider(height=1, thickness=3, color=extras.divider_color)
        self.dlg_modal = ft.AlertDialog(modal=True, actions_alignment=ft.MainAxisAlignment.END, surface_tint_color="#44CCCCCC")

# due tab's element
        self.due_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Sr. No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Days", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color), on_sort=self.days_sort_handler),
                ft.DataColumn(ft.Text("Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color), on_sort=self.name_sort_handler),
                ft.DataColumn(ft.Text("Father Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Contact", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Payed Till", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Due Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.due_list_view = ft.ListView([self.due_data_table], expand=True)
        self.due_list_view_container = ft.Container(self.due_list_view, margin=10, expand=True, border=ft.border.all(2, "grey"), border_radius=10)

# pay tab's element
        self.search_tf = ft.TextField(hint_text="Search by Anything.", capitalization=ft.TextCapitalization.WORDS, width=730, bgcolor="#44CCCCCC", on_submit=self.fetch_search_data_table_rows, on_focus=self.focus_search_tf, on_blur=self.blur_search_tf)
        self.search_btn = ft.ElevatedButton("Search", on_click=self.fetch_search_data_table_rows, width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor)
        self.search_container = ft.Container(ft.Row([self.search_tf, self.search_btn], alignment=ft.MainAxisAlignment.CENTER), margin=10)

        self.search_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Sr. No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Days", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color), on_sort=self.days_sort_handler),
                ft.DataColumn(ft.Text("Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color), on_sort=self.name_sort_handler),
                ft.DataColumn(ft.Text("Father Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Contact", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Payed Till", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Due Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.search_list_view = ft.ListView([self.search_data_table], expand=True)
        self.search_list_view_container = ft.Container(self.search_list_view, margin=10, visible=False, expand=True, border=ft.border.all(2, "grey"), border_radius=10)

# Reciept tab's content
        self.reciept_container = ft.Container(expand=True, padding=ft.Padding(top=15, bottom=0, left=0, right=0))

# main tab property, which contains all tabs
        self.tabs = ft.Tabs(
                    animation_duration=300,
                    on_change=self.on_tab_change,
                    tab_alignment=ft.TabAlignment.START_OFFSET,
                    expand=True,
                    selected_index=0,
                    tabs=[
                        ft.Tab(
                            text="Due(s)",
                            content=ft.Column(controls=[self.due_list_view_container])
                        ),
                        ft.Tab(
                            text="Search",
                            content=ft.Container(ft.Column([self.search_container, self.search_list_view_container], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
                        ),
                        ft.Tab(
                            text="Receipt",
                            content=self.reciept_container
                        ),
                    ],
                )
        
        self.fetch_due_data_table_rows()
# main tab added to page
        self.controls = [self.tabs]

# triggered when tabs is changed
    def on_tab_change(self, e):
        if e.control.selected_index == 0:
            self.excel_list = []
            self.reciept_container.content = None
            self.fetch_due_data_table_rows()

        elif e.control.selected_index == 1:
            self.excel_list = []
            self.reciept_container.content = None
            self.search_tf.value = ""
            self.search_data_table.rows.clear()
            self.search_list_view_container.visible = False
            self.update()

        elif e.control.selected_index == 2:
            self.excel_list = []

# it works, when search textfield is in focus
    def focus_search_tf(self, e):
        self.search_tf.hint_text = ""
        self.search_tf.label = "Name / Father Name / Contact / Aadhar / Address / Gender / Shift / Timing / Seat / Fees / Joining / Enrollment no."
        self.search_tf.label_style = ft.TextStyle(weight=ft.FontWeight.BOLD)
        self.update()
    
# it works, when search textfield is not in focus
    def blur_search_tf(self, e):
        self.search_tf.hint_text = "Search by Anything."
        self.search_tf.label = ""
        self.update()

# used to sort the data table's rows in behalf of days
    def days_sort_handler(self, e: ft.DataColumnSortEvent):
        try:
            self.sort_ascending_days = not self.sort_ascending_days
            self.sort_ascending_name = not self.sort_ascending_name
            if self.tabs.selected_index == 0:
                sorted_data = sorted(self.due_data, key=lambda row: -(datetime.now() - datetime.strptime(row[-2], "%d-%m-%Y")).days, reverse=not self.sort_ascending_days)
                self.update_due_data_table_rows(sorted_data)

            elif self.tabs.selected_index == 1:
                sorted_data = sorted(self.search_data, key=lambda row: -(datetime.now() - datetime.strptime(row[-2], "%d-%m-%Y")).days, reverse=not self.sort_ascending_days)
                self.update_search_data_table_rows(sorted_data)

        except AttributeError:
            self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Database not found.")
            self.page.open(self.dlg_modal)
        except Exception as e:
                self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)
        finally:
            self.update()
            
# used to sort the data table's rows in behalf of name
    def name_sort_handler(self, e: ft.DataColumnSortEvent):
        try:
            self.sort_ascending_days = not self.sort_ascending_days
            self.sort_ascending_name = not self.sort_ascending_name
            if self.tabs.selected_index == 0:
                sorted_data = sorted(self.due_data, key=lambda row: row[1], reverse=not self.sort_ascending_name)
                self.update_due_data_table_rows(sorted_data)

            elif self.tabs.selected_index == 1:
                sorted_data = sorted(self.search_data, key=lambda row: row[1], reverse=not self.sort_ascending_name)
                self.update_search_data_table_rows(sorted_data)

        except AttributeError:
            self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Database not found.")
            self.page.open(self.dlg_modal)
        except Exception as e:
                self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)
        finally:    
            self.update()

# used to update the due_data_table with sorted data
    def update_due_data_table_rows(self, data):
        self.due_data_table.rows.clear()
        if data:
            index = 1
            for row in data:
                given_date = datetime.strptime(row[13], "%d-%m-%Y")
                difference = -(datetime.now() - given_date).days

                if difference < 0:
                    due_fees = int(-difference * (int(row[10])/30))
                else:
                    due_fees = 0

                if difference <= 0:
                    cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in [index, difference, row[1], row[2], row[3], row[10], row[13], due_fees]]
                    action_cell = ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, icon_color=ft.colors.LIGHT_BLUE_ACCENT_700, on_click=lambda e, row=row: self.current_view_popup(row)),
                        ft.ElevatedButton(text="Pay Fees", color=ft.colors.GREEN_400, bgcolor=extras.secondary_eb_bgcolor, on_click=lambda e, row=row: self.pay_fees_popup(row)),
                        ft.ElevatedButton(text="Fees Slip", color=ft.colors.DEEP_ORANGE_400, bgcolor=extras.secondary_eb_bgcolor, on_click=lambda e, row=row: self.fees_slip_clicked(row)),
                    ]))
                    cells.append(action_cell)
                    self.due_data_table.rows.append(ft.DataRow(cells=cells))
                    index += 1
        self.update()

# fetch the due fees user's data from database and shown inside due tab data table
    def fetch_due_data_table_rows(self):
        self.due_data_table.rows.clear()
        try: 
            con = sqlite3.connect(f"{self.session_value[1]}.db")
            cur = con.cursor()
            cur.execute(f"select * from users_{self.session_value[1]}")
            res = cur.fetchall()

            self.due_data = []
            self.excel_list = []
            for row in res:
                self.due_data.append(list(row))

            if self.due_data:
                index = 1
                for row in self.due_data:
                    given_date = datetime.strptime(row[13], "%d-%m-%Y")
                    difference = -(datetime.now() - given_date).days

                    if difference < 0:
                        due_fees = int(-difference * (int(row[10])/30))
                    else:
                        due_fees = 0

                    if difference <= 0:
                        self.excel_list.append([index, difference, row[1], row[2], row[3], row[6], row[10], row[12], row[13], due_fees])
                        cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in [index, difference, row[1], row[2], row[3], row[10], row[13], due_fees]]
                        action_cell = ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, icon_color=ft.colors.LIGHT_BLUE_ACCENT_700, on_click=lambda e, row=row: self.current_view_popup(row)),
                            ft.ElevatedButton(text="Pay Fees", color=ft.colors.GREEN_400, bgcolor=extras.secondary_eb_bgcolor, on_click=lambda e, row=row: self.pay_fees_popup(row)),
                            ft.ElevatedButton(text="Fees Slip", color=ft.colors.DEEP_ORANGE_400, bgcolor=extras.secondary_eb_bgcolor, on_click=lambda e, row=row: self.fees_slip_clicked(row)),
                        ]))
                        cells.append(action_cell)
                        self.due_data_table.rows.append(ft.DataRow(cells=cells))
                        index += 1
        except sqlite3.OperationalError:
            self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Database not found.")
            self.page.open(self.dlg_modal)
        except Exception as e:
            self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)
        finally:
            con.close()
            self.update()

# used to update the due_dat_table with sorted data
    def update_search_data_table_rows(self, data):
        self.search_data_table.rows.clear()
        if data:
            index = 1
            for row in data:
                given_date = datetime.strptime(row[13], "%d-%m-%Y")
                difference = -(datetime.now() - given_date).days

                if difference < 0:
                    due_fees = int(-difference * (int(row[10])/30))
                else:
                    due_fees = 0


                cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in [index, difference, row[1], row[2], row[3], row[10], row[13], due_fees]]
                action_cell = ft.DataCell(ft.Row([
                    ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, icon_color=ft.colors.LIGHT_BLUE_ACCENT_700, on_click=lambda e, row=row: self.current_view_popup(row)),
                    ft.ElevatedButton(text="Pay Fees", color=ft.colors.GREEN_400, bgcolor=extras.secondary_eb_bgcolor, on_click=lambda e, row=row: self.pay_fees_popup(row)),
                    ft.ElevatedButton(text="Fees Slip", color=ft.colors.DEEP_ORANGE_400, bgcolor=extras.secondary_eb_bgcolor, on_click=lambda e, row=row: self.fees_slip_clicked(row)),
                ]))
                cells.append(action_cell)
                self.search_data_table.rows.append(ft.DataRow(cells=cells))
                index += 1
        self.update()

# fetch searched data from server and shown it in search tab's data table
    def fetch_search_data_table_rows(self, e):
        self.search_data_table.rows.clear()
        self.search_list_view_container.visible = True
        try:
            con = sqlite3.connect(f"{self.session_value[1]}.db")
            cur = con.cursor()
            sql = f"select * from users_{self.session_value[1]} where name=? or father_name=? or contact=? or aadhar=? or address=? or gender=? or shift=? or timing=? or seat=? or fees=? or joining=? or enrollment=? or payed_till=?"
            value = (self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip())
            cur.execute(sql, value)
            res = cur.fetchall()

            self.search_data = []
            self.excel_list = []
            for row in res:
                self.search_data.append(list(row))

            if self.search_data:
                index = 1
                for row in self.search_data:
                    given_date = datetime.strptime(row[13], "%d-%m-%Y")
                    difference = -(datetime.now() - given_date).days

                    if difference < 0:
                        due_fees = int(-difference * (int(row[10])/30))
                    else:
                        due_fees = 0

                    self.excel_list.append([index, difference, row[1], row[2], row[3], row[6], row[10], row[12], row[13], due_fees])
                    cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in [index, difference, row[1], row[2], row[3], row[10], row[13], due_fees]]
                    action_cell = ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, icon_color=ft.colors.LIGHT_BLUE_ACCENT_700, on_click=lambda e, row=row: self.current_view_popup(row)),
                        ft.ElevatedButton(text="Pay Fees", color=ft.colors.GREEN_400, bgcolor=extras.secondary_eb_bgcolor, on_click=lambda e, row=row: self.pay_fees_popup(row)),
                        ft.ElevatedButton(text="Fees Slip", color=ft.colors.DEEP_ORANGE_400, bgcolor=extras.secondary_eb_bgcolor, on_click=lambda e, row=row: self.fees_slip_clicked(row)),
                    ]))
                    cells.append(action_cell)
                    self.search_data_table.rows.append(ft.DataRow(cells=cells))
                    index += 1
        except sqlite3.OperationalError:
            self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Database not found.")
            self.page.open(self.dlg_modal)
        except Exception as e:
            self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)
        finally:
            con.close()
            self.update()

# show all total detail of users using alert dialogue box from user_(contact) table of database
    def current_view_popup(self, row):
        img = ft.Image(src=os.getcwd()+row[14], height=200, width=250)
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

# used to pay the fees of user and save it to fees table of database.
    def pay_fees_popup(self, row):
        # triggered when amount field value got changed
        def on_change_amount_field(e):
            try:
                if amount_field.value:
                    per_day_fees = int(row[10])/30
                    no_of_days = round(int(amount_field.value)/per_day_fees)
                    previous_date = datetime.strptime(fees_from_field.value, "%d-%m-%Y")
                    next_date = (previous_date + timedelta(days=no_of_days)).strftime("%d-%m-%Y")
                    if no_of_days >= 0:
                        fees_to_field.value = next_date
                        fees_to_field.update()
            except Exception:
                pass

        # triggered when Fees To field value got changed
        def on_change_fees_to_field(e):
            try:
                if re.match(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$', fees_to_field.value):
                    next_date = datetime.strptime(fees_to_field.value, "%d-%m-%Y")
                    previous_date = datetime.strptime(fees_from_field.value, "%d-%m-%Y")
                    difference = (next_date - previous_date).days
                    if difference >= 0:
                        due_fees = int(difference * (int(row[10])/30))
                        amount_field.value = due_fees
                        amount_field.update()
            except Exception:
                pass

        # triggered when Fees Pay button is clicked. it save the fees in fees table and update the payed_till in users table of database
        def pay_button_clicked(e):
            try:
                if re.match(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$', fees_to_field.value):
                    next_date = datetime.strptime(fees_to_field.value, "%d-%m-%Y")
                    previous_date = datetime.strptime(fees_from_field.value, "%d-%m-%Y")
                    difference = (next_date - previous_date).days
                    if difference > 0:
                        try:
                            con = sqlite3.connect(f"{self.session_value[1]}.db")
                            cur = con.cursor()

                            pay_date = datetime.today().strftime('%d-%m-%Y')

                            users_sql = f"update users_{self.session_value[1]} set payed_till=? where enrollment=?"
                            users_value = (fees_to_field.value, row[12])
                            cur.execute(users_sql, users_value)
                            
                            history_sql = f"insert into history_fees_users_{self.session_value[1]} (date, name, father_name, contact, gender, enrollment, amount, payed_from, payed_till) values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                            histroy_value = (pay_date, row[1], row[2], row[3], row[6], row[12], amount_field.value, fees_from_field.value, fees_to_field.value)
                            cur.execute(history_sql, histroy_value)

                            self.page.close(self.dlg_modal)
                            self.update()
                            con.commit()

                            cur.execute(f"select * from history_fees_users_{self.session_value[1]} order by slip_num desc limit 1")
                            slip_num = cur.fetchone()[0]
                            duration = f"{fees_from_field.value}  To  {fees_to_field.value}"

                            # Get the current date
                            now = datetime.now()
                            # Format the date as yyyy/month_name/dd-mm-yyyy
                            formatted_date = now.strftime("%Y/%B/%d-%m-%Y")
                            folder_path = os.path.join(os.environ['USERPROFILE'], "Downloads", "modal", "receipt", formatted_date)
                            os.makedirs(folder_path, exist_ok=True)
                            file_name = f"{folder_path}/{slip_num}_{row[1]}_{row[2]}.pdf"

                            Receipt(file_name, self.session_value, pay_date, str(slip_num), row[1], row[2], str(row[3]), row[7], row[8], row[9], row[5], duration, str(amount_field.value), os.getcwd()+row[14])
                            try:
                                os.startfile(file_name)
                            except Exception:
                                None
                            
                            if self.tabs.selected_index == 0:
                                self.fetch_due_data_table_rows()
                            
                            elif self.tabs.selected_index == 1:
                                self.search_tf.value = ""
                                self.search_data_table.rows.clear()
                                self.search_list_view_container.visible = False
                            
                        except Exception as e:
                            print(e)
                        finally:
                            con.close()
                            self.update()
            except Exception as e:
                print(e)

        fees_from = row[13]
        fees_to = (datetime.strptime(fees_from, "%d-%m-%Y") + relativedelta(months=1)).strftime("%d-%m-%Y")

        img = ft.Image(src=os.getcwd()+row[14], height=200, width=250)
        name_field = ft.TextField(label="Name", value=row[1], read_only=True, label_style=extras.label_style)
        father_name_field = ft.TextField(label="Father Name", value=row[2], read_only=True, label_style=extras.label_style)
        contact_field = ft.TextField(label="Contact", value=row[3], width=200, read_only=True, label_style=extras.label_style)
        amount_field = ft.TextField(label="Amount", value=row[10], width=200, autofocus=True, input_filter=ft.InputFilter(regex_string=r"[0-9]"), prefix=ft.Text("Rs. "), label_style=extras.label_style, text_style=ft.TextStyle(color=ft.colors.ORANGE_ACCENT_400, weight=ft.FontWeight.BOLD), on_change=on_change_amount_field)
        fees_from_field = ft.TextField(label="From", value=row[13], width=200, read_only=True, label_style=extras.label_style)
        fees_to_field = ft.TextField(label="To  (dd-mm-yyyy)", value=fees_to, width=200, label_style=extras.label_style, on_change=on_change_fees_to_field)

        contact_fees_row = ft.Row([contact_field, amount_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        fees_from_to_row = ft.Row([fees_from_field, fees_to_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        img_container = ft.Container(content=ft.Column(controls=[img], horizontal_alignment=ft.CrossAxisAlignment.CENTER), width=300)
        main_container = ft.Container(content=ft.Column(controls=[img_container, self.divider, name_field, father_name_field, contact_fees_row, fees_from_to_row], spacing=17, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                      width=450, height=480, padding=10)

        self.dlg_modal.content = main_container
        self.dlg_modal.title = ft.Text("Pay Fees", weight=ft.FontWeight.BOLD, color=ft.colors.LIGHT_BLUE_ACCENT_700, size=19)
        self.dlg_modal.actions = [ft.ElevatedButton("Pay", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=pay_button_clicked),
                                  ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.dlg_modal))]
        self.page.open(self.dlg_modal)
        self.update()

# used to see fees receipt of student
    def fees_slip_clicked(self, row):
        self.tabs.selected_index = 2

        img = ft.Image(src=os.getcwd()+row[14], height=150, width=200)
        name_field = ft.TextField(label="Name", value=row[1], width=300, read_only=True, label_style=extras.label_style)
        father_name_field = ft.TextField(label="Father Name", value=row[2], width=300, read_only=True, label_style=extras.label_style)
        contact_field = ft.TextField(label="Contact", value=row[3], width=300, read_only=True, label_style=extras.label_style)
        aadhar_field = ft.TextField(label="Aadhar", value=row[4], width=300, read_only=True, label_style=extras.label_style)
        total_amount_field = ft.TextField(label="Total Amount", color=ft.colors.GREEN_400, text_style=ft.TextStyle(weight=ft.FontWeight.BOLD) , width=300, read_only=True, label_style=extras.label_style)
        gender_field = ft.TextField(label="Gender", value=row[6], width=300, read_only=True, label_style=extras.label_style)


        name_father_name_contact_row = ft.Row([name_field, father_name_field, contact_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        aadhar_address_gender_row = ft.Row([aadhar_field, total_amount_field, gender_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        container_1 = ft.Container(content=ft.Column(controls=[img], horizontal_alignment=ft.CrossAxisAlignment.CENTER), width=350)
        container_2 = ft.Container(content=ft.Column(controls=[name_father_name_contact_row, aadhar_address_gender_row], spacing=30, horizontal_alignment=ft.CrossAxisAlignment.CENTER ), padding=20, expand=True)

        fees_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("S. N.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Slip No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Date", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Amount", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Duration", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        fees_list_view = ft.ListView([fees_data_table], expand=True)
        fees_list_view_container = ft.Container(fees_list_view, margin=10, expand=True, border=ft.border.all(2, "grey"), border_radius=10)


        try:
            conn = sqlite3.connect(f"{self.session_value[1]}.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT sum(amount) FROM history_fees_users_{self.session_value[1]} where enrollment=? ORDER BY slip_num DESC", (row[12],))
            total_amount = cursor.fetchone()[0]
            total_amount_field.value = total_amount
            cursor.execute(f"SELECT * FROM history_fees_users_{self.session_value[1]} where enrollment=? ORDER BY slip_num DESC", (row[12],))
            history_fees_rows = cursor.fetchall()

            index = len(history_fees_rows)
            self.excel_list = []
            for history_fees_row in history_fees_rows:
                duration = f"{history_fees_row[8]}  To  {history_fees_row[9]}"
                custom_row = [index, history_fees_row[0], history_fees_row[1], history_fees_row[7], duration]
                cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in custom_row]
                action_cell = ft.DataCell(ft.Row([
                    ft.ElevatedButton(text="Download", color=ft.colors.DEEP_ORANGE_400, bgcolor=extras.secondary_eb_bgcolor, on_click=lambda _, history_fees_row=history_fees_row: self.receipt_download(row, history_fees_row)),
                ]))
                cells.append(action_cell)
                fees_data_table.rows.append(ft.DataRow(cells=cells))
                self.excel_list.append([index, history_fees_row[0], history_fees_row[1], history_fees_row[2], history_fees_row[3], history_fees_row[4], history_fees_row[5], history_fees_row[6], history_fees_row[7], duration])
                index -= 1

        except sqlite3.OperationalError:
            self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Database not found.")
            self.page.open(self.dlg_modal)
        except Exception as e:
            self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)
        finally:
            conn.close()


        self.reciept_container.content = ft.Column(controls=[ft.Container(ft.Row([container_1, container_2])), self.divider, fees_list_view_container])
        self.update()

# data table to excel export, first fetch data from server, convert it do pandas data frame and return data frame.
    def get_export_data(self):
        if self.tabs.selected_index == 0 or self.tabs.selected_index == 1:
            header = ["Sr.No.", "Days", "Name", "Father_name", "Contact", "Gender", "Fees", "Enrollment", "Payed_till", "Due_fees"]
        elif self.tabs.selected_index == 2:
            header = ["Sr.No.", "slip_num", "date", "name", "father_name", "contact", "gender", "enrollment", "amount", "duration"]
            
        df = pd.DataFrame(self.excel_list, columns=header)
        return df
    
# used to download fees receipt of stuent
    def receipt_download(self, row, history_fees_row):
        def save_file(filename):
            if filename:
                try:
                    os.makedirs(os.path.join(os.environ['USERPROFILE'], "Downloads"), exist_ok=True)
                    file_name = os.path.join(os.getenv('userprofile'), "Downloads", f"{filename}.pdf")
                    duration = f"{history_fees_row[8]}  To  {history_fees_row[9]}"
                    Receipt(file_name, self.session_value, history_fees_row[1], str(history_fees_row[0]), row[1], row[2], str(row[3]), row[7], row[8], row[9], row[5], duration, str(history_fees_row[7]), os.getcwd()+row[14])
                    self.page.close(dlg_modal)
                    try:
                        os.startfile(file_name)
                    except Exception:
                        None

                except Exception:
                    pass
                

        alert_text = ft.Text("File will saved in Downloads folder.", weight=ft.FontWeight.W_500, size=16)
        filename_field = ft.TextField(label="File Name", autofocus=True, on_submit=lambda _: save_file(filename_field.value), suffix_text=".pdf")

        dlg_modal = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Old Receipt Download", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400),
                    content=ft.Container(content=ft.Column([alert_text, filename_field], spacing=20), width=400, height=100),
                    actions=[
                        ft.ElevatedButton("Download", on_click= lambda _: save_file(filename_field.value), color=ft.colors.GREEN_400),
                        ft.TextButton("Cancel", on_click= lambda _: self.page.close(dlg_modal)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700
                )
        self.page.open(dlg_modal)