import os
import sqlite3
import flet as ft
from utils import extras
import utils.cred as cred

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
                    login_path = os.path.join(os.getcwd(), f"{self.session_value[1]}")
                    os.makedirs(login_path, exist_ok=True)
                    os.chdir(login_path)
                    os.makedirs(f"{login_path}/photo/current", exist_ok=True)
                    os.makedirs(f"{login_path}/photo/deleted", exist_ok=True)


                    con = sqlite3.connect(f"{self.session_value[1]}.db")
                    cur = con.cursor()
                    cur.execute(f"create table if not exists users_{contact} (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(30), contact bigint, aadhar bigint unique, fees int, joining varchar(15), shift varchar(10), seat varchar(10), payed_till varchar(15), img_src varchar(200))")
                    cur.execute(f"create table if not exists deleted_users_{contact} (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(30), contact bigint, aadhar bigint, fees int, joining varchar(15), shift varchar(10), seat varchar(10), payed_till varchar(15), leave_date varchar(15), reason varchar(150), img_src varchar(200))")
                    con.commit()
                    con.close()
                    self.page.session.set(key=cred.login_session_key ,value=self.session_value)
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

    def login_validate_sqlite(self, contact, password):
        con = sqlite3.connect(cred.auth_db_name)
        cur = con.cursor()
        sql = "select bus_name, bus_contact, bus_password, valid_till from soft_reg where bus_contact=? AND bus_password=?"
        value = (contact, password)
        cur.execute(sql, value)
        result = cur.fetchone()
        con.close()
        try:
            if result[2] == password:
                                    # bus_name, bus_contact, bus_password, valid_till
                self.session_value = [result[0], result[1], result[2], result[3]]
                return True
            else:
                return False
        except Exception:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text("Details are incorrect.")
                self.page.open(self.dlg_modal)