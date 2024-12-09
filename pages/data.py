import os
import re
import sys
import json
import math
import shutil
import sqlite3
import tempfile
import flet as ft
import pandas as pd
from PIL import Image
from utils import extras
from pages.camera import CameraWindow
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication


class Data(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.page = page
        self.expand = True
        self.session_value = session_value

        self.sort_column = "id"
        self.sort_order = "desc"
        self.search_sort_order = "asc"

        self.sort_ascending_name = True

        self.divider = ft.Divider(height=1, thickness=3, color=extras.divider_color)
        self.dlg_modal = ft.AlertDialog(modal=True, actions_alignment=ft.MainAxisAlignment.END, surface_tint_color="#44CCCCCC")
        
# search tab's elements
        self.search_tf = ft.TextField(hint_text="Search by Anything.", capitalization=ft.TextCapitalization.WORDS, width=730, bgcolor="#44CCCCCC", on_submit=lambda _: self.fetch_search_data_table_rows(), on_focus=self.focus_search_tf, on_blur=self.blur_search_tf)
        self.search_btn = ft.ElevatedButton("Search", on_click=lambda _: self.fetch_search_data_table_rows(), width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor)
        self.search_container = ft.Container(ft.Row([self.search_tf, self.search_btn], alignment=ft.MainAxisAlignment.CENTER), margin=10)

        self.search_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            data_row_max_height=90,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Sr. No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Father Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Contact", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Gender", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Enrollment", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.search_list_view = ft.ListView([self.search_data_table], expand=True)
        self.search_list_view_container = ft.Container(self.search_list_view, margin=10, visible=False, expand=True, border=ft.border.all(2, "grey"), border_radius=10)

# current tab's elements
        self.current_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            data_row_max_height=90,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Sr. No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Father Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Contact", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Gender", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Enrollment", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.current_list_view = ft.ListView([self.current_data_table], expand=True)
        self.current_list_view_container = ft.Container(self.current_list_view, margin=10, expand=True, border=ft.border.all(2, "grey"), border_radius=10)
        self.current_pagination_row = ft.Row(height=35, alignment=ft.MainAxisAlignment.CENTER)

# inactive tab's elements
        self.inactive_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Sr. No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Inactive Days", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Father Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Contact", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Enrollment", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.inactive_list_view = ft.ListView([self.inactive_data_table], expand=True)
        self.inactive_list_view_container = ft.Container(self.inactive_list_view, margin=10, expand=True, border=ft.border.all(2, "grey"), border_radius=10)
        # self.inactive_pagination_row = ft.Row(height=35, alignment=ft.MainAxisAlignment.CENTER)

# deleted tab's elements
        self.deleted_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Sr. No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Father Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Contact", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Gender", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Leave Date", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.deleted_list_view = ft.ListView([self.deleted_data_table], expand=True)
        self.deleted_list_view_container = ft.Container(self.deleted_list_view, margin=10, expand=True, border=ft.border.all(2, "grey"), border_radius=10)
        self.deleted_pagination_row = ft.Row(height=35, alignment=ft.MainAxisAlignment.CENTER)

# main tab property, which contains all tabs
        self.tabs = ft.Tabs(
            animation_duration=300,
            on_change=self.on_tab_change,
            tab_alignment=ft.TabAlignment.START_OFFSET,
            expand=True,
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Search (Current)",
                    content=ft.Container(ft.Column([self.search_container, self.search_list_view_container], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
                ),
                ft.Tab(
                    text="Current",
                    content=ft.Column(controls=[self.current_list_view_container, self.current_pagination_row])
                ),
                ft.Tab(
                    text="Inactive",
                    content=ft.Column(controls=[self.inactive_list_view_container])
                ),
                ft.Tab(
                    text="Deleted",
                    content=ft.Column(controls=[self.deleted_list_view_container, self.deleted_pagination_row])
                ),
            ],
        )
        

# main tab added to page
        self.controls = [self.tabs]

# triggered when tabs is changed        
    def on_tab_change(self, e):
        if e.control.selected_index == 0:
            self.search_tf.value = ""
            self.search_data_table.rows.clear()
            self.search_list_view_container.visible = False
            self.update()

        elif e.control.selected_index == 1:
            self.page_number = 1
            self.rows_per_page = 30
            self.total_rows = self.get_total_rows(f"users_{self.session_value[1]}")
            self.total_pages = math.ceil(self.total_rows / self.rows_per_page)
            self.fetch_current_data_table_rows()
        
        elif e.control.selected_index == 2:
            self.fetch_inactive_data_table_rows()  

        elif e.control.selected_index == 3:
            self.page_number = 1
            self.rows_per_page = 30
            self.total_rows = self.get_total_rows(f"deleted_users_{self.session_value[1]}")
            self.total_pages = math.ceil(self.total_rows / self.rows_per_page)
            self.fetch_deleted_data_table_rows()
            
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

# fetch total no of rows of given table of database
    def get_total_rows(self, table_name):
        try:
            conn = sqlite3.connect(f"{self.session_value[1]}.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]
            return total_rows
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

# fetch perticular rows from given table of database
    def load_data(self, table_name):
        offset = (self.page_number - 1) * self.rows_per_page
        try:
            conn = sqlite3.connect(f"{self.session_value[1]}.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY {self.sort_column} {self.sort_order.upper()} LIMIT ? OFFSET ?", (self.rows_per_page, offset))
            rows = cursor.fetchall()
            return rows
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

# used to sort the data table's rows in behalf of name
    def sort_handler(self, e: ft.DataColumnSortEvent):
        None
        # try:
        #     self.sort_ascending_name = not self.sort_ascending_name
        #     if self.tabs.selected_index == 0:
        #         self.search_sort_order = "asc" if self.search_sort_order == "desc" else "desc"
        #         self.fetch_search_data_table_rows()

        #     elif self.tabs.selected_index == 1:
        #         self.sort_column = "name" if self.sort_column == "id" else "id"
        #         self.sort_order = "asc" if self.sort_order == "desc" else "desc"
        #         self.fetch_current_data_table_rows()

        #     elif self.tabs.selected_index == 2:
        #         self.sort_column = "name" if self.sort_column == "id" else "id"
        #         self.sort_order = "asc" if self.sort_order == "desc" else "desc"
        #         self.fetch_deleted_data_table_rows()

        # except AttributeError:
        #     self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
        #     self.dlg_modal.title = extras.dlg_title_error
        #     self.dlg_modal.content = ft.Text("Database not found.")
        #     self.page.open(self.dlg_modal)
        # except Exception as e:
        #         self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
        #         self.dlg_modal.title = extras.dlg_title_error
        #         self.dlg_modal.content = ft.Text(e)
        #         self.page.open(self.dlg_modal)
        # finally:    
        #     self.update()

# fetch searched data from server and shown it in search tab's data table
    def fetch_search_data_table_rows(self):
        self.search_data_table.rows.clear()
        self.search_list_view_container.visible = True
        try:
            con = sqlite3.connect(f"{self.session_value[1]}.db")
            cur = con.cursor()
            sql = f"select * from users_{self.session_value[1]} where name=? or father_name=? or contact=? or aadhar=? or address=? or gender=? or shift=? or timing=? or seat=? or fees=? or joining=? or enrollment=? or payed_till=? ORDER BY name {self.search_sort_order.upper()}"
            value = (self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip())
            cur.execute(sql, value)
            res = cur.fetchall()

            self.search_data = []
            for row in res:
                self.search_data.append(list(row))

            if self.search_data:
                for index, row in enumerate(self.search_data):
                    cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in [index+1, row[1], row[2], row[3], row[6], row[10], row[12]]]
                    action_cell = ft.DataCell(ft.Column([
                        ft.Row([ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, icon_color=ft.colors.LIGHT_BLUE_ACCENT_700, on_click=lambda e, row=row: self.current_view_popup(row)),
                                ft.IconButton(icon=ft.icons.EDIT_ROUNDED, icon_color=ft.colors.GREEN_400, on_click=lambda e, row=row: self.current_edit_popup(row))]),
                        ft.Row([ft.IconButton(icon=ft.icons.DISABLED_BY_DEFAULT_OUTLINED, icon_color=ft.colors.PURPLE_400, on_click=lambda e, row=row: self.current_inactive_popup(row)),
                                ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=extras.icon_button_color, on_click=lambda e, row=row: self.current_delete_popup(row))])
                        ]))
                    cells.append(action_cell)
                    self.search_data_table.rows.append(ft.DataRow(cells=cells))
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

