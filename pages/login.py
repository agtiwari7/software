import flet as ft
import mysql.connector
import utils.cred as cred
import requests
import time

class Login(ft.Column):
    def __init__(self, page, view):
        super().__init__()
        # Adding the title
        self.title = ft.Row(controls=[ft.Text("Welcome", size=30, weight=ft.FontWeight.BOLD)],alignment=ft.MainAxisAlignment.CENTER)
        self.width = 400
        self.page = page
        self.view = view

        # create a horizontal divider and show them after app bar
        self.divider = ft.Divider(height=1, thickness=3, color=ft.colors.LIGHT_BLUE_ACCENT_700)

        # dialogue box method
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okey!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)
        
        self.contact_field = ft.TextField(label="Contact", on_change = self.validate, prefix_text="+91 ", max_length=10, prefix_icon=ft.icons.CONTACT_PAGE,input_filter=ft.InputFilter(regex_string=r"[0-9]"), on_submit=lambda e: self.password_field.focus())
        self.password_field = ft.TextField(label="Password",password=True, can_reveal_password=True, on_change = self.validate, max_length=12, prefix_icon=ft.icons.PASSWORD, on_submit=self.login_btn_clicked)
        self.login_btn = ft.ElevatedButton(text="Login", width=100, color="Black", bgcolor=ft.colors.GREY_400, on_click=self.login_btn_clicked)
        self.registration_page_text = ft.Text("Don't have an account?")
        self.registration_page_btn = ft.TextButton("Register", on_click=lambda _:self.page.go(self.view))
        # create a container, which contains a column, and column contains "name_field, contact_field, password_field, key_field, note".
        self.container_1 = ft.Container(content=
                                ft.Column(controls=
                                        [self.contact_field, self.password_field]), padding=10)
    

        # adding the STATUS text, internet icon and status text which contains value (online or offline)
        self.status_text = ft.Text("STATUS: ", weight=ft.FontWeight.BOLD)
        self.internet_icon = ft.CircleAvatar(radius=7)
        self.status = ft.Text(size=15)
        # wrapping the STATUS text, internet icon and status text inside a row, called status_row
        self.status_row = ft.Row(controls=[self.status_text, self.internet_icon, self.status])
        # self.status_row = ft.Text("hello")

        # create another container, which contains a row, and row contains "status_row and submit_button".
        # self.container_2 = ft.Container(content=
        #                         ft.Row(controls=
        #                                 [self.status_row, self.submit_btn],
        #                                 alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        #                                 padding=10)
        # run thread for check the internet connection
        self.page.run_thread(handler=self.check_internet_connection)



        self.container_2 = ft.Container(content=
                            ft.Row(controls=
                                    [self.status_row, self.login_btn],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    padding=15)

        self.container_3 = ft.Container(content=
                            ft.Row(controls=
                                    [self.registration_page_text, self.registration_page_btn],
                                    alignment=ft.MainAxisAlignment.CENTER), padding=7)

        # main container, which contains all properties and other containers also.
        self.main_container = ft.Container(content=
                                           ft.Column(controls=
                                                     [self.title, self.divider, self.container_1, self.container_2, self.container_3]),
                                                     padding=15, border_radius=15, bgcolor="#44CCCCCC", border=ft.border.all(2, ft.colors.BLACK))

        # main controls of this calss, which contains everything together
        self.controls = [self.main_container]

    # validate the input values, if any value is null then disable the login button.
    def validate(self, e):
        if all([self.contact_field.value, self.password_field.value]):
            self.login_btn.disabled = False
        else:
            self.login_btn.disabled = True
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

    # again validate the value and their length also, if failed then open alert dialogue box with error text,
    # otherwise fetch and print the input values and show the alert dialogue box with successfull parameters.
    def login_btn_clicked(self, e):
        if not all([self.contact_field.value, self.password_field.value, len(self.contact_field.value)>=10]):
            self.dlg_modal.title = ft.Text("Error!")
            self.dlg_modal.content = ft.Text("Provide all the details properly.")
            self.page.open(self.dlg_modal)
        else:
            contact = self.contact_field.value
            password = self.password_field.value
            # print(contact, password)
            try:
                if self.login_validate(contact, password):
                    self.page.session.set(key=cred.login_session_key ,value=self.session_value)
                    self.page.go("/dashboard")
                else:
                    self.dlg_modal.title = ft.Text("Error!")
                    self.dlg_modal.content = ft.Text("Details are incorrect.")
                    self.page.open(self.dlg_modal)
            except Exception as e:
                self.dlg_modal.title = ft.Text("Error!")
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)

    def login_validate(self, contact, password):
        # local system's mysql server connect with local server details
        db = mysql.connector.connect(
            host = cred.l_host,
            user = cred.l_user,
            password = cred.l_password,
            database = cred.l_database
        )

        sql = "select bus_name, bus_contact, aes_decrypt(bus_password, %s), valid_till from soft_reg where bus_contact=%s"
        value = (cred.encrypt_key, contact)

        db_cursor = db.cursor()
        db_cursor.execute(sql, value)
        try:
            result = db_cursor.fetchone()
            if result[2].decode() == password:
                # bus_name, bus_contact, bus_password, valid_till
                self.session_value = [result[0], result[1], result[2].decode(), result[3]]
                return True
            else:
                return False
        except Exception:
                self.dlg_modal.title = ft.Text("Error!")
                self.dlg_modal.content = ft.Text("Details are incorrect.")
                self.page.open(self.dlg_modal)
