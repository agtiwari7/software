import calendar
import sqlite3
import datetime
from utils import extras

import flet as ft

class Dashboard(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page
        self.expand = True
        self.current_month_name = datetime.datetime.now().strftime("%B")

        self.dlg_modal = ft.AlertDialog(modal=True, actions_alignment=ft.MainAxisAlignment.END, surface_tint_color="#44CCCCCC")
    
# Enrolled Students Card
        self.enrolled_student_text = ft.Text(color=ft.colors.BLUE, size=40, weight=ft.FontWeight.BOLD)
        self.enrolled_students_card = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(name=ft.icons.PEOPLE, color=ft.colors.BLUE, size=50),
                    ft.Text("Enrolled Students", color=ft.colors.BLACK, size=19),
                    self.enrolled_student_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=270,
            height=190,
            padding=20,
            border_radius=ft.border_radius.all(15),
            bgcolor=ft.colors.BLUE_50,
        )

# Due Fees Students Card
        self.due_fees_students_text = ft.Text(color=ft.colors.ORANGE, size=40, weight=ft.FontWeight.BOLD)
        self.due_fees_students_card = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(name=ft.icons.WARNING, color=ft.colors.ORANGE, size=50),
                    ft.Text("Due Fees Students", color=ft.colors.BLACK, size=19),
                    self.due_fees_students_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=270,
            height=190,
            padding=20,
            border_radius=ft.border_radius.all(15),
            bgcolor=ft.colors.ORANGE_50,
        )

# Current month Fees Collection Card
        self.monthly_fees_collection_text = ft.Text(color=ft.colors.GREEN, size=40, weight=ft.FontWeight.BOLD)
        self.monthly_fees_collection_card = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(name=ft.icons.MONETIZATION_ON, color=ft.colors.GREEN, size=50),
                    ft.Text(f"{self.current_month_name} Fees Collection", color=ft.colors.BLACK, size=19),
                    self.monthly_fees_collection_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=270,
            height=190,
            padding=20,
            border_radius=ft.border_radius.all(15),
            bgcolor=ft.colors.GREEN_50,
        )

# main card container, which contains all cards
        self.main_card_container = ft.Container(ft.Column([self.enrolled_students_card, self.due_fees_students_card, self.monthly_fees_collection_card],
                                                        horizontal_alignment= ft.CrossAxisAlignment.CENTER, 
                                                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                                        expand=True,
                                                        ),
                                                    expand=True)

# ad container, which is used for display advertisment of various product.
        self.ad_container = ft.Container(expand=True, border=ft.Border(right=ft.BorderSide(1, ft.colors.GREY)))

# main page row, which contains card and ad container
        self.main_page_row = ft.Row([self.ad_container, self.main_card_container], expand=True)

# fetch cards data from database
        total_students, total_dues, total_amount = self.fetch_data()
        self.enrolled_student_text.value = total_students
        self.due_fees_students_text.value = total_dues
        self.monthly_fees_collection_text.value = total_amount

# all controls added to page
        self.controls = [self.main_page_row]


# fetch total no of rows of given table of database
    def fetch_data(self):
        try:
            conn = sqlite3.connect(f"{self.session_value[1]}.db")
            cursor = conn.cursor()
            
            # fetch the total number of students
            cursor.execute(f"SELECT COUNT(*) FROM users_{self.session_value[1]}")
            total_students = cursor.fetchone()[0]

            # fetch the total number of fees due students
            cursor.execute(f"SELECT * FROM users_{self.session_value[1]}")
            rows = cursor.fetchall()

            total_dues = 0
            for row in rows:
                given_date = datetime.datetime.strptime(row[13], "%d-%m-%Y")
                difference = (datetime.datetime.now() - given_date).days

                if difference >= 0:
                    total_dues += 1

            # fetch the total credited fees amount of current month
            first_date, last_date = self.get_first_and_last_date_of_current_month()
            cursor.execute(f"select SUM(amount) FROM history_fees_users_{self.session_value[1]} WHERE date between ? AND ?", (first_date, last_date))
            data = cursor.fetchone()[0]
            if data:
                total_amount = f"₹{self.format_indian_number_system(data)}"
            else:
                total_amount = 0

            # return all fetch data
            return total_students, total_dues, total_amount

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


    def get_first_and_last_date_of_current_month(self):
        # Get the current month name and year
        current_year = datetime.datetime.now().year
        
        # Convert month name to month number
        month_number = datetime.datetime.strptime(self.current_month_name, "%B").month
        
        # Get the first date of the month
        first_date = datetime.date(current_year, month_number, 1)
        
        # Get the last date of the month
        last_day = calendar.monthrange(current_year, month_number)[1]
        last_date = datetime.date(current_year, month_number, last_day)
        
        # Format dates as dd-mm-yyyy
        first_date_formatted = first_date.strftime("%d-%m-%Y")
        last_date_formatted = last_date.strftime("%d-%m-%Y")
        
        return first_date_formatted, last_date_formatted

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