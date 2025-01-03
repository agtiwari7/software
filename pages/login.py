import os
import re
import json
import sqlite3
import base64
import threading
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

# validate the contact and password from database
    def login_validate_sqlite(self, contact, password):
        con = sqlite3.connect(cred.auth_db_name)
        cur = con.cursor()
        sql = "select * from soft_reg where bus_contact=? AND bus_password=?"
        value = (contact, password)
        cur.execute(sql, value)
        result = cur.fetchone()
        con.close()
        try:
            if result[2] == password:

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

                                     # bus_name, bus_contact, bus_password, valid_till, bus_address
                    self.session_value = [result[0], result[1], result[2], valid_till, result[5]]
                    return True
                else:
                    return False
            else:
                return False
        except Exception:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text("Details are incorrect.")
                self.page.open(self.dlg_modal)

# start working while login button clicked.
    def login_btn_clicked(self, e):
        if not all([self.contact_field.value, self.password_field.value, len(self.contact_field.value)>=10]):
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Provide all the details properly.")
            self.page.open(self.dlg_modal)
        else:
            contact = self.contact_field.value
            password = self.password_field.value
            try:
                if self.login_validate_sqlite(contact, password):
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

                    try:
                        # # Start the backup thread as a daemon
                        update_thread = threading.Thread(target=self.update_changes)
                        update_thread.daemon = True  # Make it a daemon thread
                        update_thread.start()
                    except Exception as e:
                        None

                    # and in last go to the dashboard page
                    self.page.go("/dashboard")
            except sqlite3.OperationalError:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text("Database not found.")
                self.page.open(self.dlg_modal)
                
            except Exception as e:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)
            self.update()

    def update_changes(self):
        def db_img_update():
            contact = str(self.session_value[1])
            if not contact:
                return
            
            db_path = os.path.join(os.getenv('LOCALAPPDATA'), "Programs", "modal", "config", contact, f"{contact}.db")

            if not os.path.exists(db_path):
                return

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            for table in [f"users_{contact}", f"inactive_users_{contact}", f"deleted_users_{contact}"]:
                cursor.execute(f"select id, img_src from {table}")

                result = cursor.fetchall()
                if result:
                    for row in result:
                        row = list(row)
                        # print(row)
                        old = row[1]
                        old = old.replace("/", '\\')
                        contact_pos = old.find(contact)
                        if contact_pos != -1:
                            new = old[contact_pos+10:]
                            row[1] = new
                            print(row)
                            cursor.execute(f"update {table} set img_src=? where id=?", (new, row[0]))

            conn.commit()
            conn.close()

        def changes_for_designation():
        # config file changes for designation
            try:
                with open(f'{self.session_value[1]}.json', 'r') as config_file:
                    config = json.load(config_file)

                if "staff" not in config.keys():
                    data = {"staff": {},}

                    for key in config.keys():
                        data[key] = config[key]

                    with open(f'{self.session_value[1]}.json', "w") as json_file:
                        json.dump(data, json_file, indent=4)
            except Exception:
                None

        # add designation column in history_fees_users table
            try:
                conn = sqlite3.connect(f"{self.session_value[1]}.db")
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info(history_fees_users_{self.session_value[1]})")
                columns = [row[1] for row in cursor.fetchall()]  # row[1] contains the column names

                if "staff" not in columns:
                    alter_table_query = f"ALTER TABLE history_fees_users_{self.session_value[1]} ADD COLUMN staff varchar(40)"
                    cursor.execute(alter_table_query)
                    conn.commit()
                    conn.close()

            except Exception as e:
                print(e)
            finally:
                conn.close()




        db_img_update()
        changes_for_designation()
