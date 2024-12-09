import math
import sqlite3
import flet as ft
from utils import extras
import pandas as pd

class Income(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page
        self.expand = True
        self.export_sql = ""
        self.export_value = ()
        self.sort_order = "asc"
        self.sort_column = "slip_num"

        self.divider = ft.Divider(height=1, thickness=3, color=extras.divider_color)
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)

# top row container elements, which contains date pickers, text, buttons etc.
        self.start_date_picker = ft.DatePicker(on_change=self.start_date_picker_change)
        self.end_date_picker = ft.DatePicker(on_change=self.end_date_picker_change)

        self.duration_text = ft.Text("Duration: ", size=18, weight=ft.FontWeight.W_600)
        self.to_text = ft.Text("To", size=16)
        self.start_date_btn = ft.TextButton("Start Date", on_click=lambda _: self.page.open(self.start_date_picker))
        self.end_date_btn = ft.TextButton("End Date", on_click=lambda _: self.page.open(self.end_date_picker))
        self.all_checkbox = ft.Checkbox(label="All", on_change=self.checkbox_change)
        self.calculate_btn = ft.ElevatedButton(text="Calculate", color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.calculate_btn_click)

        self.duration_container = ft.Container(content=ft.Row(controls=[self.duration_text, self.start_date_btn, self.to_text, self.end_date_btn], spacing=30), width=400)
        self.top_row_container = ft.Container(content=ft.Row(controls=[self.duration_container, self.all_checkbox, self.calculate_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=ft.Padding(left=50, right=50, top=10, bottom=0))

# Fees data table elements
        self.fees_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Slip No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Date", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Father Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Contact", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Enrollment", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Staff", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Amount", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.fees_list_view = ft.ListView([self.fees_data_table], expand=True)
        self.fees_list_view_container = ft.Container(self.fees_list_view, margin=ft.Margin(left=10, right=10, top=5, bottom=0), expand=True, border=ft.border.all(2, "grey"), border_radius=10)
        self.fees_pagination_row = ft.Row([ft.Text("Page 1 of 1")], height=35)

# total amount and slips elements
        self.total_slips_text = ft.Text(size=16, weight=ft.FontWeight.BOLD)
        self.total_amount_text = ft.Text(size=16, color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD)

        self.total_slip_row = ft.Row([ft.Text("Total number of Slips : ", size=16), self.total_slips_text], width=275, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.total_amount_row = ft.Row([ft.Text("Total Amount : ", size=16), self.total_amount_text], width=275, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.total_column = ft.Column([self.total_slip_row, self.total_amount_row])
        self.bottom_row = ft.Row([self.fees_pagination_row, self.total_column], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=self.page.window_width/2)
        
        self.bottom_container = ft.Container(ft.Row(controls=[self.bottom_row], expand=True, alignment=ft.MainAxisAlignment.END), margin=ft.Margin(left=0, right=50, top=10, bottom=20))

# all controls added to page
        self.controls = [self.top_row_container, self.fees_list_view_container, self.bottom_container]

# triggered, when choose date by from_date_picker 
    def start_date_picker_change(self, e):
        self.start_date_btn.text = e.control.value.strftime('%d-%m-%Y')
        self.start_date_btn.update()

# triggered, when choose date by to_date_picker 
    def end_date_picker_change(self, e):
        self.end_date_btn.text = e.control.value.strftime('%d-%m-%Y')
        self.end_date_btn.update()

# used to enable and disable duration container, And fetch / calculate total income from all rows of datatable
    def checkbox_change(self, e):
        if e.control.value:
            self.duration_container.disabled = True
            self.duration_text.color=ft.colors.GREY_700
            self.to_text.color=ft.colors.GREY_700
        else:
            self.duration_container.disabled = False
            self.duration_text.color=None
            self.to_text.color=None
        self.duration_container.update()

# fetch total no of rows and total amount from history_fees table of database
    def get_total_rows_and_amount(self, table_name):
        if self.all_checkbox.value:
            sql = f"SELECT COUNT(*), SUM(amount) FROM {table_name}"
            value = ()
        else:
            start_date = self.start_date_picker.value.strftime("%Y-%m-%d")
            end_date = self.end_date_picker.value.strftime("%Y-%m-%d")
            sql = f"SELECT COUNT(*), SUM(amount) FROM {table_name} WHERE DATE(substr(date, 7, 4) || '-' || substr(date, 4, 2) || '-' || substr(date, 1, 2)) BETWEEN ? AND ?"
            value = (start_date, end_date)
        
        try:
            conn = sqlite3.connect(f"{self.session_value[1]}.db")
            cursor = conn.cursor()
            cursor.execute(sql, value)
            result = cursor.fetchone()
            return result
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
        if self.all_checkbox.value:
            sql = f"SELECT * FROM {table_name} ORDER BY {self.sort_column} {self.sort_order} LIMIT ? OFFSET ?"
            value = (self.rows_per_page, offset)
            self.export_sql = f"SELECT * FROM {table_name} ORDER BY {self.sort_column} {self.sort_order}"
            self.export_value = ()
        else:
            start_date = self.start_date_picker.value.strftime("%Y-%m-%d")
            end_date = self.end_date_picker.value.strftime("%Y-%m-%d")
            sql = f"SELECT * FROM {table_name} WHERE DATE(substr(date, 7, 4) || '-' || substr(date, 4, 2) || '-' || substr(date, 1, 2)) BETWEEN ? AND ? ORDER BY {self.sort_column} {self.sort_order} LIMIT ? OFFSET ?"
            value = (start_date, end_date, self.rows_per_page, offset)
            self.export_sql = f"SELECT * FROM {table_name} WHERE DATE(substr(date, 7, 4) || '-' || substr(date, 4, 2) || '-' || substr(date, 1, 2)) BETWEEN ? AND ? ORDER BY {self.sort_column} {self.sort_order}"
            self.export_value = (start_date, end_date)
        try:
            conn = sqlite3.connect(f"{self.session_value[1]}.db")
            cursor = conn.cursor()
            cursor.execute(sql, value)
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

# add the rows in fees tab data table
    def fetch_fees_data_table_rows(self):
        self.fees_data_table.rows.clear()
        rows = self.load_data(f"history_fees_users_{self.session_value[1]}")
        if rows:
            for row in rows:
                cells = [ft.DataCell(ft.Text(str(cell), size=14)) for cell in [row[0], row[1], row[2], row[3], row[4], row[6], row[10], row[7]]]
                self.fees_data_table.rows.append(ft.DataRow(cells=cells))
            self.update_pagination_controls()
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

        self.fees_pagination_row.controls = pagination_control
        self.fees_pagination_row.update()

# triggerd, when page is changed using next and previous buttons 
    def change_page(self, direction):
        self.page_number += direction
        self.fetch_fees_data_table_rows()

# triggered, when calculate btn clicked, And used to fetch all / specific rows from database, show into datatable and sum the amount
    def calculate_btn_click(self, e):
        if not self.all_checkbox.value:
            if not all([self.start_date_picker.value, self.end_date_picker.value]):
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text("Provide all the details properly.")
                self.page.open(self.dlg_modal)
                self.update()
                return
            
        self.page_number = 1
        self.rows_per_page = 30
        result = self.get_total_rows_and_amount(f"history_fees_users_{self.session_value[1]}")
        self.total_rows = result[0]
        if result[1]:
            self.total_amount =  self.format_indian_number_system(result[1])
        else:
            self.total_amount = 0
        self.total_pages = math.ceil(self.total_rows / self.rows_per_page)

        self.total_slips_text.value = self.total_rows
        self.total_amount_text.value = f"₹ {self.total_amount}"

        self.fetch_fees_data_table_rows()
        self.update()

# convert the amount into indian number system
    def format_indian_number_system(self, number):
        number_str = str(number)[::-1]  # Reverse the string for easier grouping
        grouped = []

        # Group the first 3 digits
        grouped.append(number_str[:3])
        
        # Group every 2 digits after the first 3
        for i in range(3, len(number_str), 2):
            grouped.append(number_str[i:i+2])
        
        # Reverse the grouped parts and join with commas
        formatted_number = ','.join(grouped)[::-1]
        
        return formatted_number
    
# data table to excel export, first fetch data from server, convert it do pandas data frame and return data frame.
    def get_export_data(self):
        try:
            if self.export_sql:
                conn = sqlite3.connect(f"{self.session_value[1]}.db")
                df = pd.read_sql_query(self.export_sql, conn, params=self.export_value)
                conn.close()
                return df
        except Exception as e:
            self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)