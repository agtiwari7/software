import base64
import sqlite3
import hashlib
import subprocess
import flet as ft
import mysql.connector
from utils import extras, cred
import mysql.connector.locales.eng
from datetime import datetime, timedelta

class Registration(ft.Column):
    def __init__(self, page, view, version):
        super().__init__()
        self.title = ft.Row(controls=[ft.Text("Registration", size=30, weight=ft.FontWeight.BOLD)],alignment=ft.MainAxisAlignment.CENTER)
        self.width = 460
        self.page = page
        self.view = view
        self.version = version

        self.divider = ft.Divider(height=1, thickness=3, color=extras.divider_color)

        # dialogue box method
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)

        # all types of text field, which takes different types of data with different parameter.
        self.name_field = ft.TextField(label="Library Name", max_length=25, prefix_icon=ft.icons.VERIFIED_USER_OUTLINED, on_submit=lambda e: self.address_field.focus(), capitalization=ft.TextCapitalization.WORDS)
        self.address_field = ft.TextField(label="Library Address", max_length=30, prefix_icon=ft.icons.VERIFIED_USER_OUTLINED, on_submit=lambda e: self.contact_field.focus(), capitalization=ft.TextCapitalization.WORDS)
        self.contact_field = ft.TextField(label="Contact", prefix_text="+91 ", max_length=10, prefix_icon=ft.icons.CONTACT_PAGE,input_filter=ft.InputFilter(regex_string=r"[0-9]"), on_submit=lambda e: self.password_field.focus())
        self.password_field = ft.TextField(label="Password",password=True, can_reveal_password=True, max_length=12, prefix_icon=ft.icons.PASSWORD, on_submit=self.submit_btn_clicked)
        self.submit_btn = ft.ElevatedButton(text="Submit", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.submit_btn_clicked)
        self.login_page_text = ft.Text("Already have an account?")
        self.login_page_btn = ft.TextButton("Login", on_click=lambda _: self.page.go(self.view))
        self.login_page_row = ft.Row(controls=[self.login_page_text, self.login_page_btn],alignment=ft.MainAxisAlignment.CENTER)
        # create a container, which contains a column, and column contains "name_field, contact_field, password_field".
        self.container_1 = ft.Container(content=ft.Column(controls=[self.name_field, self.address_field, self.contact_field, self.password_field]), padding=10)
        self.container_2 = ft.Container(content=ft.Row(controls=[self.submit_btn],alignment=ft.MainAxisAlignment.CENTER))
        self.container_3 = ft.Container(content=self.login_page_row, margin=10)
        # main container, which contains all properties and other containers also.
        self.main_container = ft.Container(content=
                                           ft.Column(controls=
                                                     [self.title, self.divider, self.container_1, self.container_2, self.container_3]),
                                                     padding=extras.main_container_padding, border_radius=extras.main_container_border_radius, bgcolor=extras.main_container_bgcolor, border=extras.main_container_border)

        self.controls = [self.main_container]

    def get_sys_hash(self):
        result = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'], capture_output=True, text=True)
        uuid = result.stdout.strip().split('\n')[-1].strip()
        hash = hashlib.sha256(uuid.encode()).hexdigest()
        return hash

    def submit_btn_clicked(self, e):
        if not all([self.name_field.value.strip(), self.address_field.value.strip(), self.contact_field.value, self.password_field.value.strip(), len(self.contact_field.value)>=10, len(self.password_field.value)>=5]):
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Provide all the details properly.")
            self.page.open(self.dlg_modal)
            self.update()
        else:
            name = self.name_field.value.strip()
            address = self.address_field.value.strip()
            contact = self.contact_field.value
            password = self.password_field.value.strip()

            future_date = datetime.now() + timedelta(days=5)
            valid_format = f"VALID-{future_date.strftime('%Y%m%d')}"
            binary = valid_format.encode("utf-8")
            b64encode = base64.b64encode(binary).decode("utf-8")
            str_1 = b64encode.replace("=", "")
            str_2 = str_1.swapcase()
            valid_till = str_2[::-1]

            sys_hash = self.get_sys_hash()

            self.mysql_server(name, contact, password, valid_till, sys_hash, address)


    def mysql_server(self, name, contact, password, valid_till, sys_hash, address):
        try:
            connection = mysql.connector.connect(
                host = cred.host,
                user = cred.user,
                password = cred.password,
                database = cred.database
            )
            cursor = connection.cursor()

            soft_reg_sql = "insert into soft_reg (bus_name, bus_contact, bus_password, valid_till, sys_hash, bus_address, bus_uid, soft_version) values (%s, %s, aes_encrypt(%s, %s), %s, %s, %s, %s, %s)"
            soft_reg_value = (name, contact, password, cred.encrypt_key, valid_till, sys_hash, address, "DEMO", self.version)
            cursor.execute(soft_reg_sql, soft_reg_value)
            connection.commit()

            self.sqlite_server(name, contact, password, valid_till, sys_hash, address)
        
        except Exception as e:
            if "soft_reg.bus_contact" in str(e):
                text = "Contact is already registered."
            else:
                text = e
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(text)
            self.page.open(self.dlg_modal)

        finally:
            connection.close()
            self.update()


    def sqlite_server(self, name, contact, password, valid_till, sys_hash, address):
        try:
            con = sqlite3.connect(cred.auth_db_name)
            cur = con.cursor()
            soft_reg_sql = "insert into soft_reg (bus_name, bus_contact, bus_password, valid_till, sys_hash, bus_address, bus_uid) values (?, ?, ?, ?, ?, ?, ?)"
            soft_reg_value = (name, contact, password, valid_till, sys_hash, address, "DEMO")
            cur.execute(soft_reg_sql, soft_reg_value)
            con.commit()

            self.dlg_modal.title = extras.dlg_title_done
            self.dlg_modal.content = ft.Text("Activation process is completed.")
            self.dlg_modal.on_dismiss = lambda _:self.page.go("/login")
            self.page.open(self.dlg_modal)

        except Exception as e:
            if "soft_reg.bus_contact" in str(e):
                text = "Contact is already registered."
            else:
                text = e
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(text)
            self.page.open(self.dlg_modal)
        
        finally:
            con.close()
            self.update()