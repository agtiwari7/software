import re
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
    def __init__(self, page, view):
        super().__init__()
        self.title = ft.Row(controls=[ft.Text("Registration", size=30, weight=ft.FontWeight.BOLD)],alignment=ft.MainAxisAlignment.CENTER)
        self.width = 460
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

        # all types of text field, which takes different types of data with different parameter.
        self.name_field = ft.TextField(label="Business Name", max_length=30, prefix_icon=ft.icons.VERIFIED_USER_OUTLINED, on_submit=lambda e: self.address_field.focus(), capitalization=ft.TextCapitalization.WORDS)
        self.address_field = ft.TextField(label="Business Address", max_length=50, prefix_icon=ft.icons.VERIFIED_USER_OUTLINED, on_submit=lambda e: self.contact_field.focus(), capitalization=ft.TextCapitalization.WORDS)
        self.contact_field = ft.TextField(label="Contact", prefix_text="+91 ", max_length=10, prefix_icon=ft.icons.CONTACT_PAGE,input_filter=ft.InputFilter(regex_string=r"[0-9]"), on_submit=lambda e: self.password_field.focus())
        self.password_field = ft.TextField(label="Password",password=True, can_reveal_password=True, max_length=12, prefix_icon=ft.icons.PASSWORD, on_submit=lambda e: self.key_field.focus())
        self.key_field = ft.TextField(label="Activation Key", max_length=28, prefix_icon=ft.icons.KEY,input_filter=ft.InputFilter(regex_string=r"[a-z, A-Z, 0-9]"), on_submit=self.submit_btn_clicked)
        self.submit_btn = ft.ElevatedButton(text="Submit", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.submit_btn_clicked)
        self.login_page_text = ft.Text("Already have an account?")
        self.login_page_btn = ft.TextButton("Login", on_click=lambda _: self.page.go(self.view))
        self.login_page_row = ft.Row(controls=[self.login_page_text, self.login_page_btn],alignment=ft.MainAxisAlignment.CENTER)
        # create a container, which contains a column, and column contains "name_field, contact_field, password_field, key_field".
        self.container_1 = ft.Container(content=ft.Column(controls=[self.name_field, self.address_field, self.contact_field, self.password_field, self.key_field]), padding=10)
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
        if not all([self.name_field.value.strip(), self.address_field.value.strip(), self.contact_field.value, self.password_field.value.strip(), self.key_field.value.strip(), len(self.contact_field.value)>=10, len(self.key_field.value)>=28, len(self.password_field.value)>=5]):
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Provide all the details properly.")
            self.page.open(self.dlg_modal)
            self.update()
        else:
            name = self.name_field.value.strip()
            address = self.address_field.value.strip()
            contact = self.contact_field.value
            password = self.password_field.value.strip()
            act_key = self.key_field.value.strip()
            try:
                str_2 = act_key[::-1]
                str_1 = str_2.swapcase()
                no_pad = len(str_1)%3
                b64encode = (str_1 + str(no_pad*"=")).encode("utf-8")
                binary = base64.b64decode(b64encode)
                key_format = binary.decode()
                pattern = r'^KEY-\d{8}-\d{4}-\d{3}$'
                result = re.match(pattern, key_format)

                if result is not None:
                    date_str = key_format[4:12]
                    date_obj = datetime.strptime(date_str, "%Y%m%d")
                    future_date = date_obj + timedelta(days=int(key_format[-3:]))
                    
                    # encrypting the valid till 
                    valid_format = f"VALID-{future_date.strftime('%Y%m%d')}"
                    binary = valid_format.encode("utf-8")
                    b64encode = base64.b64encode(binary).decode("utf-8")
                    str_1 = b64encode.replace("=", "")
                    str_2 = str_1.swapcase()
                    valid_till = str_2[::-1]

                    sys_hash = self.get_sys_hash()
                    try:
                        self.mysql_server(name, contact, password, act_key, valid_till, sys_hash, address)
                    except Exception as e:
                        self.dlg_modal.title = extras.dlg_title_error
                        self.dlg_modal.content = ft.Text(e)
                        self.page.open(self.dlg_modal)
            except Exception:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text("Key is invalid.")
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)

    def mysql_server(self, name, contact, password, act_key, valid_till, sys_hash, address):
        try:
            connection = mysql.connector.connect(
                host = cred.host,
                user = cred.user,
                password = cred.password,
                database = cred.database
            )
            cursor = connection.cursor()

            soft_reg_sql = "insert into soft_reg (bus_name, bus_contact, bus_password, valid_till, sys_hash, bus_address) values (%s, %s, aes_encrypt(%s, %s), %s, %s, %s)"
            soft_reg_value = (name, contact, password, cred.encrypt_key, valid_till, sys_hash, address)
            cursor.execute(soft_reg_sql, soft_reg_value)

            act_key_sql = "insert into act_key (soft_reg_contact, act_key, valid_till, sys_hash) values (%s, %s, %s, %s)"
            act_key_value = (contact, act_key, valid_till, sys_hash)
            cursor.execute(act_key_sql, act_key_value)

            connection.commit()
            cursor.close()
            connection.close()

            self.sqlite_server(name, contact, password, act_key, valid_till, sys_hash, address)

            self.dlg_modal.title = extras.dlg_title_done
            self.dlg_modal.content = ft.Text("Activation process is completed.")
            self.dlg_modal.on_dismiss = lambda _:self.page.go("/login")
            self.page.open(self.dlg_modal)

        except mysql.connector.errors.IntegrityError as e:
            self.dlg_modal.title = extras.dlg_title_error
            if "soft_reg.bus_contact" in str(e):
                try:
                    sql = "select valid_till from soft_reg where bus_contact=%s AND bus_password=aes_encrypt(%s, %s) AND sys_hash=%s"
                    value = (contact, password, cred.encrypt_key, sys_hash)
                    cursor.execute(sql, value)
                    res = cursor.fetchone()
                    if res:
                        sql = "select valid_till from act_key where act_key=%s AND valid_till=%s AND sys_hash=%s"
                        value = (act_key, res[0], sys_hash)   # res[0] is server valid till, which is stored in server
                        cursor.execute(sql, value)
                        act_res = cursor.fetchone()
                        if act_res:
                            server_valid_till = act_res[0]
                            self.sqlite_server(name, contact, password, act_key, server_valid_till, sys_hash, address)
                            text = "Activation process is completed."
                            self.dlg_modal.title = extras.dlg_title_done
                    else:
                        text = "Contact is already registered."
                except Exception:
                    text = "Contact is already registered."

            elif "act_key.act_key" in str(e):
                text = "Activation Key is already registered."
            else:
                text = e

            self.dlg_modal.content = ft.Text(text)
            self.dlg_modal.on_dismiss = lambda _:self.page.go("/login")
            self.page.open(self.dlg_modal)

        except mysql.connector.errors.DatabaseError:
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Internet is not connected.")
            self.page.open(self.dlg_modal)

        except Exception as e:
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)

        finally:
            cursor.close()
            connection.close()
            self.update()

    def sqlite_server(self, name, contact, password, act_key, valid_till, sys_hash, address):
        try:
            # save registration details locally in sqlite server
            con = sqlite3.connect(cred.auth_db_name)
            cur = con.cursor()
            soft_reg_sql = "insert into soft_reg (bus_name, bus_contact, bus_password, valid_till, sys_hash, bus_address) values (?, ?, ?, ?, ?, ?)"
            soft_reg_value = (name, contact, password, valid_till, sys_hash, address)
            cur.execute(soft_reg_sql, soft_reg_value)

            act_key_sql = "insert into act_key (soft_reg_contact, act_key, valid_till, sys_hash) values (?, ?, ?, ?)"
            act_key_value = (contact, act_key, valid_till, sys_hash)
            cur.execute(act_key_sql, act_key_value)

            con.commit()
            con.close()
        
        except sqlite3.IntegrityError as e:
            if "soft_reg.bus_contact" in str(e):
                text = "Contact is already registered."
            elif "act_key.act_key" in str(e):
                text = "Activation Key is already registered."
            else:
                text = e
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(text)
            self.page.open(self.dlg_modal)

        except sqlite3.OperationalError:
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Database not found.")
            self.page.open(self.dlg_modal)

        except Exception as e:
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)
        
        finally:
            con.close()