# fetch all data from users_contact (current) table of database and shown it in current tab's data table
    def fetch_current_data_table_rows(self):
        self.current_data_table.rows.clear()
        rows = self.load_data(f"users_{self.session_value[1]}")
        for index, row in enumerate(rows):
            cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in [index+1, row[1], row[2], row[3], row[6], row[10], row[12]]]
            action_cell = ft.DataCell(ft.Column([
                ft.Row([ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, icon_color=ft.colors.LIGHT_BLUE_ACCENT_700, on_click=lambda e, row=row: self.current_view_popup(row)),
                        ft.IconButton(icon=ft.icons.EDIT_ROUNDED, icon_color=ft.colors.GREEN_400, on_click=lambda e, row=row: self.current_edit_popup(row))]),
                ft.Row([ft.IconButton(icon=ft.icons.DISABLED_BY_DEFAULT_OUTLINED, icon_color=ft.colors.PURPLE_400, on_click=lambda e, row=row: self.current_inactive_popup(row)),
                        ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=extras.icon_button_color, on_click=lambda e, row=row: self.current_delete_popup(row))])
                ]))
            cells.append(action_cell)
            self.current_data_table.rows.append(ft.DataRow(cells=cells))
        self.update_pagination_controls()
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
        payed_till_field = ft.TextField(label="Fees Payed Till", value=row[13], text_style=ft.TextStyle(color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD), width=225, read_only=True, label_style=extras.label_style)
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

