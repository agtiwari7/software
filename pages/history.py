import math
import sqlite3
import flet as ft
import pandas as pd
from utils import extras

class History(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.page = page
        self.expand = True
        self.sort_order = "desc"
        self.sort_column = "slip_num"
        self.export_sql = None
        self.export_value = None
        self.session_value = session_value
        
        self.dlg_modal = ft.AlertDialog(modal=True, actions_alignment=ft.MainAxisAlignment.END, surface_tint_color="#44CCCCCC")
        
        self.page_number = 1
        self.rows_per_page = 30
        self.total_rows = self.get_total_rows(f"history_fees_users_{self.session_value[1]}")
        self.total_pages = math.ceil(self.total_rows / self.rows_per_page)


# Fees pay tab's elements
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
                # ft.DataColumn(ft.Text("Gender", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Enrollment", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Amount", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Duration", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.fees_list_view = ft.ListView([self.fees_data_table], expand=True)
        self.fees_list_view_container = ft.Container(self.fees_list_view, margin=10, expand=True, border=ft.border.all(2, "grey"), border_radius=10)
        self.fees_pagination_row = ft.Row(height=35, alignment=ft.MainAxisAlignment.CENTER)

# Admission tab's elements
        self.admission_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Sr. No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Date", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Father Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Contact", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Gender", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Enrollment", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.admission_list_view = ft.ListView([self.admission_data_table], expand=True)
        self.admission_list_view_container = ft.Container(self.admission_list_view, margin=10, expand=True, border=ft.border.all(2, "grey"), border_radius=10)
        self.admission_pagination_row = ft.Row(height=35, alignment=ft.MainAxisAlignment.CENTER)

# Deleted tab's elements
        self.deleted_data_table = ft.DataTable(
            vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Sr. No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Date", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Father Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Contact", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Gender", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Enrollment", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Due Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.deleted_list_view = ft.ListView([self.deleted_data_table], expand=True)
        self.deleted_list_view_container = ft.Container(self.deleted_list_view, margin=10, expand=True, border=ft.border.all(2, "grey"), border_radius=10)
        self.deleted_pagination_row = ft.Row(height=35, alignment=ft.MainAxisAlignment.CENTER)


# Main tab property, which contains all tabs
        self.tabs = ft.Tabs(
            animation_duration=300,
            on_change=self.on_tab_change,
            tab_alignment=ft.TabAlignment.START_OFFSET,
            expand=True,
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Fees Pay",
                    content=ft.Column(controls=[self.fees_list_view_container, self.fees_pagination_row])
                ),
                ft.Tab(
                    text="Admission",
                    content=ft.Column(controls=[self.admission_list_view_container, self.admission_pagination_row])
                ),
                ft.Tab(
                    text="Deleted Student",
                    content=ft.Column(controls=[self.deleted_list_view_container, self.deleted_pagination_row])
                ),
            ],
        )

        self.fetch_fees_data_table_rows()

# Main tab added to page
        self.controls = [self.tabs]

# triggered when tabs is changed
    def on_tab_change(self, e):
        if e.control.selected_index == 0:
            self.fees_data_table.rows.clear()
            self.page_number = 1
            self.rows_per_page = 30
            self.total_rows = self.get_total_rows(f"history_fees_users_{self.session_value[1]}")
            self.total_pages = math.ceil(self.total_rows / self.rows_per_page)
            self.fetch_fees_data_table_rows()

        elif e.control.selected_index == 1:
            self.admission_data_table.rows.clear()
            self.page_number = 1
            self.rows_per_page = 30
            self.total_rows = self.get_total_rows(f"history_users_{self.session_value[1]}")
            self.total_pages = math.ceil(self.total_rows / self.rows_per_page)
            self.fetch_admission_data_table_rows()

        elif e.control.selected_index == 2:
            self.deleted_data_table.rows.clear()
            self.page_number = 1
            self.rows_per_page = 30
            self.total_rows = self.get_total_rows(f"history_deleted_users_{self.session_value[1]}")
            self.total_pages = math.ceil(self.total_rows / self.rows_per_page)
            self.fetch_deleted_data_table_rows()

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
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY {self.sort_column} {self.sort_order} LIMIT ? OFFSET ?", (self.rows_per_page, offset))
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

        table_name = f"history_fees_users_{self.session_value[1]}"
        self.export_sql = f"select * from {table_name} order by slip_num desc"
        self.export_value = ()

        self.sort_column = "slip_num"
        rows = self.load_data(table_name)
        for row in rows:
            duration = f"{row[8]}  To  {row[9]}"
            row = [row[0], row[1], row[2], row[3], row[4], row[6], row[7], duration]
            cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in row]
            self.fees_data_table.rows.append(ft.DataRow(cells=cells))
        self.update_pagination_controls()
        self.update()

# add the rows in admission tab data table
    def fetch_admission_data_table_rows(self):
        self.admission_data_table.rows.clear()

        table_name = f"history_users_{self.session_value[1]}"
        self.export_sql = f"select * from {table_name} order by id desc"
        self.export_value = ()

        self.sort_column = "id"
        rows = self.load_data(table_name)
        for row in rows:
            cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in row]
            self.admission_data_table.rows.append(ft.DataRow(cells=cells))
        self.update_pagination_controls()
        self.update()

# add the rows in deleted tab data table
    def fetch_deleted_data_table_rows(self):
        self.deleted_data_table.rows.clear()

        table_name = f"history_deleted_users_{self.session_value[1]}"
        self.export_sql = f"select * from {table_name} order by id desc"
        self.export_value = ()

        self.sort_column = "id"
        rows = self.load_data(table_name)
        for row in rows:
            cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in row]
            self.deleted_data_table.rows.append(ft.DataRow(cells=cells))
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

        tab_index = self.tabs.selected_index
        if tab_index == 0:
            self.fees_pagination_row.controls = pagination_control
        elif tab_index == 1:
            self.admission_pagination_row.controls = pagination_control
        elif tab_index == 2:
            self.deleted_pagination_row.controls = pagination_control
        self.update()

# triggerd, when page is changed using next and previous buttons 
    def change_page(self, direction):
        self.page_number += direction
        tab_index = self.tabs.selected_index
        if tab_index == 0:
            self.fetch_fees_data_table_rows()
        elif tab_index == 1:
            self.fetch_admission_data_table_rows()
        elif tab_index == 2:
            self.fetch_deleted_data_table_rows()
    
# data table to excel export, first fetch data from server, convert it do pandas data frame and return data frame.
    def get_export_data(self):
        conn = sqlite3.connect(f"{self.session_value[1]}.db")
        df = pd.read_sql_query(self.export_sql, conn, params=self.export_value)
        conn.close()
        return df