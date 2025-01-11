import os
import re
import base64
import hashlib
import sqlite3
import threading
import subprocess
import flet as ft
from datetime import datetime
from utils import extras, cred
from utils.backup import Backup

class Login(ft.Column):
    def __init__(self, page, view):
        super().__init__()
        self.title = ft.Row(controls=[ft.Text("Welcome", size=30, weight=ft.FontWeight.BOLD)],alignment=ft.MainAxisAlignment.CENTER)
        self.width = 400
        self.page = page
        self.view = view

        self.divider = ft.Divider(height=1, thickness=3, color=extras.divider_color)

        # dialogue box method
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)
        
        self.contact_field = ft.TextField(label="Contact", on_change = self.validate, prefix_text="+91 ", max_length=10, prefix_icon=ft.icons.CONTACT_PAGE,input_filter=ft.InputFilter(regex_string=r"[0-9]"), on_submit=lambda e: self.password_field.focus())
        self.password_field = ft.TextField(label="Password",password=True, can_reveal_password=True, on_change = self.validate, max_length=12, prefix_icon=ft.icons.PASSWORD, on_submit=self.login_btn_clicked)
        self.login_btn = ft.ElevatedButton(text="Login", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.login_btn_clicked)
        self.registration_page_text = ft.Text("Don't have an account?")
        self.registration_page_btn = ft.TextButton("Register", on_click=lambda _:self.page.go(self.view))
        # create a container, which contains a column, and column contains "name_field, contact_field, password_field, key_field".
        self.container_1 = ft.Container(content=ft.Column(controls= [self.contact_field, self.password_field]), padding=10)
        self.container_2 = ft.Container(content=ft.Row(controls=[self.login_btn], alignment=ft.MainAxisAlignment.CENTER))
        self.container_3 = ft.Container(content=ft.Row(controls=[self.registration_page_text, self.registration_page_btn],alignment=ft.MainAxisAlignment.CENTER), margin=10)
        # main container, which contains all properties and other containers also.
        self.main_container = ft.Container(content=ft.Column(controls=[self.title, self.divider, self.container_1, self.container_2, self.container_3]),
                                        padding=extras.main_container_padding, border_radius=extras.main_container_border_radius, bgcolor=extras.main_container_bgcolor, border=extras.main_container_border)

        self.controls = [self.main_container]

# validate the input values, if any value is null then disable the login button.
    def validate(self, e):
        if all([self.contact_field.value, self.password_field.value]):
            self.login_btn.disabled = False
        else:
            self.login_btn.disabled = True
        self.update()

# generate the system hash for software activation
    def get_sys_hash(self):
        result = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'], capture_output=True, text=True)
        uuid = result.stdout.strip().split('\n')[-1].strip()
        hash = hashlib.sha256(uuid.encode()).hexdigest()
        return hash


