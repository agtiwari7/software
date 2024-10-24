import os
import re
import base64
import hashlib
import sqlite3
# import webbrowser
import subprocess
import flet as ft
from utils import cred
import mysql.connector
from utils import extras
import mysql.connector.locales.eng
from datetime import datetime, timedelta

class Activate(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page
        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)
        
        
        self.software_activation_text_container = ft.Container(ft.Row([ft.Text("Software Activation", size=26, weight=ft.FontWeight.BOLD)], width=350, alignment=ft.MainAxisAlignment.CENTER), border=ft.Border(bottom=ft.BorderSide(2, "grey")), padding=ft.Padding(left=20, right=20, bottom=20, top=0), margin=ft.Margin(left=0, right=0, bottom=20, top=0))
        self.key_tf = ft.TextField(label="Activation Key", max_length=28, width=390, prefix_icon=ft.icons.KEY,input_filter=ft.InputFilter(regex_string=r"[a-z, A-Z, 0-9]"))
        self.submit_btn = ft.ElevatedButton("Submit", color=extras.main_eb_color, width=extras.main_eb_width, bgcolor=extras.main_eb_bgcolor, on_click=self.activate_submit_btn_clicked)
        # self.buy_btn = ft.ElevatedButton(text="Buy", color="black", bgcolor=ft.colors.GREEN_400, width=extras.main_eb_width, on_click=self.on_buy_click)
        # self.btn_row = ft.Row([self.buy_btn, self.submit_btn], width=390,  alignment=ft.MainAxisAlignment.SPACE_AROUND)
        self.btn_row = ft.Row([self.submit_btn], width=390,  alignment=ft.MainAxisAlignment.CENTER)
        self.body_container = ft.Container(ft.Column([self.software_activation_text_container, self.key_tf, self.btn_row], spacing=20), padding=20, border_radius=10, border=ft.border.all(1, "grey"))

# all controls added to page
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(expand=True),  # This will push the body_container to the middle
                        self.body_container,
                        ft.Container(expand=True),  # This will push the body_container to the middle
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                expand=True
            )
        ]
        
# open the tab in browser, for puchase the activation key
    # def on_buy_click(self, e):
    #     try:
    #         url = f"https://modal-key.onrender.com/?name={self.session_value[0]}&contact={self.session_value[1]}&address={self.session_value[4]}&soft_type=LMS&duration=365 Days"
    #         webbrowser.open(url)
    #     except Exception:
    #         None


# generate the system hash for software activation
    def get_sys_hash(self):
        result = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'], capture_output=True, text=True)
        uuid = result.stdout.strip().split('\n')[-1].strip()
        hash = hashlib.sha256(uuid.encode()).hexdigest()
        return hash

# handles the software activation process
    def activate_submit_btn_clicked(self, e):
        # return
        if self.key_tf.value != "" and len(self.key_tf.value) == 28:
            key = self.key_tf.value
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
                        connection = mysql.connector.connect(
                            host = cred.host,
                            user = cred.user,
                            password = cred.password,
                            database = cred.database
                        )
                        cursor = connection.cursor()

                        soft_reg_sql = "update soft_reg set valid_till=%s where bus_contact=%s AND bus_password=aes_encrypt(%s, %s) AND sys_hash=%s"
                        soft_reg_value = (valid_till, self.session_value[1], self.session_value[2], cred.encrypt_key, sys_hash)
                        cursor.execute(soft_reg_sql, soft_reg_value)

                        act_key_sql = "insert into act_key (soft_reg_contact, act_key, valid_till, sys_hash) values (%s, %s, %s, %s)"
                        act_key_value = (self.session_value[1], key, valid_till, sys_hash)
                        cursor.execute(act_key_sql, act_key_value)

                        connection.commit()
                        cursor.close()
                        connection.close()


                        con = sqlite3.connect(os.path.join(os.getenv('LOCALAPPDATA'), "Programs", "modal", "config", cred.auth_db_name))
                        cur = con.cursor()
                        soft_reg_sql = "update soft_reg set valid_till=? where bus_contact=? AND bus_password=? AND sys_hash=?"
                        soft_reg_value = (valid_till, self.session_value[1], self.session_value[2], sys_hash)
                        cur.execute(soft_reg_sql, soft_reg_value)
                        con.commit()

                        act_key_sql = "insert into act_key (soft_reg_contact, act_key, valid_till, sys_hash) values (?, ?, ?, ?)"
                        act_key_value = (self.session_value[1], key, valid_till, sys_hash)
                        cur.execute(act_key_sql, act_key_value)

                        con.commit()
                        cur.close()
                        con.close()


                        self.dlg_modal.title = extras.dlg_title_done
                        self.dlg_modal.actions=[ft.TextButton("Okay!", on_click=self.activation_done , autofocus=True)]
                        self.dlg_modal.content = ft.Text("Activation Completed.\nPlease Login Again.")
                        self.page.open(self.dlg_modal)

                    except Exception:
                        pass

            except Exception:
                pass
            finally:
                self.key_tf.value = ""                
        else:
            self.key_tf.value = ""    
        self.update()

    def activation_done(self, e):
        self.page.close(self.dlg_modal)
        self.page.go("/login")