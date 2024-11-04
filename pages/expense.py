import re
import math
import sqlite3
import flet as ft
import pandas as pd
from utils import extras
from datetime import datetime

class Expense(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page
        self.expand = True
        self.export_sql = ""
        self.export_value = ()
        self.sort_order = "desc"
        self.sort_column = "slip_num"
        self.add_expense_index = 1
        self.add_expense_list = []
        self.total_amount = 0

        self.divider = ft.Divider(height=1, thickness=3, color=extras.divider_color)
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)

# Add tab's elements
        self.date_field = ft.TextField(label="Date (dd-mm-yyyy)", max_length=10, value=datetime.today().strftime('%d-%m-%Y'), width=180, label_style=extras.label_style)
        self.head_field = ft.TextField(label="Head", max_length=40, capitalization=ft.TextCapitalization.WORDS, width=200, label_style=extras.label_style, on_submit=lambda _: self.description_field.focus())
        self.description_field = ft.TextField(label="Description", max_length=100, capitalization=ft.TextCapitalization.WORDS, width=430, label_style=extras.label_style, on_submit=lambda _: self.amount_field.focus())
        self.amount_field = ft.TextField(label="Amount", width=200, max_length=6, input_filter=ft.InputFilter(regex_string=r"[0-9]"), prefix=ft.Text("Rs. "), label_style=extras.label_style, text_style=ft.TextStyle(color=ft.colors.ORANGE_ACCENT_400, weight=ft.FontWeight.BOLD), on_submit=self.add_btn_clicked)
        self.add_btn = ft.ElevatedButton(text="Add", color=ft.colors.GREEN_400, bgcolor=extras.secondary_eb_bgcolor, on_click=self.add_btn_clicked)

        self.top_row = ft.Row([self.date_field, self.head_field, self.description_field, self.amount_field, self.add_btn], alignment=ft.MainAxisAlignment.SPACE_EVENLY, height=110)

        # Add expense data table elements
        self.add_expense_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Sr. No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Date", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Head", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Description", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Amount", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ]
        )
        self.add_expense_list_view = ft.ListView([self.add_expense_data_table], expand=True)
        self.add_expense_list_view_container = ft.Container(self.add_expense_list_view, margin=ft.Margin(left=10, right=10, top=0, bottom=0), expand=True, border=ft.border.all(2, "grey"), border_radius=10)

        self.total_amount_text = ft.Text(self.total_amount, size=16, color=ft.colors.DEEP_ORANGE_400, weight=ft.FontWeight.BOLD)
        self.total_amount_row = ft.Row([ft.Text("Total Amount : ", size=16), self.total_amount_text], width=250)
        self.submit_btn = ft.ElevatedButton("Submit", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.submit_btn_clicked)
    
        self.total_amount_save_btn_row = ft.Row([self.total_amount_row, self.submit_btn], width=450, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.total_amount_save_btn_row_container = ft.Container(ft.Row(controls=[self.total_amount_save_btn_row], expand=True, alignment=ft.MainAxisAlignment.END), margin=ft.Margin(left=0, right=50, top=10, bottom=20))

# track tab's element
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
        self.track_expense_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Slip No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Date", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Head", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Description", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Amount", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.track_expense_list_view = ft.ListView([self.track_expense_data_table], expand=True)
        self.track_expense_list_view_container = ft.Container(self.track_expense_list_view, margin=ft.Margin(left=10, right=10, top=5, bottom=0), expand=True, border=ft.border.all(2, "grey"), border_radius=10)
        self.track_expense_pagination_row = ft.Row([ft.Text("Page 1 of 1")], height=35)

        # total amount and expense slips elements
        self.total_expense_slip_text = ft.Text(size=16, weight=ft.FontWeight.BOLD)
        self.total_expense_slip_amount_text = ft.Text(size=16, color=ft.colors.DEEP_ORANGE_400, weight=ft.FontWeight.BOLD)

        self.total_expense_slip_row = ft.Row([ft.Text("Total Expense Slips : ", size=16), self.total_expense_slip_text], width=275, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.total_expense_slip_amount_row = ft.Row([ft.Text("Total Amount : ", size=16), self.total_expense_slip_amount_text], width=275, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.total_expense_slip_column = ft.Column([self.total_expense_slip_row, self.total_expense_slip_amount_row])
        self.track_expense_bottom_row = ft.Row([self.track_expense_pagination_row, self.total_expense_slip_column], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=self.page.window_width/2)
        
        self.track_expense_bottom_row_container = ft.Container(ft.Row(controls=[self.track_expense_bottom_row], expand=True, alignment=ft.MainAxisAlignment.END), margin=ft.Margin(left=0, right=50, top=10, bottom=10))


# Main tab property, which contains all tabs
        self.tabs = ft.Tabs(
            animation_duration=300,
            on_change=self.on_tab_change,
            tab_alignment=ft.TabAlignment.START_OFFSET,
            expand=True,
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Add",
                    content=ft.Column([self.top_row, self.add_expense_list_view_container, self.total_amount_save_btn_row_container])
                ),
                ft.Tab(
                    text="Track",
                    content=ft.Column([self.top_row_container, self.track_expense_list_view_container, self.track_expense_bottom_row_container])
                )
            ],
        )

# Main tab added to page
        self.controls = [self.tabs]

# Triggered when tabs is changed
    def on_tab_change(self, e):
        if e.control.selected_index == 0:
            self.add_expense_data_table.rows.clear()
            self.add_expense_list.clear()
            self.add_expense_index = 1
            self.total_amount = 0
            self.total_amount_text.value = 0
            self.date_field.value=datetime.today().strftime('%d-%m-%Y')
            self.head_field.value = ""
            self.description_field.value = ""
            self.amount_field.value = ""
            self.update()

        elif e.control.selected_index == 1:
            self.start_date_btn.text = "Start Date"
            self.end_date_btn.text = "End Date"
            self.all_checkbox.value = False
            self.track_expense_data_table.rows.clear()
            self.total_expense_slip_text.value = ""
            self.total_expense_slip_amount_text.value = ""
            self.track_expense_pagination_row.controls = [ft.Text("Page 1 of 1")]
            self.duration_container.disabled = False
            self.duration_text.color=None
            self.to_text.color=None
            self.update()

# Triggered when add button is clicked and used to add data to the data table
    def add_btn_clicked(self, e):
        if not all([self.head_field.value, self.description_field.value, self.amount_field.value,
                    re.match(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$', self.date_field.value) ]):
            self.date_field.value=datetime.today().strftime('%d-%m-%Y')
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Provide all the details properly.")
            self.page.open(self.dlg_modal)
            self.update()
        else:
            date = self.date_field.value
            head = self.head_field.value
            description = self.description_field.value
            amount = self.amount_field.value

            row = [self.add_expense_index, date, head, description, amount]
            self.add_expense_list.append(row)
            
            self.total_amount += int(amount)
            self.total_amount_text.value = self.total_amount

            self.add_expense_index += 1
            self.head_field.value = ""
            self.description_field.value = ""
            self.amount_field.value = ""

            # Add the row to the DataTable
            self.add_row_to_table(row)
            self.update()

# Adds the row to the add expense table
    def add_row_to_table(self, row):
        cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in row]
        action_cell = ft.DataCell(
            ft.Row([
                ft.ElevatedButton(
                    text="Delete",
                    color=ft.colors.DEEP_ORANGE_400,
                    bgcolor=extras.secondary_eb_bgcolor,
                    on_click=lambda e, row=row: self.expense_row_delete(row)
                )
            ])
        )
        cells.append(action_cell)
        self.add_expense_data_table.rows.append(ft.DataRow(cells=cells))
        self.update()

# Function to delete the row of add expense table
    def expense_row_delete(self, row):
        self.total_amount -= int(row[4])
        self.total_amount_text.value = self.total_amount

        self.add_expense_list.remove(row)
        self.add_expense_data_table.rows.clear()
        for index, row in enumerate(self.add_expense_list):
            row[0] = index + 1  # Update Sr. No.
            self.add_row_to_table(row)
        self.update()

# used to save the expense in database table
    def submit_btn_clicked(self, e):
        if self.add_expense_list:
            data = []
            for i in self.add_expense_list:
                data.append(i[1:])

            try: 
                con = sqlite3.connect(f"{self.session_value[1]}.db")
                cur = con.cursor()
                query = f"insert into expense_users_{self.session_value[1]} (date, head, description, amount) values (?, ?, ?, ?)"
                cur.executemany(query, data)
                con.commit()
                cur.close()
                con.close()
                
                self.dlg_modal.title = extras.dlg_title_done
                self.dlg_modal.content = ft.Text("Expense saved successfully.")
                self.page.open(self.dlg_modal)

                self.add_expense_data_table.rows.clear()
                self.add_expense_list.clear()
                self.add_expense_index = 1
                self.total_amount = 0
                self.total_amount_text.value = 0
                self.date_field.value=datetime.today().strftime('%d-%m-%Y')
                self.head_field.value = ""
                self.description_field.value = ""
                self.amount_field.value = ""

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
        
        else:
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Provide all the details properly.")
            self.page.open(self.dlg_modal)
            self.update()

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
        result = self.get_total_rows_and_amount(f"expense_users_{self.session_value[1]}")
        self.total_rows = result[0]
        if result[1]:
            self.total_amount =  self.format_indian_number_system(result[1])
        else:
            self.total_amount = 0
        self.total_pages = math.ceil(self.total_rows / self.rows_per_page)

        self.total_expense_slip_text.value = self.total_rows
        self.total_expense_slip_amount_text.value = f"₹ {self.total_amount}"

        self.fetch_track_expense_data_table_rows()
        self.update()

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
    def fetch_track_expense_data_table_rows(self):
        self.track_expense_data_table.rows.clear()
        rows = self.load_data(f"expense_users_{self.session_value[1]}")
        if rows:
            for row in rows:
                cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in row]
                self.track_expense_data_table.rows.append(ft.DataRow(cells=cells))
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

        self.track_expense_pagination_row.controls = pagination_control
        self.track_expense_pagination_row.update()

# triggerd, when page is changed using next and previous buttons 
    def change_page(self, direction):
        self.page_number += direction
        self.fetch_track_expense_data_table_rows()

# data table to excel export, first fetch data from server, convert it do pandas data frame and return data frame.
    def get_export_data(self):
        try:
            if self.tabs.selected_index == 0:
                header = ["Sr.No.", "Date", "Head", "Description", "Amount"]
                df = pd.DataFrame(self.add_expense_list, columns=header)
                return df
            
            elif self.tabs.selected_index == 1 and self.export_sql:
                conn = sqlite3.connect(f"{self.session_value[1]}.db")
                df = pd.read_sql_query(self.export_sql, conn, params=self.export_value)
                conn.close()
                return df
            
        except Exception as e:
            self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)