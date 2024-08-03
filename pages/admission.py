import flet as ft
import os
from shutil import copy2
import utils.cred as cred
from datetime import datetime
import sqlite3
import mysql.connector
from pages.dashboard import Dashboard

class Admission(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page


        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okey!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)
        
        self.file_picker = ft.FilePicker(on_result=self.on_file_picker_result)

        self.img = ft.Image(src="/images/user.jpg", height=150, width=150, )
        self.choose_photo_btn = ft.ElevatedButton("Choose Photo", color="Black", bgcolor=ft.colors.GREY_400, on_click=lambda _: self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "png", "jpeg"]))
        
        self.name_field = ft.TextField(max_length=30, on_submit=lambda _: self.contact_field.focus(), capitalization=ft.TextCapitalization.WORDS)
        self.contact_field = ft.TextField(prefix_text="+91 ", max_length=10, input_filter=ft.InputFilter(regex_string=r"[0-9]"), on_submit=lambda _: self.aadhar_field.focus())
        self.aadhar_field = ft.TextField( max_length=12, on_submit=lambda _: self.shift_dd.focus(), input_filter=ft.InputFilter(regex_string=r"[0-9]"))
        name_row = ft.Row([ft.Text("Name:", size=16, weight=ft.FontWeight.W_500), self.name_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        contact_row = ft.Row([ft.Text("Contact:", size=16, weight=ft.FontWeight.W_500), self.contact_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        aadhar_row = ft.Row([ft.Text("Aadhar:", size=16, weight=ft.FontWeight.W_500), self.aadhar_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.shift_tf = ft.TextField(visible=False,  on_submit=lambda _: self.fees_dd.focus())
        self.shift_dd = ft.Dropdown(on_change=self.shift_dd_changed,
            options=[
                ft.dropdown.Option("6 hrs"),
                ft.dropdown.Option("12 hrs"),
                ft.dropdown.Option("24 hrs"),
                ft.dropdown.Option("full Night"),
                # ft.dropdown.Option("Custom")
            ])
        shift_row = ft.Row([ft.Text("Shift:", size=16, weight=ft.FontWeight.W_500), self.shift_dd, self.shift_tf], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        # timing_row = ft.Row([ft.Text("Timing:", size=16, weight=ft.FontWeight.W_500), ft.TextField()], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.joining_field = ft.TextField(read_only=True, value=datetime.today().strftime('%d-%m-%Y'))
        joining_date_row = ft.Row([ft.Text("Joining:", size=16, weight=ft.FontWeight.W_500), self.joining_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.fees_tf = ft.TextField(visible=False, input_filter=ft.InputFilter(regex_string=r"[0-9]"), prefix=ft.Text("Rs. "), autofocus=True)
        self.fees_dd = ft.Dropdown(on_change=self.fees_dd_changed,
            options=[
                ft.dropdown.Option("400"),
                ft.dropdown.Option("600"),
                ft.dropdown.Option("900"),
                ft.dropdown.Option("1000"),
                ft.dropdown.Option("Custom")
            ])
        fees_row = ft.Row([ft.Text("Fees:", size=16, weight=ft.FontWeight.W_500), self.fees_dd, self.fees_tf], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        # seat_row = ft.Row([ft.Text("Seat:", size=16, weight=ft.FontWeight.W_500), ft.TextField()], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.submit_btn = ft.ElevatedButton("Submit", color="Black", width=100, bgcolor=ft.colors.GREY_400, on_click=self.submit_btn_clicked)


        container_1 = ft.Container(content=ft.Column(controls=[self.img, ft.Container(self.choose_photo_btn, margin=20)],width=400, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        container_2 = ft.Container(content=ft.Column(controls=[name_row, contact_row, aadhar_row], horizontal_alignment=ft.CrossAxisAlignment.CENTER ), padding=10, width=400)
        self.divider = ft.Divider(height=1, thickness=3, color=ft.colors.LIGHT_BLUE_ACCENT_700)
        container_3 = ft.Container(content=ft.Column(controls=[shift_row,
                                                                # timing_row,
                                                                joining_date_row], horizontal_alignment=ft.CrossAxisAlignment.CENTER,), padding=10, width=400)
        container_4 = ft.Container(content=ft.Column(controls=[ fees_row,
                                                                # seat_row,
                                                                ft.Container(self.submit_btn, margin=10)], horizontal_alignment=ft.CrossAxisAlignment.CENTER,), padding=10, width=400)

        self.main_container = ft.Container(content=ft.Column(controls=[
            ft.Row([container_1, container_2], alignment=ft.MainAxisAlignment.END),
            self.divider,
            ft.Row([container_3, container_4])]),
        width=870,
        margin=50,
        padding=30,
        
        border_radius=15, bgcolor="#44CCCCCC", border=ft.border.all(2, ft.colors.BLACK)
        )

        self.controls = [self.file_picker, self.main_container]
    
    def on_file_picker_result(self, e):
        if e.files:
            selected_file = e.files[0]
            file_path = selected_file.path
            self.img.src = file_path
            self.update()

    
    def fees_dd_changed(self, e):
        if self.fees_dd.value == "Custom":
            self.fees_dd.visible = False
            self.fees_tf.visible = True
            self.fees_tf.focus()
        self.update()
    
    def shift_dd_changed(self, e):
        if self.shift_tf.value == "Custom":
            self.shift_dd.visible = False
            self.shift_tf.visible = True
            self.shift_tf.autofocus = True
        self.update()
    
    def save_photo(self, aadhar):
        # Create the folder hierarchy if it doesn't exist
        target_folder = os.path.join("photo", "active")
        target_folder = "photo/active"
        os.makedirs(target_folder, exist_ok=True)

        file_path = self.img.src
        base_file_name = os.path.basename(file_path)
        file_root, file_extension = os.path.splitext(base_file_name)
        file_name = f"{aadhar}{file_extension}"

        # Define the target file path and Copy the file to the target folder
        # target_file_path = os.path.join(target_folder, file_name)
        target_file_path = f"{target_folder}/{file_name}"
        copy2(file_path, target_file_path)      # shutil.copy2()

        return target_file_path

    # validate the value and their length also, if failed then open alert dialogue box with error text,
    # otherwise fetch and print the input values and show the alert dialogue box with successfull parameters.
    def submit_btn_clicked(self, e):
        if not all([self.name_field.value, self.contact_field.value, self.aadhar_field.value, self.fees_dd.value, self.shift_dd.value, len(self.contact_field.value)>=10, len(self.aadhar_field.value)>=12]):
            self.dlg_modal.title = ft.Text("Error!")
            self.dlg_modal.content = ft.Text("Provide all the details properly.")
            self.page.open(self.dlg_modal)
            self.update()
        else:
            name = self.name_field.value
            contact = self.contact_field.value
            aadhar = self.aadhar_field.value
            if self.fees_dd.value == "Custom":
                fees = self.fees_tf.value
            else:
                fees = self.fees_dd.value
            shift = self.shift_dd.value
            joining = self.joining_field.value
            img_src = self.save_photo(aadhar)
            fees_payed_till = joining
            try:
                value = (name, contact, aadhar, fees, joining, shift, fees_payed_till, img_src)
                # print(value)
                # self.mysql_server(value)
                self.sqlite_server(value)
            except Exception as e:
                self.dlg_modal.title = ft.Text("Error!")
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)

    # save the registration details in sql server
    def mysql_server(self, value):
        # local system's mysql server connect with local server details
        db = mysql.connector.connect(
            host = cred.host,
            user = cred.user,
            password = cred.password,
            database = cred.database
        )
        sql = "insert into users (name, contact, aadhar, fees, joining, shift, fees_payed_till, img_src) values (%s, %s, %s, %s, %s, %s, %s, %s)"
        # sql = "insert into users (name, contact, aadhar, fees, joining, shift, seat, fees_payed_till, img_src) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        try:
            db_cursor = db.cursor()
            db_cursor.execute(sql, value)
            db.commit()

            self.dlg_modal.title = ft.Text("Done!")
            self.dlg_modal.content = ft.Text("Admission process is completed.")
            self.page.open(self.dlg_modal)
            self.dlg_modal.on_dismiss = self.go_to_dashboard

        except mysql.connector.errors.IntegrityError :
            self.dlg_modal.title = ft.Text("Error!")
            self.dlg_modal.content = ft.Text("Aadhar is already registerd.")
            self.page.open(self.dlg_modal)

        except Exception as e:
            self.dlg_modal.title = ft.Text("Error!")
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)
            self.update()
    
    def sqlite_server(self, value):
        con = sqlite3.connect("software.db")
        cur = con.cursor()

        cur.execute("create table if not exists users (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(30), contact bigint, aadhar bigint unique, fees int, joining varchar(15), shift varchar(10), seat varchar(10), fees_payed_till varchar(15), img_src varchar(100))")
        con.commit()

        sql = "insert into users (name, contact, aadhar, fees, joining, shift, fees_payed_till, img_src) values (?, ?, ?, ?, ?, ?, ?, ?)"
        # sql = "insert into users (name, contact, aadhar, fees, joining, shift, fees_payed_till, seat, img_src) values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        try:
            cur.execute(sql, value)
            con.commit()

            self.dlg_modal.title = ft.Text("Done!")
            self.dlg_modal.content = ft.Text("Admission process is completed.")
            self.page.open(self.dlg_modal)
            self.dlg_modal.on_dismiss = self.go_to_dashboard
        except sqlite3.IntegrityError:
            self.dlg_modal.title = ft.Text("Error!")
            self.dlg_modal.content = ft.Text("Aadhar is already registerd.")
            self.page.open(self.dlg_modal)
        con.close()

    def go_to_dashboard(self, e):
        last_view = self.page.views[-1]
        last_view.controls.clear()
        last_view.controls.append(Dashboard(self.page))
        self.page.update()