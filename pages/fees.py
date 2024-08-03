import flet as ft
import sqlite3
from datetime import datetime
import os
from dateutil.relativedelta import relativedelta
import time

class Fees(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.expand = True

        # Initial sort order state
        self.sort_ascending = True

        # dialogue box method
        self.dlg_modal = ft.AlertDialog(modal=True, actions_alignment=ft.MainAxisAlignment.END, surface_tint_color="#44CCCCCC")
        
        self.search_tf = ft.TextField(label="Name / Contact / Aadhar / Fees / Joining / Shift", capitalization=ft.TextCapitalization.WORDS, width=700, bgcolor="#44CCCCCC", on_submit=self.fetch_data)
        self.search_btn = ft.ElevatedButton("Search", on_click=self.fetch_data, color="Black", bgcolor=ft.colors.GREY_400)
        self.search_container = ft.Container(ft.Row([self.search_tf, self.search_btn], alignment=ft.MainAxisAlignment.CENTER), margin=15)

        self.divider = ft.Divider(height=1, thickness=3, color=ft.colors.LIGHT_BLUE_ACCENT_700)

        self.pay_fees_data_table = ft.DataTable(
            border=ft.border.all(2, "grey"),
            border_radius=10, vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Name", size=18, weight=ft.FontWeight.W_500), on_sort=self.pay_fees_sort_handler),
                ft.DataColumn(ft.Text("Contact", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Aadhar", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Fees", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Joining", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Shift", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Action", size=18, weight=ft.FontWeight.W_500)),
            ])

        self.pay_fees_list_view = ft.ListView([self.pay_fees_data_table], expand=True, visible=False)
        self.pay_fees_data_table_container = ft.Container(self.pay_fees_list_view, margin=15, expand=True)

        self.due_fees_data_table = ft.DataTable(
            border=ft.border.all(2, "grey"),
            border_radius=10, vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Days", size=18, weight=ft.FontWeight.W_500), on_sort=self.sort_handler),
                ft.DataColumn(ft.Text("Name", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Contact", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Aadhar", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Fees", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Shift", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Payed Till", size=18, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text("Action", size=18, weight=ft.FontWeight.W_500)),
            ])

        self.due_list_view = ft.ListView([self.due_fees_data_table], expand=True)

        self.tabs = ft.Tabs(
                    animation_duration=300,
                    on_change=self.on_tab_change,
                    tab_alignment=ft.TabAlignment.START_OFFSET,
                    expand=True,
                    selected_index=1,
                    tabs=[
                        ft.Tab(
                            text="Due(s)",
                            content=ft.Container(self.due_list_view, margin=15, expand=True),
                        ),
                        ft.Tab(
                            text="Pay",
                            content=ft.Container(ft.Column([self.search_container, self.divider, self.pay_fees_data_table_container]))
                        ),
                    ],
                )

        self.controls = [self.tabs]

    def on_tab_change(self, e):
        if e.control.selected_index == 0:
            self.due_fees_data_table.rows.clear()
            con = sqlite3.connect("software.db")
            cur = con.cursor()
            res = cur.execute("select * from users")
            self.due_fees_data = []
            for row in res.fetchall():
                self.due_fees_data.append(list(row))
            con.close()
            if self.due_fees_data:
                for row in self.due_fees_data:
                    given_date = datetime.strptime(row[-2], "%d-%m-%Y")
                    difference = -(datetime.now() - given_date).days
                    if difference <= 0:
                        due_row = [difference, row[1], row[2], row[3], row[4], row[6], row[-2], row[-1]]
                        cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in due_row[:-1]]
                        action_cell = ft.DataCell(ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, on_click=lambda e, due_row=due_row: self.due_fees_popup(due_row)))
                        cells.append(action_cell)
                        self.due_fees_data_table.rows.append(ft.DataRow(cells=cells))
            self.update()

    def sort_handler(self, e: ft.DataColumnSortEvent):
        col_index = e.column_index
        self.sort_ascending = not self.sort_ascending
        sorted_data = sorted(self.due_fees_data, key=lambda row: -(datetime.now() - datetime.strptime(row[-2], "%d-%m-%Y")).days, reverse=not self.sort_ascending)
        self.due_fees_update_table(sorted_data)

    def due_fees_update_table(self, data):
        self.due_fees_data_table.rows.clear()
        if data:
            for row in data:
                given_date = datetime.strptime(row[-2], "%d-%m-%Y")
                difference = -(datetime.now() - given_date).days
                if difference <= 0:
                    due_row = [difference, row[1], row[2], row[3], row[4], row[6], row[-2], row[-1]]
                    cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in due_row[:-1]]
                    action_cell = ft.DataCell(ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, on_click=lambda e, due_row=due_row: self.due_fees_popup(due_row)))
                    cells.append(action_cell)
                    self.due_fees_data_table.rows.append(ft.DataRow(cells=cells))
        self.update()

    def due_fees_popup(self, due_row):
        a = os.getcwd().replace('\\', '/')
        img_src = f"{a}/{due_row[-1]}"

        self.dlg_modal.content = ft.Column([ft.Image(src=img_src, height=150, width=150,),
                                            self.divider,
                                            ft.Container(ft.Column([
                                                ft.Row([ft.Text("Name:", size=16, weight=ft.FontWeight.W_500), ft.TextField(due_row[1], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Contact:", size=16, weight=ft.FontWeight.W_500), ft.TextField(due_row[2], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Aadhar:", size=16, weight=ft.FontWeight.W_500), ft.TextField(due_row[3], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Fees:", size=16, weight=ft.FontWeight.W_500), ft.TextField(due_row[4], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Payed Till:", size=16, weight=ft.FontWeight.W_500), ft.TextField(due_row[-2], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                            ]), margin=10),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=450, height=450)
        
        self.dlg_modal.actions = [ft.TextButton("Okey!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
        self.page.open(self.dlg_modal)
        self.update()

    def fetch_data(self, e):
        con = sqlite3.connect("software.db")
        cur = con.cursor()
        sql = "select * from users where name=? or contact=? or aadhar=? or fees=? or joining=? or shift=? or seat=?"
        value = (self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value)
        res = cur.execute(sql, value)

        self.pay_fees_data = []
        for row in res.fetchall():
            self.pay_fees_data.append(list(row))
        con.close()

        self.pay_fees_data_table.rows.clear()
        self.pay_fees_list_view.visible = True
        if self.pay_fees_data:
            for row in self.pay_fees_data:
                cells = [ft.DataCell(ft.Text(cell, size=16)) for cell in row[1:7]]
                action_cell = ft.DataCell(ft.ElevatedButton(text="Pay Fees", on_click=lambda e, row=row: self.pay_fees_popup(row), color="Black", bgcolor=ft.colors.GREY_400))
                cells.append(action_cell)
                self.pay_fees_data_table.rows.append(ft.DataRow(cells=cells))
        self.update()

    def pay_fees_sort_handler(self, e: ft.DataColumnSortEvent):
        col_index = e.column_index
        self.sort_ascending = not self.sort_ascending
        sorted_data = sorted(self.pay_fees_data, key=lambda row: row[1], reverse=not self.sort_ascending)
        self.pay_fees_update_table(sorted_data)

    def pay_fees_update_table(self, data):
        self.pay_fees_data_table.rows.clear()
        if data:
            for row in data:
                cells = [ft.DataCell(ft.Text(cell, size=16)) for cell in row[1:7]]
                action_cell = ft.DataCell(ft.ElevatedButton(text="Pay Fees", on_click=lambda e, row=row: self.pay_fees_popup(row), color="Black", bgcolor=ft.colors.GREY_400))
                cells.append(action_cell)
                self.pay_fees_data_table.rows.append(ft.DataRow(cells=cells))
        self.update()

    def pay_fees_popup(self, row):
        a = os.getcwd().replace('\\', '/')
        img_src = f"{a}/{row[-1]}"

        date_obj = datetime.strptime(row[-2], "%d-%m-%Y")
        new_date_obj = date_obj + relativedelta(months=1)
        new_date_str = new_date_obj.strftime("%d-%m-%Y")
        duration = f"{row[-2]}  to  {new_date_str}"
        self.dlg_modal.content = ft.Column([ft.Image(src=img_src, height=150, width=150,),
                                            self.divider,
                                            ft.Container(ft.Column([
                                                ft.Row([ft.Text("Name:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[1], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Contact:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[2], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Aadhar:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[3], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Fees:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[4], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Duration:", size=16, weight=ft.FontWeight.W_500), ft.TextField(duration, read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                            ]), margin=10),
                             
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=450, height=470)
        
        self.dlg_modal.actions = [ft.ElevatedButton("Pay", width=100, on_click=lambda e: self.pay_clicked(row, new_date_str)),
                                  ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.dlg_modal))]

        self.page.open(self.dlg_modal)
        self.update()

    def pay_clicked(self, row, new_date_str):
        row[-2] = new_date_str

        con = sqlite3.connect("software.db")
        cur = con.cursor()

        sql = "update users set payed_till=? where contact=? and aadhar=?"
        value = (row[-2], row[2], row[3])

        cur.execute(sql, value)
        con.commit()
        con.close()
        
        self.page.close(self.dlg_modal)
        time.sleep(1)

        self.pay_fees_list_view.visible = False
        self.search_tf.value = ""
        self.pay_fees_data_table.rows.clear()
        self.due_fees_data_table.rows.clear()
        self.update()
