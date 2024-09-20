import sqlite3
import flet as ft
from utils import extras

class Net(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page
        self.expand = True
        self.export_sql = ""
        self.export_value = ()
        self.sort_order = "asc"
        self.sort_column = "slip_num"
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

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
        self.top_row_container = ft.Container(content=ft.Row(controls=[self.duration_container, self.all_checkbox, self.calculate_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=ft.Padding(left=50, right=50, top=20, bottom=20), border=ft.Border(bottom=ft.BorderSide(1, "grey")))

# body container, which shows the total income, total expense, and net income.
        self.total_income_text = ft.Text("0", size=18, weight=ft.FontWeight.BOLD)
        self.total_expense_text = ft.Text("0", size=18, weight=ft.FontWeight.BOLD)
        self.net_income_text = ft.Text("0", size=18, weight=ft.FontWeight.BOLD)

        self.total_income_row = ft.Row([ft.Text("Total Income  : ", size=18), self.total_income_text], width=250, alignment=ft.MainAxisAlignment.SPACE_AROUND)
        self.total_expense_row = ft.Row([ft.Text("Total Expense : ", size=18), self.total_expense_text], width=250, alignment=ft.MainAxisAlignment.SPACE_AROUND)
        self.net_income_row = ft.Row([ft.Text("Net Income : ", size=18), self.net_income_text], width=250, alignment=ft.MainAxisAlignment.SPACE_AROUND)
        
        self.total_income_expense_container = ft.Container(ft.Column([self.total_income_row, self.total_expense_row]), border=ft.Border(bottom=ft.BorderSide(2, "grey")), padding=20)
        self.body_container = ft.Container(ft.Column([self.total_income_expense_container, ft.Container(self.net_income_row, padding=ft.Padding(left=20, right=20, bottom=20, top=10))]), border_radius=10, border=ft.border.all(1, "grey"))

# all controls added to page
        self.controls = [
            self.top_row_container,
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(expand=True),  # This will push the body_container to the middle
                        self.body_container,
                        ft.Container(expand=True),  # This will push the body_container to the middle
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                expand=True
            )
        ]

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

# triggered, when calculate btn clicked, And used to fetch the total amount from the database table
    def calculate_btn_click(self, e):
        if not self.all_checkbox.value:
            if not all([self.start_date_picker.value, self.end_date_picker.value]):
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text("Provide all the details properly.")
                self.page.open(self.dlg_modal)
                self.update()
                return

        if self.all_checkbox.value:
            income_sql = f"SELECT SUM(amount) FROM history_fees_users_{self.session_value[1]}"
            income_value = ()
            expense_sql = f"SELECT SUM(amount) FROM expense_users_{self.session_value[1]}"
            expense_value = ()
        else:
            start_date = self.start_date_picker.value.strftime('%d-%m-%Y')
            end_date = self.end_date_picker.value.strftime('%d-%m-%Y')
            income_sql = f"SELECT SUM(amount) FROM history_fees_users_{self.session_value[1]} WHERE date between ? AND ?"
            income_value = (start_date, end_date)
            expense_sql = f"SELECT SUM(amount) FROM expense_users_{self.session_value[1]} WHERE date between ? AND ?"
            expense_value = (start_date, end_date)
        
        try:
            conn = sqlite3.connect(f"{self.session_value[1]}.db")
            cursor = conn.cursor()
            cursor.execute(income_sql, income_value)
            total_income = cursor.fetchone()[0]
            cursor.execute(expense_sql, expense_value)
            total_expense = cursor.fetchone()[0]
        
            if not total_income:
                total_income = 0
            if not total_expense:
                total_expense = 0
            
            self.total_income_text.value = total_income
            self.total_expense_text.value = total_expense

            net_income = total_income - total_expense
            
            if 0 > net_income:
                self.net_income_text.value = f"- {self.format_indian_number_system(-net_income)}"
                self.net_income_text.color = ft.colors.DEEP_ORANGE_400
            elif 0 == net_income:
                self.net_income_text.value = f"₹ {self.format_indian_number_system(net_income)}"
                self.net_income_text.color = "white"
            else:
                self.net_income_text.value = f"₹ {self.format_indian_number_system(net_income)}"
                self.net_income_text.color = ft.colors.GREEN_400
        
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