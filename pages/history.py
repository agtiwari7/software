import sqlite3
import flet as ft
from utils import extras

class History(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.page = page
        self.expand = True
        self.sort_order = "desc"
        self.session_value = session_value
        self.dlg_modal = ft.AlertDialog(modal=True, actions_alignment=ft.MainAxisAlignment.END, surface_tint_color="#44CCCCCC")

# fees pay tab's elements
        self.fees_data_table = ft.DataTable(
            border=ft.border.all(2, "grey"),
            border_radius=10, vertical_lines=ft.BorderSide(1, "grey"),
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
                ft.DataColumn(ft.Text("Amount", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.fees_list_view = ft.ListView([self.fees_data_table], expand=True)
        self.fees_list_view_container = ft.Container(self.fees_list_view, margin=15, expand=True)

# admission tab's elements
        self.admission_data_table = ft.DataTable(
            border=ft.border.all(2, "grey"),
            border_radius=10, vertical_lines=ft.BorderSide(1, "grey"),
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
        self.admission_list_view_container = ft.Container(self.admission_list_view, margin=15, expand=True)
        
# deleted tab's elements
        self.deleted_data_table = ft.DataTable(
            border=ft.border.all(2, "grey"),
            border_radius=10, vertical_lines=ft.BorderSide(1, "grey"),
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
        self.deleted_list_view_container = ft.Container(self.deleted_list_view, margin=15, expand=True)

# main tab property, which contains all tabs
        self.tabs = ft.Tabs(
                    animation_duration=300,
                    on_change=self.on_tab_change,
                    tab_alignment=ft.TabAlignment.START_OFFSET,
                    expand=True,
                    selected_index=0,
                    tabs=[
                        ft.Tab(
                            text="Fees Pay",
                            content=self.fees_list_view_container
                        ),
                        ft.Tab(
                            text="Admission",
                            content=self.admission_list_view_container
                        ),
                        ft.Tab(
                            text="Deleted Student",
                            content=self.deleted_list_view_container
                        ),

                    ],
                )
        
        self.fetch_fees_data_table_rows()

# main tab added to page
        self.controls = [self.tabs]

# triggered when tabs is changed 
    def on_tab_change(self, e):
        if e.control.selected_index == 0:
            self.fetch_fees_data_table_rows()

        elif e.control.selected_index == 1:
            self.fetch_admission_data_table_rows()

        elif e.control.selected_index == 2:
            self.fetch_deleted_data_table_rows()

# fetch fees history data from server and shown it in fees pay tab's data table
    def fetch_fees_data_table_rows(self):
        self.fees_data_table.rows.clear()
        try:
            con = sqlite3.connect(f"{self.session_value[1]}.db")
            cur = con.cursor()
            cur.execute(f"select * from history_fees_users_{self.session_value[1]} ORDER BY id {self.sort_order.upper()}")
            res = cur.fetchall()

            for row in res:
                cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in row]
                self.fees_data_table.rows.append(ft.DataRow(cells=cells))
            
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

# fetch admission history data from server and shown it in admission tab's data table
    def fetch_admission_data_table_rows(self):
        self.admission_data_table.rows.clear()
        try:
            con = sqlite3.connect(f"{self.session_value[1]}.db")
            cur = con.cursor()
            cur.execute(f"select * from history_users_{self.session_value[1]} ORDER BY id {self.sort_order.upper()}")
            res = cur.fetchall()

            for row in res:
                cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in row]
                self.admission_data_table.rows.append(ft.DataRow(cells=cells))
            
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

# fetch deleted students history data from server and shown it in deleted tab's data table
    def fetch_deleted_data_table_rows(self):
        self.deleted_data_table.rows.clear()
        try:
            con = sqlite3.connect(f"{self.session_value[1]}.db")
            cur = con.cursor()
            cur.execute(f"select * from history_deleted_users_{self.session_value[1]} ORDER BY id {self.sort_order.upper()}")
            res = cur.fetchall()

            for row in res:
                cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in row]
                self.deleted_data_table.rows.append(ft.DataRow(cells=cells))
            
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