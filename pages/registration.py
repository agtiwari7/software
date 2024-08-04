import re
import time
import base64
import sqlite3
import requests
import flet as ft
from utils import cred
from utils import extras
from datetime import datetime, timedelta


class Registration(ft.Column):
    def __init__(self, page, view):
        super().__init__()
        self.title = ft.Row(controls=[ft.Text("Registration", size=30, weight=ft.FontWeight.BOLD)],alignment=ft.MainAxisAlignment.CENTER)
        self.width = 460
        self.page = page
        self.view = view
        self.is_key_validate = None

        self.divider = ft.Divider(height=1, thickness=3, color=extras.divider_color)

        # dialogue box method
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)

        # all types of text field, which takes different types of data with different parameter.
        self.name_field = ft.TextField(label="Business Name", max_length=30, prefix_icon=ft.icons.VERIFIED_USER_OUTLINED, on_submit=lambda e: self.contact_field.focus(), capitalization=ft.TextCapitalization.WORDS)
        self.contact_field = ft.TextField(label="Contact", prefix_text="+91 ", max_length=10, prefix_icon=ft.icons.CONTACT_PAGE,input_filter=ft.InputFilter(regex_string=r"[0-9]"), on_submit=lambda e: self.password_field.focus())
        self.password_field = ft.TextField(label="Password",password=True, can_reveal_password=True, max_length=12, prefix_icon=ft.icons.PASSWORD, on_submit=lambda e: self.key_field.focus())
        self.key_field = ft.TextField(label="Activation Key", on_change=lambda _: self.key_validate(self.key_field.value), max_length=28, prefix_icon=ft.icons.KEY,input_filter=ft.InputFilter(regex_string=r"[a-z, A-Z, 0-9]"), on_submit=self.submit_btn_clicked)
        self.submit_btn = ft.ElevatedButton(text="Submit", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.submit_btn_clicked)
        self.login_page_text = ft.Text("Already have an account?")
        self.login_page_btn = ft.TextButton("Login", on_click=lambda _: self.page.go(self.view))
        self.login_page_row = ft.Row(controls=[self.login_page_text, self.login_page_btn],alignment=ft.MainAxisAlignment.CENTER)
        # create a container, which contains a column, and column contains "name_field, contact_field, password_field, key_field".
        self.container_1 = ft.Container(content=ft.Column(controls=[self.name_field, self.contact_field, self.password_field, self.key_field]), padding=10)

        # adding the STATUS text, internet icon and status text which contains value (online or offline)
        self.status_text = ft.Text("STATUS: ", weight=ft.FontWeight.BOLD)
        self.internet_icon = ft.CircleAvatar(radius=7)
        self.status = ft.Text(size=15)
        # wrapping the STATUS text, internet icon and status text inside a row, called status_row
        self.status_row = ft.Row(controls=[self.status_text, self.internet_icon, self.status])

        # create another container, which contains a row, and row contains "status_row and submit_button".
        self.container_2 = ft.Container(content=
                                ft.Row(controls=
                                        [self.status_row, self.submit_btn],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                        padding=10)
        # run thread for check the internet connection
        self.page.run_thread(handler=self.check_internet_connection)
        
        # main container, which contains all properties and other containers also.
        self.main_container = ft.Container(content=
                                           ft.Column(controls=
                                                     [self.title, self.divider, self.container_1, self.container_2, self.login_page_row]),
                                                     padding=extras.main_container_padding, border_radius=extras.main_container_border_radius, bgcolor=extras.main_container_bgcolor, border=extras.main_container_border)

        # main controls of this calss, which contains everything together
        self.controls = [self.main_container]
    
    def sqlite_server(self, value):
        try:
            con = sqlite3.connect("software.db")
            cur = con.cursor()
            sql = "insert into soft_reg (bus_name, bus_contact, bus_password, act_key, valid_till) values (?, ?, ?, ?, ?)"
            cur.execute(sql, value)
            con.commit()
            con.close()

            self.dlg_modal.title = extras.dlg_title_done
            self.dlg_modal.content = ft.Text("Activation process is completed.")
            self.dlg_modal.on_dismiss = lambda _:self.page.go("/login")
            self.page.open(self.dlg_modal)

        except sqlite3.OperationalError:
            con.close()
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Database not found.")
            self.page.open(self.dlg_modal)
            
        except Exception as e:
            con.close()
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)
        self.update()

    def check_internet_connection(self):
        try:
            while True:
                try:
                    _ = requests.get(url="http://www.google.com", timeout=5)
                    self.internet_icon.bgcolor=ft.colors.GREEN
                    self.status.value ="Online"
                except Exception:
                    self.internet_icon.bgcolor=ft.colors.RED
                    self.status.value = "Offline"
                self.update()
                time.sleep(2)
        except AssertionError:
            pass

    # validate the value and their length also, if failed then open alert dialogue box with error text,
    # otherwise fetch and print the input values and show the alert dialogue box with successfull parameters.
    def submit_btn_clicked(self, e):
        if not all([self.name_field.value, self.contact_field.value, self.password_field.value, self.key_field.value, len(self.contact_field.value)>=10, len(self.key_field.value)>=28, len(self.password_field.value)>=5, self.is_key_validate != None]):
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Provide all the details properly.")
            self.page.open(self.dlg_modal)
            self.update()
        else:
            name = self.name_field.value
            contact = self.contact_field.value
            password = self.password_field.value
            key = self.key_field.value
            key_format = self.key_validate(key)

            current_date = datetime.now()
            future_date = current_date + timedelta(days=int(key_format[-3:]))
            valid_till = future_date.strftime('%d-%m-%Y')

            try:
                value_mysql = (name, contact, password, cred.encrypt_key, key, valid_till)
                value_sqlite = (name, contact, password, key, valid_till)
                # self.mysql_server(value_mysql)
                self.sqlite_server(value_sqlite)
            except Exception as e:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)

    def key_validate(self, key):
        if len(key) == 28:
            try:
                str_2 = key[::-1]
                str_1 = str_2.swapcase()
                no_pad = len(str_1)%3
                b64encode = (str_1 + str(no_pad*"=")).encode("utf-8")
                binary = base64.b64decode(b64encode)
                key_format = binary.decode()

                pattern = r'^KEY-\d{8}-\d{4}-\d{3}$'
                result = re.match(pattern, key_format)
                if result is not None:
                    self.key_field.suffix_icon = ft.icons.DONE_ALL
                    self.update()
                    self.is_key_validate = key_format
                    return key_format
                else:
                    self.key_field.suffix_icon = None
                self.update()

            except Exception:
                pass
        else:
            self.key_field.suffix_icon = None
            self.update()