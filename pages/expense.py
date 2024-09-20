import re
import sqlite3
import flet as ft
from utils import extras
from datetime import datetime

class Expense(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page
        self.expand = True
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
        self.amount_field = ft.TextField(label="Amount", width=200, input_filter=ft.InputFilter(regex_string=r"[0-9]"), prefix=ft.Text("Rs. "), label_style=extras.label_style, text_style=ft.TextStyle(color=ft.colors.ORANGE_ACCENT_400, weight=ft.FontWeight.BOLD), on_submit=self.add_btn_clicked)
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
        self.bottom_container = ft.Container(ft.Row(controls=[self.total_amount_save_btn_row], expand=True, alignment=ft.MainAxisAlignment.END), margin=ft.Margin(left=0, right=50, top=10, bottom=20))


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
                    content=ft.Column([self.top_row, self.add_expense_list_view_container, self.bottom_container])
                ),
                ft.Tab(
                    text="Track",
                    content=ft.Container()
                )
            ],
        )

# Main tab added to page
        self.controls = [self.tabs]

# Triggered when tabs is changed
    def on_tab_change(self, e):
        if e.control.selected_index == 0:
            self.add_expense_data_table.rows.clear()
            self.total_amount = 0
            self.total_amount_text.value = 0
            self.date_field.value=datetime.today().strftime('%d-%m-%Y')
            self.head_field.value = ""
            self.description_field.value = ""
            self.amount_field.value = ""
            self.update()

        elif e.control.selected_index == 1:
            pass

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
        if self.add_expense_list :
            data = []
            for i in self.add_expense_list:
                data.append(i[1:])

            try: 
                con = sqlite3.connect(f"{self.session_value[1]}.db")
                cur = con.cursor()
                query = f"insert into expense_users_{self.session_value[1]} (date, head, description, amount) values (?, ?, ?, ?)"
                cur.executemany(query, data)
                cur.close()
                con.close()
                
                self.dlg_modal.title = extras.dlg_title_done
                self.dlg_modal.content = ft.Text("Expense saved successfully.")
                self.page.open(self.dlg_modal)

                self.add_expense_data_table.rows.clear()
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