# start working while login button clicked.
    def login_btn_clicked(self, e):
        if not all([self.contact_field.value, self.password_field.value, len(self.contact_field.value)>=10]):
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Provide all the details properly.")
            self.page.open(self.dlg_modal)
            self.update()
            return
        else:
            contact = self.contact_field.value
            password = self.password_field.value


        try:
            con = sqlite3.connect(cred.auth_db_name)
            cur = con.cursor()
            cur.execute("select * from soft_reg where bus_contact=? AND bus_password=?", (contact, password))
            result = cur.fetchone()
            con.close()

            if not result:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text("Details are incorrect.")
                self.page.open(self.dlg_modal)
                self.update()
                return
                
            sys_hash = self.get_sys_hash()      # result[4] is db sys_hash

            if result[4] != sys_hash:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text("Another System Found.")
                self.page.open(self.dlg_modal)
                self.update()
                return

            str_2 = result[3][::-1]
            str_1 = str_2.swapcase()
            no_pad = len(str_1)%3
            b64encode = (str_1 + str(no_pad*"=")).encode("utf-8")
            binary = base64.b64decode(b64encode)
            valid_till_format = binary.decode()

            if re.match(r'^VALID-\d{8}$', valid_till_format) or re.match(r'^VALID-LIFETIME-ACCESS$', valid_till_format):
                if valid_till_format[6:] != "LIFETIME-ACCESS":
                    date_str = valid_till_format[6:]
                    date_obj = datetime.strptime(date_str, "%Y%m%d")
                    valid_till = date_obj.strftime("%d-%m-%Y")
                else:
                    valid_till = "LIFETIME ACCESS"

                                # bus_name, bus_contact, bus_password, valid_till, bus_address, bus_uid
            self.session_value = [result[0], result[1], result[2], valid_till, result[5], result[6]]
        
            session_folder = os.path.join(os.getcwd(), f"{self.session_value[1]}")
            os.makedirs(session_folder, exist_ok=True)
            os.chdir(session_folder)
            os.makedirs(f"{session_folder}/photo/current", exist_ok=True)
            os.makedirs(f"{session_folder}/photo/deleted", exist_ok=True)

            con = sqlite3.connect(f"{self.session_value[1]}.db")
            cur = con.cursor()
            cur.execute(f"create table if not exists users_{contact} (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(40), father_name varchar(40), contact bigint, aadhar bigint unique, address varchar(100), gender varchar(10), shift varchar(30), timing varchar(40), seat varchar(30), fees int, joining varchar(20), enrollment varchar(30) unique, payed_till varchar(20), img_src varchar(200))")
            cur.execute(f"create table if not exists inactive_users_{contact} (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(40), father_name varchar(40), contact bigint, aadhar bigint unique, address varchar(100), gender varchar(10), shift varchar(30), timing varchar(40), seat varchar(30), fees int, joining varchar(20), enrollment varchar(30) unique, payed_till varchar(20), img_src varchar(200), inactive_date varchar(20), remaining_days int)")
            cur.execute(f"create table if not exists deleted_users_{contact} (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(40), father_name varchar(40), contact bigint, aadhar bigint, address varchar(100), gender varchar(10), shift varchar(30), timing varchar(40), seat varchar(30), fees int, joining varchar(20), enrollment varchar(30), payed_till varchar(20), img_src varchar(200), due_fees int, leave_date varchar(20), reason varchar(150))")
            cur.execute(f"create table if not exists history_users_{contact} (id INTEGER PRIMARY KEY AUTOINCREMENT, date varchar(20), name varchar(40), father_name varchar(40), contact bigint, gender varchar(10), enrollment varchar(30), fees int)")
            cur.execute(f"create table if not exists history_deleted_users_{contact} (id INTEGER PRIMARY KEY AUTOINCREMENT, date varchar(20), name varchar(40), father_name varchar(40), contact bigint, gender varchar(10), enrollment varchar(30), due_fees int)")
            cur.execute(f"create table if not exists history_fees_users_{contact} (slip_num INTEGER PRIMARY KEY AUTOINCREMENT, date varchar(20), name varchar(40), father_name varchar(40), contact bigint, gender varchar(10), enrollment varchar(30), amount int, payed_from varchar(30), payed_till varchar(20), staff varchar(40), FOREIGN KEY (enrollment) REFERENCES users_{contact}(enrollment))")
            cur.execute(f"create table if not exists expense_users_{contact} (slip_num INTEGER PRIMARY KEY AUTOINCREMENT, date varchar(20), head varchar(40), description varchar(100), amount int)")
            con.commit()
            con.close()
            self.page.session.set(key=cred.login_session_key ,value=self.session_value)
            
            try:
                # # Start the backup thread as a daemon
                update_thread = threading.Thread(target=Backup, args=(self.session_value,))
                update_thread.daemon = True  # Make it a daemon thread
                update_thread.start()
            except Exception as e:
                None

            self.page.go("/dashboard")
            
        except Exception as e:
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)
            self.update()