# show all total detail (which can be editable) of users using alert dialogue box from user_(contact) table of database
    def current_edit_popup(self, row):
        
        # set image path is equal to choosen photo from file picker dialogue box.
        def on_file_picker_result(e):
            if e.files:
                selected_file = e.files[0]
                file_path = selected_file.path
                img.src = file_path
                img.update()

        # used to open the camera window for capute the image using camera
        def open_camera_window(e):
            app = QApplication(sys.argv)
            camera_window = CameraWindow()
            camera_window.show()
            app.exec()
            try:
                img.src = camera_window.captured_filename
            except Exception:
                img.src = row[14]
            finally:
                img.update()
        
        # add - after and each 4 digits of aadhar no.
        def format_aadhaar_number(e):
            text = e.control.value.replace("-", "")  # Remove existing hyphens
            if len(text) > 12:  # Limit the input to 12 digits
                text = text[:12]
            formatted_text = '-'.join([text[i:i+4] for i in range(0, len(text), 4)])
            e.control.value = formatted_text
            e.control.update()
        
        # save photo named as aadhar no, below 150kb and return the path of saved photo
        def save_photo(aadhar, input_image, target_size_kb=150, quality=85):
            # Create the folder hierarchy if it doesn't exist
            target_folder = os.path.join(os.getcwd(), "photo", "current")
            os.makedirs(target_folder, exist_ok=True)

            base_file_name = os.path.basename(input_image)
            _ , file_extension = os.path.splitext(base_file_name)
            file_name = f"{aadhar}{file_extension}"

            # Define the target file path and Copy the file to the target folder
            output_image = os.path.join(target_folder, file_name)

            # Image resizer and compressor process start from here #############################################
            target_size_bytes = target_size_kb * 1024           # Target size in bytes
            
            # Get the size of the input image
            original_size = os.path.getsize(input_image)
            
            # Image ko open karein
            with Image.open(input_image) as img:
                # Agar image PNG format me hai, to usko JPEG me convert karein
                if img.format == 'PNG':
                    img = img.convert('RGB')
                    output_image = output_image.rsplit('.', 1)[0] + ".jpg"

                # original image ka size 150kb ya usse kam hone pr direct save hogi
                if original_size <= target_size_bytes:
                    
                    img.save(output_image, "JPEG", quality=quality)
                    return output_image
                
                # Initial resize factor
                resize_factor = 1.0
                
                # Resize aur compress process ko repeat karein jab tak desired size achieve na ho
                while True:
                    # Current size ka estimation
                    estimated_size = os.path.getsize(input_image) * (resize_factor ** 2) * (quality / 100)
                    
                    # Agar estimated size target se chhota hai to break karein
                    if estimated_size <= target_size_bytes:
                        break
                    
                    # Resize factor ko kam karein (resize_factor < 1.0 means reduction in size)
                    resize_factor -= 0.1
                    new_size = (int(img.width * resize_factor), int(img.height * resize_factor))
                    
                    # Naye attribute LANCZOS ka use karein for resizing
                    resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Image ko compress karein aur save karein
                    resized_img.save(output_image, "JPEG", quality=quality)
                    
                    # Agar actual file size target se kam hai, to loop break karein
                    if os.path.getsize(output_image) <= target_size_bytes:
                        break

            for name in os.listdir(tempfile.gettempdir()):
                if "modal" in name and ".png" in name:
                    temp_file_name = os.path.join(tempfile.gettempdir(), name)
                    os.remove(temp_file_name)

            return output_image
        
        def shift_dd_change(e):
            for data in shift_options[shift_dd.value]:
                time_list = data.split(" - ")

                time1, period1 = time_list[0].split()
                hour1, minute1 = time1.split(':')

                time2, period2 = time_list[1].split()
                hour2, minute2 = time2.split(':')

                start_tf.value = int(hour1)
                start_dd.value = period1
                end_tf.value = int(hour2)
                end_dd.value = period2

                start_tf.update()
                start_dd.update()
                end_tf.update()
                end_dd.update()

        # used to save edited data into user_(contact) database.
        def save_edit_data(e):
            try:
                start_time = datetime.strptime(f"{start_tf.value} {start_dd.value}", "%I %p").strftime("%I:%M %p")
                end_time = datetime.strptime(f"{end_tf.value} {end_dd.value}", "%I %p").strftime("%I:%M %p")
                timing = f"{start_time} - {end_time}".strip()
            except Exception:
                timing = None

            if all([name_field.value, father_name_field.value, contact_field.value, aadhar_field.value, address_field.value, gender.value,
                    shift_dd.value, timing, seat_field.value, fees_field.value, joining_field.value, enrollment_field.value,
                    payed_till_field.value, len(str(contact_field.value))==10, len(str(aadhar_field.value))==14,
                    ]):
                try:
                    con = sqlite3.connect(f"{self.session_value[1]}.db")
                    cur = con.cursor()
                    cur.execute(f"select aadhar, enrollment from users_{self.session_value[1]}")
                    result = cur.fetchall()

                    integrity_error = False
                    for line in result:
                        if aadhar_field.value in line and enrollment_field.value not in line:
                            integrity_error = True

                    if integrity_error:
                        return

                    img_src = save_photo(aadhar_field.value, img.src).replace(os.getcwd(), "")
                    
                    sql = f"update users_{self.session_value[1]} set name=?, father_name=?, contact=?, aadhar=?, address=?, gender=?, shift=?, timing=?, seat=?, fees=?, joining=?, enrollment=?, payed_till=?, img_src=? where enrollment=?"
                    value = (name_field.value.strip(), father_name_field.value.strip(), contact_field.value, aadhar_field.value.strip(), address_field.value.strip(), gender.value.strip(), shift_dd.value.strip(), timing, seat_field.value.strip(), fees_field.value, joining_field.value.strip(), enrollment_field.value.strip(), payed_till_field.value.strip(), img_src, row[12])
                    cur.execute(sql, value)
                    con.commit()
                
                    if self.tabs.selected_index == 0:
                        self.search_tf.value = ""
                        self.search_data_table.rows.clear()
                        self.search_list_view_container.visible = False
                        
                    elif self.tabs.selected_index == 1:
                        self.fetch_current_data_table_rows()
                
                    self.page.close(self.dlg_modal)

                    # remove the old aadhar name's photo, if new aadhar is changed.
                    if aadhar_field.value != row[4]:
                        os.remove(row[14])       

                except Exception:
                    return
                finally:
                    con.close()
                    self.update()

        # adding file picker object in main page.
        file_picker = ft.FilePicker(on_result=on_file_picker_result)
        self.controls.append(file_picker)

        # main elements of current edit popup
        img = ft.Image(src=os.getcwd()+row[14], height=200, width=250)
        gallery_btn = ft.ElevatedButton("Gallery", color=extras.secondary_eb_color, bgcolor=extras.secondary_eb_bgcolor, on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "png", "jpeg"]))
        camera_btn = ft.ElevatedButton("Camera", color=extras.secondary_eb_color, bgcolor=extras.secondary_eb_bgcolor, on_click=open_camera_window)
    
        name_field = ft.TextField(label="Name", value=row[1], max_length=25, on_submit=lambda _:  father_name_field.focus(), capitalization=ft.TextCapitalization.WORDS, width=315, label_style=extras.label_style)
        father_name_field = ft.TextField(label="Father Name", value=row[2], prefix_text="Mr. ", max_length=25, on_submit=lambda _:  contact_field.focus(), capitalization=ft.TextCapitalization.WORDS, width=315, label_style=extras.label_style)
        contact_field = ft.TextField(label="Contact", value=row[3], prefix_text="+91 ", max_length=10, on_submit=lambda _:  aadhar_field.focus(), input_filter=ft.InputFilter(regex_string=r"[0-9]"), width=315, label_style=extras.label_style)
        aadhar_field = ft.TextField(label="Aadhar", value=row[4], max_length=14, on_submit=lambda _:  address_field.focus(), input_filter=ft.InputFilter(regex_string=r"[0-9]"), width=315, on_change=format_aadhaar_number, label_style=extras.label_style)
        address_field = ft.TextField(label="Address", value=row[5], max_length=30, capitalization=ft.TextCapitalization.WORDS, width=430, label_style=extras.label_style)
        gender = ft.RadioGroup(content=ft.Row([
                                                ft.Radio(value="Male", label="Male", label_position=ft.LabelPosition.LEFT, label_style=ft.TextStyle(size=18, weight="bold"), active_color=ft.colors.LIGHT_BLUE_ACCENT_700),
                                                ft.Radio(value="Female", label="Female", label_position=ft.LabelPosition.LEFT, label_style=ft.TextStyle(size=18, weight="bold"), active_color=ft.colors.LIGHT_BLUE_ACCENT_700),
                                                ]))
        if row[6] == "Male":
            gender.value = "Male"
        elif row[6] == "Female":
            gender.value = "Female"

        name_father_name_row = ft.Row([ name_field,  father_name_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        contact_aadhar_row = ft.Row([ contact_field,  aadhar_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        address_gender_row = ft.Row([ address_field,  gender], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)

        shift_options = config["shifts"]

        shift_dd = ft.Dropdown(
                    label="Shift",
                    value=row[7],
                    width=220,
                    options=[ft.dropdown.Option(shift) for shift in  shift_options],
                    label_style=extras.label_style,
                    on_change=shift_dd_change)
        
        time_list = row[8].split(" - ")

        time1, period1 = time_list[0].split()
        hour1, minute1 = time1.split(':')

        time2, period2 = time_list[1].split()
        hour2, minute2 = time2.split(':')

        start_tf = ft.TextField(label="Start", width=50, value=int(hour1), input_filter=ft.InputFilter(regex_string=r"[0-9]"), label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        start_dd = ft.Dropdown(label="AM/PM", width=50, value=period1, options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        end_tf = ft.TextField(label="End", width=50, value=int(hour2), input_filter=ft.InputFilter(regex_string=r"[0-9]"), label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        end_dd = ft.Dropdown(label="AM/PM", width=50, value=period2, options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        timing_container = ft.Container(content=ft.Row([start_tf, start_dd, end_tf, end_dd], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), width=220, height=50, border=ft.border.all(1, ft.colors.BLACK), border_radius=5)

        seat_field = ft.TextField(label="Seat", value=row[9], width=220, label_style=extras.label_style, capitalization=ft.TextCapitalization.WORDS)
        fees_field = ft.TextField(label="Fees", value=row[10], input_filter=ft.InputFilter(regex_string=r"[0-9]"), prefix=ft.Text("Rs. "), width=220, label_style=extras.label_style)
        
        joining_field = ft.TextField(label="Joining (dd-mm-yyyy)", value=row[11], read_only=True, width=220, label_style=extras.label_style)
        enrollment_field = ft.TextField(label="Enrollment No.", value=row[12], width=220, read_only=True, label_style=extras.label_style)
        payed_till_field = ft.TextField(label="Fees Payed Till", value=row[13], text_style=ft.TextStyle(color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD), width=220, read_only=True, label_style=extras.label_style)
        due_fees_field = ft.TextField(label="Due Fees", width=220, text_style=ft.TextStyle(color=ft.colors.ORANGE_ACCENT_400, weight=ft.FontWeight.BOLD), read_only=True, label_style=extras.label_style)
        
        payed_till_formatted_date = datetime.strptime(row[13], "%d-%m-%Y")
        difference = (datetime.now() - payed_till_formatted_date).days
        if difference > 0:
            due_fees = int(difference * (int(row[10])/30))
            due_fees_field.value = due_fees
        else:
            due_fees_field.value = 0

        shift_timing_seat_fees_dd_row = ft.Row(controls=[shift_dd, timing_container, seat_field, fees_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        joining_enrollment_payed_till_due_fees_row = ft.Row(controls=[joining_field, enrollment_field, payed_till_field, due_fees_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        container_1 = ft.Container(content=ft.Column(controls=[img, ft.Container(ft.Row(controls=[ gallery_btn,  camera_btn], alignment=ft.MainAxisAlignment.CENTER), margin=10)],width=300, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        container_2 = ft.Container(content=ft.Column(controls=[name_father_name_row, contact_aadhar_row, address_gender_row], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=10, expand=True)
        container_3 = ft.Container(content=ft.Column(controls=[shift_timing_seat_fees_dd_row, joining_enrollment_payed_till_due_fees_row], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=25), padding=10, expand=True)

        main_container = ft.Container(content=ft.Column(controls=[
                                                                    ft.Container(ft.Row([container_1, container_2])),
                                                                    self.divider,
                                                                    container_3,
                                                                    ], spacing=15
                                                            ),
                                                            width=1050, 
                                                            height=480,
                                                            padding=30,
                                                            border_radius=extras.main_container_border_radius, 
                                                            bgcolor=extras.main_container_bgcolor,
                                                            border=extras.main_container_border
                                            )
        
        self.dlg_modal.title = ft.Text("Edit Details", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400, size=19)
        self.dlg_modal.content = main_container

        submit_btn = ft.ElevatedButton("Save", color=extras.main_eb_color, width=extras.main_eb_width, bgcolor=ft.colors.GREEN_700, on_click=save_edit_data)
        close_btn = ft.TextButton("Close", on_click=lambda e: self.page.close(self.dlg_modal))

        self.dlg_modal.actions=[submit_btn, close_btn]
        self.dlg_modal.actions_alignment=ft.MainAxisAlignment.END

        self.page.open(self.dlg_modal)
        self.update()

# show all total detail of users using alert dialogue box from user_(contact) table of database
    def current_inactive_popup(self, row):
        def inactive_date_field_change(e):
            if re.match(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$', inactive_date_field.value):
                payed_till_formatted_date = datetime.strptime(row[13], "%d-%m-%Y")
                inactive_formatted_date = datetime.strptime(inactive_date_field.value, "%d-%m-%Y")
                difference = (payed_till_formatted_date - inactive_formatted_date).days
                if difference > 0:
                    remaining_days_field.value = difference
                else:
                    remaining_days_field.value = 0
                remaining_days_field.update()

        def inactive_btn_clicked(e):
            if all([inactive_date_field.value, int(remaining_days_field.value) >=0, re.match(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$', inactive_date_field.value)]):
                try:
                    conn = sqlite3.connect(f"{self.session_value[1]}.db")
                    cursor = conn.cursor()

                    result = list(row)
                    if result:
                        result.append(inactive_date_field.value)
                        result.append(remaining_days_field.value)

                        sql = f"INSERT INTO inactive_users_{self.session_value[1]} (id, name, father_name, contact, aadhar, address, gender, shift, timing, seat, fees, joining, enrollment, payed_till, img_src, inactive_date, remaining_days) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                        value = (result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10], result[11], result[12], result[13], result[14], result[15], result[16])
                        cursor.execute(sql, value)

                        cursor.execute(f"DELETE FROM users_{self.session_value[1]} WHERE id = ?", (result[0],))
                        conn.commit()

                    if self.tabs.selected_index == 0:
                        self.search_tf.value = ""
                        self.search_data_table.rows.clear()
                        self.search_list_view_container.visible = False
                        
                    elif self.tabs.selected_index == 1:
                        self.fetch_current_data_table_rows()
                
                    self.page.close(self.dlg_modal)

                except Exception:
                    conn.rollback()
                    return
                finally:
                    conn.close()
                    self.update()

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
        enrollment_field = ft.TextField(label="Enrollment No.", value=row[12], width=225, read_only=True, label_style=extras.label_style)
        payed_till_field = ft.TextField(label="Fees Payed Till", value=row[13], text_style=ft.TextStyle(color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD), width=225, read_only=True, label_style=extras.label_style)
        inactive_date_field = ft.TextField(label="Inactive Date  (dd-mm-yyyy)", value=datetime.today().strftime('%d-%m-%Y'), width=225, label_style=extras.label_style, on_change=inactive_date_field_change, autofocus=True)
        remaining_days_field = ft.TextField(label="Remaining Days", width=225, input_filter=ft.InputFilter(regex_string=r"[0-9]"), text_style=ft.TextStyle(color=ft.colors.ORANGE_ACCENT_400, weight=ft.FontWeight.BOLD), label_style=extras.label_style)
        
        payed_till_formatted_date = datetime.strptime(row[13], "%d-%m-%Y")
        inactive_formatted_date = datetime.strptime(inactive_date_field.value, "%d-%m-%Y")
        difference = (payed_till_formatted_date - inactive_formatted_date).days
        if difference > 0:
            remaining_days_field.value = difference
        else:
            remaining_days_field.value = 0

        name_father_name_row = ft.Row([name_field, father_name_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        contact_aadhar_row = ft.Row([contact_field, aadhar_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        address_gender_row = ft.Row([address_field, gender_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        shift_timing_seat_fees_row = ft.Row([shift_field, timing_field, seat_field, fees_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        joining_enrollment_payed_till_due_fees_row = ft.Row([enrollment_field, payed_till_field, inactive_date_field, remaining_days_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

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
        self.dlg_modal.title = ft.Text("Inactive Details", weight=ft.FontWeight.BOLD, color=ft.colors.PURPLE_400, size=19)
        self.dlg_modal.content = main_container

        submit_btn = ft.ElevatedButton("Inactive", color=extras.main_eb_color, width=extras.main_eb_width, bgcolor=ft.colors.PURPLE_400, on_click=inactive_btn_clicked)
        close_btn = ft.TextButton("Close", on_click=lambda e: self.page.close(self.dlg_modal))

        self.dlg_modal.actions=[submit_btn, close_btn]
        self.dlg_modal.actions_alignment=ft.MainAxisAlignment.END

        self.page.open(self.dlg_modal)
        self.update()

# used to delete the record of current user and save the copy of record in deleted_users table
    def current_delete_popup(self, row):
        def delete_clicked(e):
            delete_img_src = row[14].replace("current", "deleted")

            if len(str(reason_field.value)) >120:
                reason = reason_field.value[:121]
            else:
                reason = reason_field.value
            try:
                con = sqlite3.connect(f"{self.session_value[1]}.db")
                cur = con.cursor()

                if self.tabs.selected_index == 2:
                    sql_1 = f"INSERT INTO deleted_users_{self.session_value[1]} (name, father_name, contact, aadhar, address, gender, shift, timing, seat, fees, joining, enrollment, payed_till, img_src, due_fees, leave_date, reason) SELECT name, father_name, contact, aadhar, address, gender, shift, timing, seat, fees, joining, enrollment, payed_till, ?, ?, ?, ? FROM inactive_users_{self.session_value[1]} WHERE id = ?"
                    sql_2 = f"DELETE FROM inactive_users_{self.session_value[1]} WHERE id = ?"
                else:
                    sql_1 = f"INSERT INTO deleted_users_{self.session_value[1]} (name, father_name, contact, aadhar, address, gender, shift, timing, seat, fees, joining, enrollment, payed_till, img_src, due_fees, leave_date, reason) SELECT name, father_name, contact, aadhar, address, gender, shift, timing, seat, fees, joining, enrollment, payed_till, ?, ?, ?, ? FROM users_{self.session_value[1]} WHERE id = ?"
                    sql_2 = f"DELETE FROM users_{self.session_value[1]} WHERE id = ?"
                
                value_1 = (delete_img_src, due_fees_field.value, leave_date_field.value, reason, row[0])
                value_2 = (row[0],)
                
                cur.execute(sql_1, value_1)
                cur.execute(sql_2, value_2)

                history_sql = f"insert into history_deleted_users_{self.session_value[1]} (date, name, father_name, contact, gender, enrollment, due_fees) values (?, ?, ?, ?, ?, ?, ?)"
                histroy_value = (leave_date_field.value, row[1], row[2], row[3], row[6], row[12], due_fees_field.value)
                cur.execute(history_sql, histroy_value)

                con.commit()
            
                if self.tabs.selected_index == 0:
                    self.search_tf.value = ""
                    self.search_data_table.rows.clear()
                    self.search_list_view_container.visible = False
                    
                elif self.tabs.selected_index == 1:
                    self.fetch_current_data_table_rows()
                
                elif self.tabs.selected_index == 2:
                    self.fetch_inactive_data_table_rows()

                self.page.close(self.dlg_modal)

                try:
                    shutil.move(os.getcwd()+row[14], os.getcwd()+delete_img_src)
                except Exception:
                    pass
            
            except Exception:
                pass
            finally:
                con.close()
                self.update()

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
        payed_till_field = ft.TextField(label="Fees Payed Till", value=row[13], text_style=ft.TextStyle(color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD), width=225, read_only=True, label_style=extras.label_style)
        due_fees_field = ft.TextField(label="Due Fees", width=225, text_style=ft.TextStyle(color=ft.colors.ORANGE_ACCENT_400, weight=ft.FontWeight.BOLD) ,read_only=True, label_style=extras.label_style)
        leave_date_field = ft.TextField(label="Leave Date", width=225, value=datetime.today().strftime('%d-%m-%Y'), label_style=extras.label_style)
        reason_field = ft.TextField(label="Reason of leave", width=735, capitalization=ft.TextCapitalization.SENTENCES, autofocus=True, label_style=extras.label_style)

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
        leave_date_reason_row = ft.Row([leave_date_field, reason_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        container_1 = ft.Container(content=ft.Column(controls=[img], horizontal_alignment=ft.CrossAxisAlignment.CENTER), width=350)
        container_2 = ft.Container(content=ft.Column(controls=[name_father_name_row, contact_aadhar_row, address_gender_row], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER ), padding=20, expand=True)
        container_3 = ft.Container(content=ft.Column(controls=[shift_timing_seat_fees_row, joining_enrollment_payed_till_due_fees_row, leave_date_reason_row], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER ), expand=True, padding=20)

        main_container = ft.Container(content=ft.Column(controls=[
                                                                    ft.Container(ft.Row([container_1, container_2])),
                                                                    self.divider,
                                                                    container_3,
                                                                    ], spacing=15
                                                            ),
                                                            width=1050, 
                                                            height=480,
                                                            padding=10,
                                                            border_radius=extras.main_container_border_radius, 
                                                            bgcolor=extras.main_container_bgcolor,
                                                            border=extras.main_container_border
                                            )
        
        self.dlg_modal.title = ft.Text("Delete Student", weight=ft.FontWeight.BOLD, color=ft.colors.DEEP_ORANGE_400, size=19)
        self.dlg_modal.content = main_container
        delete_btn = ft.ElevatedButton("Delete", color=extras.main_eb_color, width=extras.main_eb_width, bgcolor=ft.colors.DEEP_ORANGE_700, on_click=delete_clicked)
        close_btn = ft.TextButton("Close", on_click=lambda e: self.page.close(self.dlg_modal))

        self.dlg_modal.actions=[delete_btn, close_btn]
        self.dlg_modal.actions_alignment=ft.MainAxisAlignment.END
        self.page.open(self.dlg_modal)
        self.update()

# fetch all data from inactive_users_contact (inactive) table of database and shown it in inactive tab's data table
    def fetch_inactive_data_table_rows(self):
        self.inactive_data_table.rows.clear()
        try:
            con = sqlite3.connect(f"{self.session_value[1]}.db")
            cur = con.cursor()
            cur.execute(f"select * from inactive_users_{self.session_value[1]} ORDER BY name {self.search_sort_order.upper()}")
            res = cur.fetchall()

            self.inactive_data = []
            for row in res:
                self.inactive_data.append(list(row))

            if self.inactive_data:
                for index, row in enumerate(self.inactive_data):
                    inactive_days = (datetime.now() - datetime.strptime(row[15], "%d-%m-%Y")).days
                    cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in [index+1, inactive_days, row[1], row[2], row[3], row[10], row[12]]]
                    action_cell = ft.DataCell(ft.Row([
                                ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, icon_color=ft.colors.LIGHT_BLUE_ACCENT_700, on_click=lambda e, row=row: self.inactive_view_popup(row)),
                                ft.IconButton(icon=ft.icons.SETTINGS_BACKUP_RESTORE, icon_color=ft.colors.GREEN_400, on_click=lambda e, row=row: self.inactive_active_popup(row)),
                                ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=extras.icon_button_color, on_click=lambda e, row=row: self.current_delete_popup(row))
                            ]))
                    cells.append(action_cell)
                    self.inactive_data_table.rows.append(ft.DataRow(cells=cells))
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

# show all total details of users using alert dialogue box from inactive_user_(contact) table of database
    def inactive_view_popup(self, row):
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
        enrollment_field = ft.TextField(label="Enrollment No.", value=row[12], width=225, read_only=True, label_style=extras.label_style)
        payed_till_field = ft.TextField(label="Fees Payed Till", value=row[13], text_style=ft.TextStyle(color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD), width=225, read_only=True, label_style=extras.label_style)
        inactive_date_field = ft.TextField(label="Inactive Date  (dd-mm-yyyy)", value=row[15], width=225, read_only=True, label_style=extras.label_style)
        remaining_days_field = ft.TextField(label="Remaining Days", value=row[16], width=225, read_only=True, text_style=ft.TextStyle(color=ft.colors.ORANGE_ACCENT_400, weight=ft.FontWeight.BOLD), label_style=extras.label_style)
        
        name_father_name_row = ft.Row([name_field, father_name_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        contact_aadhar_row = ft.Row([contact_field, aadhar_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        address_gender_row = ft.Row([address_field, gender_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        shift_timing_seat_fees_row = ft.Row([shift_field, timing_field, seat_field, fees_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        joining_enrollment_payed_till_due_fees_row = ft.Row([enrollment_field, payed_till_field, inactive_date_field, remaining_days_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

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
        self.dlg_modal.title = ft.Text("Inactive User", weight=ft.FontWeight.BOLD, color=ft.colors.PURPLE_400, size=19)
        self.dlg_modal.content = main_container
        
        self.dlg_modal.actions = [ft.Container(ft.ElevatedButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True, 
                                                                 width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=ft.colors.PURPLE_400), width=150, alignment=ft.alignment.center)]
        self.page.open(self.dlg_modal)
        self.update()

# show inactive user all detials and used to make it active again.
    def inactive_active_popup(self, row):
        def month_start_changed(e):
            if re.match(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$', month_start_field.value):
                try:
                    if int(previous_days_field.value) > 0:
                        month_end_field.value =  (datetime.strptime(month_start_field.value, "%d-%m-%Y")  + timedelta(days=int(previous_days_field.value))).strftime("%d-%m-%Y")
                    elif int(previous_days_field.value) == 0:
                        # month_end_field.value = (datetime.strptime(month_start_field.value, "%d-%m-%Y")  + relativedelta(months=1)).strftime("%d-%m-%Y")
                        month_end_field.value = "Fees have to be paid."
                except Exception:
                    None
                month_end_field.update()

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

        def reserved_seat_check(timing):
            with open(f'{self.session_value[1]}.json', 'r') as config_file:
                config = json.load(config_file)
            seats_options = config["seats"]

            try:
                con = sqlite3.connect(f"{self.session_value[1]}.db")
                cursor = con.cursor()
                cursor.execute(f"select seat, timing from users_{self.session_value[1]}")
                reserved_seats_timing = cursor.fetchall()

                reserve_seat_list = []
                for reserved_seat, existing_range in reserved_seats_timing:
                    if has_conflict(existing_range, timing):
                        if reserved_seat in seats_options:
                            reserve_seat_list.append(reserved_seat)

                if seat_field.value in reserve_seat_list:
                    seat_field.error_text = "Seat is reserved. Try other."
                    seat_field.update()
                else:
                    return True
            except Exception:
                return

        def activate_btn_clicked(e):
            try:
                start_time = datetime.strptime(f"{start_tf.value} {start_dd.value}", "%I %p").strftime("%I:%M %p")
                end_time = datetime.strptime(f"{end_tf.value} {end_dd.value}", "%I %p").strftime("%I:%M %p")
                timing = f"{start_time} - {end_time}".strip()
            except Exception:
                timing = None

            if all([shift_dd.value, timing, seat_field.value, fees_field.value, int(previous_days_field.value) >= 0, re.match(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$', month_start_field.value)]):
                if not reserved_seat_check(timing):
                    return
                try:
                    conn = sqlite3.connect(f"{self.session_value[1]}.db")
                    cursor = conn.cursor()

                    result = list(row)
                    if result:
                        if int(previous_days_field.value) > 0:
                            joining = month_start_field.value
                            payed_till = month_end_field.value

                        elif int(previous_days_field.value) == 0:
                            joining = month_start_field.value
                            payed_till = month_start_field.value

                        sql = f"INSERT INTO users_{self.session_value[1]} (id, name, father_name, contact, aadhar, address, gender, shift, timing, seat, fees, joining, enrollment, payed_till, img_src) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                        value = (result[0], result[1], result[2], result[3], result[4], result[5], result[6], shift_dd.value, timing, seat_field.value, fees_field.value, joining, result[12], payed_till, result[14])
                        cursor.execute(sql, value)

                        cursor.execute(f"DELETE FROM inactive_users_{self.session_value[1]} WHERE id = ?", (result[0],))
                        conn.commit()

                    if self.tabs.selected_index == 2:
                        self.fetch_inactive_data_table_rows()
                
                    self.page.close(self.dlg_modal)

                except Exception:
                    conn.rollback()
                    return
                finally:
                    conn.close()
                    self.update()

        def shift_dd_change(e):
            for data in shift_options[shift_dd.value]:
                time_list = data.split(" - ")

                time1, period1 = time_list[0].split()
                hour1, minute1 = time1.split(':')

                time2, period2 = time_list[1].split()
                hour2, minute2 = time2.split(':')

                start_tf.value = int(hour1)
                start_dd.value = period1
                end_tf.value = int(hour2)
                end_dd.value = period2

                start_tf.update()
                start_dd.update()
                end_tf.update()
                end_dd.update()

        img = ft.Image(src=os.getcwd()+row[14], height=200, width=250)
        name_field = ft.TextField(label="Name", value=row[1], width=300, read_only=True, label_style=extras.label_style)
        father_name_field = ft.TextField(label="Father Name", value=row[2], width=300, read_only=True, label_style=extras.label_style)
        contact_field = ft.TextField(label="Contact", value=row[3], width=300, read_only=True, label_style=extras.label_style)
        aadhar_field = ft.TextField(label="Aadhar", value=row[4], width=300, read_only=True, label_style=extras.label_style)
        address_field = ft.TextField(label="Address", value=row[5], width=440, read_only=True, label_style=extras.label_style)
        gender_field = ft.TextField(label="Gender", value=row[6], width=160, read_only=True, label_style=extras.label_style)

        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)

        shift_options = config["shifts"]

        shift_dd = ft.Dropdown(
                    label="Shift",
                    value=row[7],
                    width=220,
                    options=[ft.dropdown.Option(shift) for shift in  shift_options],
                    label_style=extras.label_style,
                    on_change=shift_dd_change)
        
        time_list = row[8].split(" - ")

        time1, period1 = time_list[0].split()
        hour1, minute1 = time1.split(':')

        time2, period2 = time_list[1].split()
        hour2, minute2 = time2.split(':')

        start_tf = ft.TextField(label="Start", width=50, value=int(hour1), input_filter=ft.InputFilter(regex_string=r"[0-9]"), label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        start_dd = ft.Dropdown(label="AM/PM", width=50, value=period1, options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        end_tf = ft.TextField(label="End", width=50, value=int(hour2), input_filter=ft.InputFilter(regex_string=r"[0-9]"), label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        end_dd = ft.Dropdown(label="AM/PM", width=50, value=period2, options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        timing_container = ft.Container(content=ft.Row([start_tf, start_dd, end_tf, end_dd], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), width=220, height=50, border=ft.border.all(1, ft.colors.BLACK), border_radius=5)

        seat_field = ft.TextField(label="Seat", value=row[9], width=225, label_style=extras.label_style)
        fees_field = ft.TextField(label="Fees", value=row[10], width=225, label_style=extras.label_style)
        enrollment_field = ft.TextField(label="Enrollment No.", value=row[12], width=225, read_only=True, label_style=extras.label_style)
        month_start_field = ft.TextField(label="Month Start  (dd-mm-yyyy)", value=datetime.today().strftime('%d-%m-%Y'), autofocus=True, on_change=month_start_changed, text_style=ft.TextStyle(color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD), width=225, label_style=extras.label_style)
        previous_days_field = ft.TextField(label="Previous Days", value=row[16], width=225, input_filter=ft.InputFilter(regex_string=r"[0-9]"), on_change=month_start_changed, text_style=ft.TextStyle(color=ft.colors.ORANGE_ACCENT_400, weight=ft.FontWeight.BOLD), label_style=extras.label_style)
        month_end_field = ft.TextField(label="Month End", width=225, label_style=extras.label_style, read_only=True)
        
        try:
            if int(previous_days_field.value) > 0:
                month_end_field.value =  (datetime.strptime(month_start_field.value, "%d-%m-%Y")  + timedelta(days=int(previous_days_field.value))).strftime("%d-%m-%Y")
            elif int(previous_days_field.value) == 0:
                # month_end_field.value = (datetime.strptime(month_start_field.value, "%d-%m-%Y")  + relativedelta(months=1)).strftime("%d-%m-%Y")
                month_end_field.value = "Fees have to be paid."
        except Exception:
            None

        name_father_name_row = ft.Row([name_field, father_name_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        contact_aadhar_row = ft.Row([contact_field, aadhar_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        address_gender_row = ft.Row([address_field, gender_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        shift_timing_seat_fees_row = ft.Row([shift_dd, timing_container, seat_field, fees_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        joining_enrollment_payed_till_due_fees_row = ft.Row([enrollment_field, month_start_field, previous_days_field, month_end_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

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
        self.dlg_modal.title = ft.Text("User Activation", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400, size=19)
        self.dlg_modal.content = main_container

        submit_btn = ft.ElevatedButton("Activate", color=extras.main_eb_color, width=102, bgcolor=ft.colors.GREEN_400, on_click=activate_btn_clicked)
        close_btn = ft.TextButton("Close", on_click=lambda e: self.page.close(self.dlg_modal))

        self.dlg_modal.actions=[submit_btn, close_btn]
        self.dlg_modal.actions_alignment=ft.MainAxisAlignment.END

        self.page.open(self.dlg_modal)
        self.update()

# fetch all data from deleted_users_contact (deleted) table of database and shown it in deleted tab's data table
    def fetch_deleted_data_table_rows(self):
        self.deleted_data_table.rows.clear()
        rows = self.load_data(f"deleted_users_{self.session_value[1]}")
        for index, row in enumerate(rows):
            cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in [index+1, row[1], row[2], row[3], row[6], row[10], row[16]]]
            action_cell = ft.DataCell(ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, icon_color=ft.colors.LIGHT_BLUE_ACCENT_700, on_click=lambda e, row=row: self.view_deleted_popup(row)))
            cells.append(action_cell)
            self.deleted_data_table.rows.append(ft.DataRow(cells=cells))
        self.update_pagination_controls()
        self.update()

# used to show the data of previous / deleted user using alert diaologue box
    def view_deleted_popup(self, row):
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
        img = ft.Image(src=os.getcwd()+row[14], height=200, width=250)
        due_fees_field = ft.TextField(label="Due Fees", value=row[15], width=225, read_only=True, text_style=ft.TextStyle(color=ft.colors.ORANGE_ACCENT_400, weight=ft.FontWeight.BOLD), label_style=extras.label_style)
        leave_date_field = ft.TextField(label="Leave Date", value=row[16], width=225, read_only=True, label_style=extras.label_style)
        reason_field = ft.TextField(label="Reason of leave", value=row[17], width=735, read_only=True, label_style=extras.label_style)

        name_father_name_row = ft.Row([name_field, father_name_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        contact_aadhar_row = ft.Row([contact_field, aadhar_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        address_gender_row = ft.Row([address_field, gender_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        shift_timing_seat_fees_row = ft.Row([shift_field, timing_field, seat_field, fees_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        joining_enrollment_payed_till_due_fees_row = ft.Row([joining_field, enrollment_field, payed_till_field, due_fees_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        leave_date_reason_row = ft.Row([leave_date_field, reason_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        container_1 = ft.Container(content=ft.Column(controls=[img], horizontal_alignment=ft.CrossAxisAlignment.CENTER), width=350)
        container_2 = ft.Container(content=ft.Column(controls=[name_father_name_row, contact_aadhar_row, address_gender_row], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER ), padding=20, expand=True)
        container_3 = ft.Container(content=ft.Column(controls=[shift_timing_seat_fees_row, joining_enrollment_payed_till_due_fees_row, leave_date_reason_row], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER ), expand=True, padding=20)

        main_container = ft.Container(content=ft.Column(controls=[
                                                                    ft.Container(ft.Row([container_1, container_2])),
                                                                    self.divider,
                                                                    container_3,
                                                                    ], spacing=15
                                                            ),
                                                            width=1050, 
                                                            height=480,
                                                            padding=10,
                                                            border_radius=extras.main_container_border_radius, 
                                                            bgcolor=extras.main_container_bgcolor,
                                                            border=extras.main_container_border
                                            )

        
        self.dlg_modal.title = ft.Text("Previous Student", weight=ft.FontWeight.BOLD, color=ft.colors.LIGHT_BLUE_ACCENT_700, size=19)
        self.dlg_modal.content = main_container
        
        self.dlg_modal.actions = [ft.Container(ft.ElevatedButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True, 
                                                                 width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor), width=150, alignment=ft.alignment.center)]
        self.page.open(self.dlg_modal)
        self.update()

# used to update the pagination controls of particular tab
    def update_pagination_controls(self):
        pagination_control = [
            ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                on_click=lambda e: self.change_page(-1) if self.page_number > 1 else None,
                icon_color=ft.colors.LIGHT_BLUE_ACCENT_400 if self.page_number != 1 else ft.colors.GREY,
                disabled=(self.page_number == 1)
            ),
            ft.Text(f"Page {self.page_number} of {self.total_pages}"),
            ft.IconButton(
                icon=ft.icons.ARROW_FORWARD,
                on_click=lambda e: self.change_page(1) if self.page_number < self.total_pages else None,
                icon_color=ft.colors.LIGHT_BLUE_ACCENT_400 if self.page_number != self.total_pages else ft.colors.GREY,
                disabled=(self.page_number == self.total_pages)
            ),
        ]            

        tab_index = self.tabs.selected_index
        if tab_index == 1:
            self.current_pagination_row.controls = pagination_control
        elif tab_index == 3:
            self.deleted_pagination_row.controls = pagination_control
        self.update()

# triggerd, when page is changed using next and previous buttons 
    def change_page(self, direction):
        self.page_number += direction
        tab_index = self.tabs.selected_index
        if tab_index == 1:
            self.fetch_current_data_table_rows()
        elif tab_index == 3:
            self.fetch_deleted_data_table_rows()

# data table to excel export, first fetch data from server, convert it do pandas data frame and return data frame.
    def get_export_data(self):
        if self.tabs.selected_index == 0:
            column = 'name, father_name, contact, aadhar, address, gender, shift, timing, seat, fees, joining, enrollment, payed_till'
            header = ["Sr.No.", "name", "father_name", "contact", "aadhar", "address", "gender", "shift", "timing", "seat", "fees", "joining", "enrollment", "payed_till"]
            sql = f"select {column} from users_{self.session_value[1]} where name=? or father_name=? or contact=? or aadhar=? or address=? or gender=? or shift=? or timing=? or seat=? or fees=? or joining=? or enrollment=? or payed_till=? ORDER BY name {self.search_sort_order.upper()}"
            value = (self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip(), self.search_tf.value.strip())

        elif self.tabs.selected_index == 1:
            column = 'name, father_name, contact, aadhar, address, gender, shift, timing, seat, fees, joining, enrollment, payed_till'
            header = ["Sr.No.", "name", "father_name", "contact", "aadhar", "address", "gender", "shift", "timing", "seat", "fees", "joining", "enrollment", "payed_till"]
            sql = f"select {column} from users_{self.session_value[1]} order by id asc"
            value = ()

        elif self.tabs.selected_index == 3:
            column = 'name, father_name, contact, aadhar, address, gender, shift, timing, seat, fees, joining, enrollment, payed_till, due_fees, leave_date, reason'
            header = ["Sr.No.", "name", "father_name", "contact", "aadhar", "address", "gender", "shift", "timing", "seat", "fees", "joining", "enrollment", "payed_till", "due_fees", "leave_date", "reason"]
            sql = f"select {column} from deleted_users_{self.session_value[1]} order by id asc"
            value = ()


        conn = sqlite3.connect(f"{self.session_value[1]}.db")
        cursor = conn.cursor()
        cursor.execute(sql, value)
        rows = cursor.fetchall()

        excel_list = []
        index = 1
        for row in rows:
            row = list(row)
            row.insert(0, index)
            excel_list.append(row)
            index +=1

        df = pd.DataFrame(excel_list, columns=header)
        return df