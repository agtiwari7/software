import flet as ft
import sqlite3
from pages.dashboard import Dashboard
class Fees(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.expand = True

        # dialogue box method
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okey!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)
        
        self.search_tf = ft.TextField(label="Name / Contact / Aadhar / Fees / Joining / Shift", capitalization=ft.TextCapitalization.WORDS, width=700, bgcolor="#44CCCCCC",)
        self.search_btn = ft.ElevatedButton("Search", on_click=self.fetch_data, color="Black", bgcolor=ft.colors.GREY_400)
        self.search_container = ft.Container(ft.Row([self.search_tf,self.search_btn], alignment=ft.MainAxisAlignment.CENTER), margin=15)

        self.divider = ft.Divider(height=1, thickness=3, color=ft.colors.LIGHT_BLUE_ACCENT_700)

        self.data_table = ft.DataTable(
            border=ft.border.all(2,"grey"),
            border_radius=10, vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Name", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Contact", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Aadhar", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Fees", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Joining", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Shift", size=18, weight=ft.FontWeight.W_500)),
                # ft.DataColumn(ft.Text("Seat", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Action", size=18, weight=ft.FontWeight.W_500)),
            ])

        self.list_view = ft.ListView([self.data_table],  expand=True, visible=False)
        self.data_table_container = ft.Container(self.list_view, margin=15, expand=True)

        self.controls = [self.search_container, self.divider, self.data_table_container]

    def fetch_data(self, e):
        con = sqlite3.connect("software.db")
        cur = con.cursor()

        sql = "select * from users where name=? or contact=? or aadhar=? or fees=? or joining=? or shift=? or seat=?"
        value = (self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value)

        res = cur.execute(sql, value)

        self.data = []
        for row in res.fetchall():
            self.data.append(list(row))
        con.close()

        # self.data_table.rows.clear()
        if self.data:
            self.list_view.visible = True
            for row in self.data:
                cells = [ft.DataCell(ft.Text(cell, size=16)) for cell in row[1:7]]
                action_cell = ft.DataCell(ft.ElevatedButton(text="Pay Fees", on_click=lambda e, row=row: self.pay_fees(row), color="Black", bgcolor=ft.colors.GREY_400))
                cells.append(action_cell)
                self.data_table.rows.append(ft.DataRow(cells=cells))
        self.update()

    def go_to_dashboard(self, e):
        last_view = self.page.views[-1]
        last_view.controls.clear()
        last_view.controls.append(Dashboard(self.page))
        self.page.update()

    def pay_fees(self, row):
        self.dlg_modal.title = ft.Text("Done!")
        self.dlg_modal.content = ft.Text(f"Fees Payed Successfully for {row}")
        self.page.open(self.dlg_modal)
        # self.dlg_modal.on_dismiss = self.go_to_dashboard