import sqlite3
import flet as ft
from utils import extras
import os
from datetime import datetime
import shutil


class Data(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.page = page
        self.expand = True
        self.session_value = session_value

        self.sort_order_current = "asc"
        self.sort_order_deleted = "asc"

        self.divider = ft.Divider(height=1, thickness=3, color=extras.divider_color)

        self.dlg_modal = ft.AlertDialog(modal=True, actions_alignment=ft.MainAxisAlignment.END, surface_tint_color="#44CCCCCC")

        self.current_data_table = ft.DataTable(
            border=ft.border.all(2, "grey"),
            border_radius=10, vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Sr. No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color ), on_sort=self.sort_current_name),
                ft.DataColumn(ft.Text("Contact", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Aadhar", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Joining", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.current_list_view = ft.ListView([self.current_data_table], expand=True)
        self.current_list_view_container = ft.Container(self.current_list_view, margin=15, expand=True)

        self.deleted_data_table = ft.DataTable(
            border=ft.border.all(2, "grey"),
            border_radius=10, vertical_lines=ft.BorderSide(1, "grey"),
            heading_row_color="#44CCCCCC",
            heading_row_height=60,
            show_bottom_border=True,
            columns=[
                ft.DataColumn(ft.Text("Sr. No.", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color), ),
                ft.DataColumn(ft.Text("Name", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color ), on_sort=self.sort_deleted_name),
                ft.DataColumn(ft.Text("Contact", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Aadhar", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Fees", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Joining", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Pay Till", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Leave Date", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
                ft.DataColumn(ft.Text("Action", size=extras.data_table_header_size, weight=extras.data_table_header_weight, color=extras.data_table_header_color)),
            ])
        self.deleted_list_view = ft.ListView([self.deleted_data_table], expand=True)
        self.deleted_list_view_container = ft.Container(self.deleted_list_view, margin=15, expand=True)

        self.tabs = ft.Tabs(
            animation_duration=300,
            on_change=self.on_tab_change,
            tab_alignment=ft.TabAlignment.START_OFFSET,
            expand=True,
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Current",
                    content=self.current_list_view_container
                ),
                ft.Tab(
                    text="Deleted",
                    content=self.deleted_list_view_container
                ),
            ],
        )
        self.fetch_current_data_table_rows()
        self.controls = [self.tabs]
        
    def on_tab_change(self, e):
        if e.control.selected_index == 0:
            self.fetch_current_data_table_rows()
        elif e.control.selected_index == 1:
            self.fetch_deleted_data_table_rows()

    def fetch_current_data_table_rows(self):
        self.current_data_table.rows.clear()
        try: 
            con = sqlite3.connect("software.db")
            cur = con.cursor()
            res = cur.execute(f"select * from users_{self.session_value[1]} ORDER BY name {self.sort_order_current.upper()}")
            self.due_fees_data = []
            for row in res.fetchall():
                self.due_fees_data.append(list(row))
            con.close()
            if self.due_fees_data:
                for index, row in enumerate(self.due_fees_data):
                    cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in [index+1, row[1], row[2], row[3], row[4], row[5]]]
                    action_cell = ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, icon_color=ft.colors.LIGHT_BLUE_ACCENT_700, on_click=lambda e, row=row: self.current_view_popup(row)),
                        ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=extras.icon_button_color, on_click=lambda e, row=row: self.current_delete_popup(row))
                    ]))
                    cells.append(action_cell)
                    self.current_data_table.rows.append(ft.DataRow(cells=cells))
        except sqlite3.OperationalError:
            con.close()
            self.dlg_modal.actions = [ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Database not found.")
            self.page.open(self.dlg_modal)
        except Exception as e:
            con.close()
            self.dlg_modal.actions = [ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)
        self.update()

    def fetch_deleted_data_table_rows(self):
        self.deleted_data_table.rows.clear()
        try: 
            con = sqlite3.connect("software.db")
            cur = con.cursor()
            res = cur.execute(f"select * from deleted_users_{self.session_value[1]} ORDER BY name {self.sort_order_deleted.upper()}")
            self.due_fees_data = []
            for row in res.fetchall():
                self.due_fees_data.append(list(row))
            con.close()
            if self.due_fees_data:
                for index, row in enumerate(self.due_fees_data):
                    cells = [ft.DataCell(ft.Text(str(cell), size=16)) for cell in [index+1, row[1], row[2], row[3], row[4], row[5], row[8], row[9]]]
                    action_cell = ft.DataCell(ft.IconButton(icon=ft.icons.REMOVE_RED_EYE_OUTLINED, icon_color=ft.colors.LIGHT_BLUE_ACCENT_700, on_click=lambda e, row=row: self.view_deleted_popup(row)))
                    cells.append(action_cell)
                    self.deleted_data_table.rows.append(ft.DataRow(cells=cells))
        except sqlite3.OperationalError:
            con.close()
            self.dlg_modal.actions = [ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Database not found.")
            self.page.open(self.dlg_modal)
        except Exception as e:
            con.close()
            self.dlg_modal.actions = [ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True)]
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)
        self.update()

    def sort_current_name(self, e):
        self.sort_order_current = "asc" if self.sort_order_current == "desc" else "desc"
        self.fetch_current_data_table_rows()

    def sort_deleted_name(self, e):
        self.sort_order_deleted = "asc" if self.sort_order_deleted == "desc" else "desc"
        self.fetch_deleted_data_table_rows()

    def current_view_popup(self, row):
        a = os.getcwd().replace('\\', '/')
        img_src = f"{a}/{row[-1]}"

        self.img = ft.Image(src=img_src, height=150, width=150)
        name_row = ft.Row([ft.Text("Name:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[1], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        contact_row = ft.Row([ft.Text("Contact:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[2], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        aadhar_row = ft.Row([ft.Text("Aadhar:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[3], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        fees_row = ft.Row([ft.Text("Fees:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[4], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        joining_row = ft.Row([ft.Text("Joining:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[5], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        shift_row = ft.Row([ft.Text("Shift:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[6], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        # seat_row = ft.Row([ft.Text("Seat:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[7], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        pay_till_row = ft.Row([ft.Text("Pay Till:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[8], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        container_1 = ft.Container(content=ft.Column(controls=[self.img], width=400, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        container_2 = ft.Container(content=ft.Column(controls=[name_row, contact_row, aadhar_row], horizontal_alignment=ft.CrossAxisAlignment.CENTER ), padding=10, width=400)
        
        container_3 = ft.Container(content=ft.Column(controls=[fees_row,
                                                                shift_row,
                                                                # seat_row
                                                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=10, width=400)
        
        container_4 = ft.Container(content=ft.Column(controls=[ joining_row,
                                                                pay_till_row,
                                                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=10, width=400)

        self.main_container = ft.Container(content=ft.Column(controls=[
                                                                    ft.Container(ft.Row([container_1, container_2], alignment=ft.MainAxisAlignment.END), margin=10),
                                                                    self.divider,
                                                                    ft.Container(ft.Row([container_3, container_4]), margin=10)
                                                                    ]
                                                            ),
                                                            width=870, 
                                                            height=420,
                                                            margin=10, 
                                                            padding=30,
                                                            border_radius=extras.main_container_border_radius, 
                                                            bgcolor=extras.main_container_bgcolor,
                                                            border=extras.main_container_border
                                            )

        self.dlg_modal.content = self.main_container
        
        self.dlg_modal.actions = [ft.Container(ft.ElevatedButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True, 
                                                                 width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor), width=150, alignment=ft.alignment.center)]
        self.page.open(self.dlg_modal)
        self.update()

    def current_delete_popup(self, row):
        a = os.getcwd().replace('\\', '/')
        img_src = f"{a}/{row[-1]}"
        reason_tf = ft.TextField(max_lines=3, multiline=True, capitalization=ft.TextCapitalization.SENTENCES, max_length=120, autofocus=True)
        self.dlg_modal.content = ft.Column([ft.Container(ft.Image(src=img_src, height=150, width=150), margin=10),
                                            self.divider,
                                            ft.Container(ft.Column([
                                                ft.Row([ft.Text("Name:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[1], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Contact:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[2], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Fees:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[4], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Joining:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[5], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                                ft.Row([ft.Text("Reason:", size=16, weight=ft.FontWeight.W_500), reason_tf], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                            ]), margin=10),
                             
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=450, height=600)
        
        self.dlg_modal.actions = [ft.ElevatedButton("Delete", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=lambda e: self.delete_clicked(row, reason_tf.value)),
                                  ft.TextButton("Cancel", on_click=lambda e: self.page.close(self.dlg_modal))]
        self.page.open(self.dlg_modal)
        self.update()

    def delete_clicked(self, row, reason):
        try:
            leave_date = datetime.today().strftime('%d-%m-%Y')
            a = os.getcwd().replace('\\', '/')
            delete_img_src = row[-1].replace("current", "deleted")
            con = sqlite3.connect("software.db")
            cur = con.cursor()
            sql = f"INSERT INTO deleted_users_{self.session_value[1]} (id, name, contact, aadhar, fees, joining, shift, seat, payed_till, leave_date, reason, img_src) SELECT id, name, contact, aadhar, fees, joining, shift, seat, payed_till, ?, ?, ? FROM users_{self.session_value[1]} WHERE id = ?"
            value = ( leave_date, reason, delete_img_src, row[0])
            cur.execute(sql, value)
            sql = f"DELETE FROM users_{self.session_value[1]} WHERE id = ?"
            value = (row[0],)
            cur.execute(sql, value)
            con.commit()
            con.close()
            self.page.close(self.dlg_modal)
            shutil.move(f"{a}/{row[-1]}", f"{a}/{delete_img_src}")
            self.fetch_current_data_table_rows()
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
        self.update()

    def view_deleted_popup(self, row):
        a = os.getcwd().replace('\\', '/')
        img_src = f"{a}/{row[-1]}"

        self.img = ft.Image(src=img_src, height=150, width=150)
        name_row = ft.Row([ft.Text("Name:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[1], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        contact_row = ft.Row([ft.Text("Contact:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[2], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        aadhar_row = ft.Row([ft.Text("Aadhar:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[3], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        fees_row = ft.Row([ft.Text("Fees:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[4], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        joining_row = ft.Row([ft.Text("Joining:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[5], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        shift_row = ft.Row([ft.Text("Shift:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[6], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        # seat_row = ft.Row([ft.Text("Seat:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[7], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        pay_till_row = ft.Row([ft.Text("Pay Till:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[8], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        leave_date_row = ft.Row([ft.Text("Leave:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[9], read_only=True)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        reason_row = ft.Row([ft.Text("Reason:", size=16, weight=ft.FontWeight.W_500), ft.TextField(row[10], read_only=True, multiline=True, max_lines=2)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        container_1 = ft.Container(content=ft.Column(controls=[self.img], width=400, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        container_2 = ft.Container(content=ft.Column(controls=[name_row, contact_row, aadhar_row], horizontal_alignment=ft.CrossAxisAlignment.CENTER ), padding=10, width=400)
        
        container_3 = ft.Container(content=ft.Column(controls=[joining_row,
                                                                fees_row,
                                                                shift_row,
                                                                # seat_row
                                                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=10, width=400)
        
        container_4 = ft.Container(content=ft.Column(controls=[ leave_date_row,
                                                                pay_till_row,
                                                                reason_row
                                                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=10, width=400)

        self.main_container = ft.Container(content=ft.Column(controls=[
                                                                    ft.Container(ft.Row([container_1, container_2], alignment=ft.MainAxisAlignment.END), margin=10),
                                                                    self.divider,
                                                                    ft.Container(ft.Row([container_3, container_4]), margin=10)
                                                                    ]
                                                            ),
                                                            width=870, 
                                                            height=480,
                                                            margin=10, 
                                                            padding=30,
                                                            border_radius=extras.main_container_border_radius, 
                                                            bgcolor=extras.main_container_bgcolor,
                                                            border=extras.main_container_border
                                            )

        self.dlg_modal.content = self.main_container
        
        self.dlg_modal.actions = [ft.Container(ft.ElevatedButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True, 
                                                                 width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor), width=150, alignment=ft.alignment.center)]
        self.page.open(self.dlg_modal)
        self.update()

