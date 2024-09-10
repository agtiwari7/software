import os
import re
import sys
import json
import sqlite3
import tempfile
import flet as ft
from PIL import Image
from utils import extras
from pages.camera import CameraWindow
from pages.dashboard import Dashboard
from PyQt5.QtWidgets import QApplication
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Admission(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.page = page
        self.session_value = session_value

        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okay!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)

# one-by-one tab's elements
        self.file_picker = ft.FilePicker(on_result=self.on_file_picker_result)
        self.base_path = os.path.join(os.getenv('LOCALAPPDATA'), "Programs", "modal", "config")
        self.img = ft.Image(src=f"{self.base_path}/template/user.png", height=150, width=150)
        self.gallery_btn = ft.ElevatedButton("Gallery", color=extras.secondary_eb_color, bgcolor=extras.secondary_eb_bgcolor, on_click=lambda _: self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "png", "jpeg"]))
        self.camera_btn = ft.ElevatedButton("Camera", color=extras.secondary_eb_color, bgcolor=extras.secondary_eb_bgcolor, on_click=self.open_camera_window)
        
        self.name_field = ft.TextField(label="Name", max_length=30, on_submit=lambda _: self.father_name_field.focus(), capitalization=ft.TextCapitalization.WORDS, width=315, label_style=extras.label_style)
        self.father_name_field = ft.TextField(label="Father Name", prefix_text="Mr. ", max_length=30, on_submit=lambda _: self.contact_field.focus(), capitalization=ft.TextCapitalization.WORDS, width=315, label_style=extras.label_style)
        self.contact_field = ft.TextField(label="Contact", prefix_text="+91 ", max_length=10, on_submit=lambda _: self.aadhar_field.focus(), input_filter=ft.InputFilter(regex_string=r"[0-9]"), width=315, label_style=extras.label_style)
        self.aadhar_field = ft.TextField(label="Aadhar", max_length=14, on_submit=lambda _: self.address_field.focus(), input_filter=ft.InputFilter(regex_string=r"[0-9]"), width=315, on_change=self.format_aadhaar_number, label_style=extras.label_style)
        self.address_field = ft.TextField(label="Address", max_length=60, capitalization=ft.TextCapitalization.WORDS, width=430, label_style=extras.label_style)
        self.gender = ft.RadioGroup(content=ft.Row([
                                                    ft.Radio(value="Male", label="Male", label_position=ft.LabelPosition.LEFT, label_style=ft.TextStyle(size=18, weight="bold"), active_color=ft.colors.LIGHT_BLUE_ACCENT_700),
                                                    ft.Radio(value="Female", label="Female", label_position=ft.LabelPosition.LEFT, label_style=ft.TextStyle(size=18, weight="bold"), active_color=ft.colors.LIGHT_BLUE_ACCENT_700),
                                                    ]))

        name_father_name_row = ft.Row([self.name_field, self.father_name_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        contact_aadhar_row = ft.Row([self.contact_field, self.aadhar_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        address_gender_row = ft.Row([self.address_field, self.gender], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        with open(f'{self.session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)

        self.shift_options = config["shifts"]
        self.seats_options = config["seats"]
        self.fees_options = config["fees"]

        self.shift_dd = ft.Dropdown(
            label="Shift",
            width=220,
            options=[ft.dropdown.Option(shift) for shift in self.shift_options],
            label_style=extras.label_style,
            on_change=self.shift_dd_change)
        
        self.timing_dd = ft.Dropdown(
            label="Timing",
            width=220,
            label_style=extras.label_style,
            on_change=self.timing_dd_change)
        
        self.start_tf = ft.TextField(label="Start", width=50, label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.start_dd = ft.Dropdown(label="AM/PM", width=50, options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.end_tf = ft.TextField(label="End", width=50, label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.end_dd = ft.Dropdown(label="AM/PM", width=50, options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], label_style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_ACCENT_400, size=10))
        self.timing_container = ft.Container(content=ft.Row([self.start_tf, self.start_dd, self.end_tf, self.end_dd], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), width=220, height=50 , visible=False, border=ft.border.all(1, ft.colors.BLACK), border_radius=5)
        
        self.seat_btn_text = ft.Text("Select Seat", size=16)
        self.seat_btn = ft.OutlinedButton(content=self.seat_btn_text, width=220, height=50, on_click=self.fetch_seat, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)))
        
        self.fees_options.append("Custom")
        self.fees_tf = ft.TextField(label="Fees", visible=False, input_filter=ft.InputFilter(regex_string=r"[0-9]"), prefix=ft.Text("Rs. "), autofocus=True, width=220, label_style=extras.label_style)
        self.fees_dd = ft.Dropdown(on_change=self.fees_dd_changed,
            label="Fees",
            width=220,
            options=[ft.dropdown.Option(str(fee)) for fee in self.fees_options],
            label_style=extras.label_style)
        
        fees_row = ft.Row([self.fees_dd, self.fees_tf], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.joining_tf = ft.TextField(label="Joining (dd-mm-yyyy)", value=datetime.today().strftime('%d-%m-%Y'), width=220, label_style=extras.label_style, on_change=self.joining_tf_change)
        self.fees_pay_tf = ft.TextField(label="Fees Pay Till (dd-mm-yyyy)", value=(datetime.strptime(self.joining_tf.value, "%d-%m-%Y") + relativedelta(months=1)).strftime("%d-%m-%Y"), width=220, label_style=extras.label_style, read_only=True)
        # self.enrollment_tf = ft.TextField(label="Enrollment No.", width=345, label_style=extras.label_style)
        self.enrollment_tf = ft.TextField(label="Enrollment No.", width=220, value=self.get_enrollment(), label_style=extras.label_style)
        self.submit_btn = ft.ElevatedButton("Submit", width=extras.main_eb_width, color=extras.main_eb_color, bgcolor=extras.main_eb_bgcolor, on_click=self.submit_btn_clicked)

        container_1 = ft.Container(content=ft.Column(controls=[self.img, ft.Container(ft.Row(controls=[self.gallery_btn, self.camera_btn], alignment=ft.MainAxisAlignment.CENTER),margin=15)],width=300, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        container_2 = ft.Container(content=ft.Column(controls=[name_father_name_row, contact_aadhar_row, address_gender_row], horizontal_alignment=ft.CrossAxisAlignment.CENTER ), padding=10, expand=True)
        self.divider = ft.Divider(height=1, thickness=3, color=extras.divider_color)
        container_3 = ft.Container(content=ft.Row(controls=[self.shift_dd, self.timing_dd, self.timing_container, self.seat_btn, fees_row], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=10)
        container_4 = ft.Container(content=ft.Row(controls=[ft.Container(content=ft.Row(controls=[self.joining_tf, self.fees_pay_tf, self.enrollment_tf], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), width=720),
                                                            ft.Container(content=ft.Row(controls=[self.submit_btn], alignment=ft.MainAxisAlignment.CENTER), margin=10, expand=True)
                                                            ]), padding=10)

        self.main_container = ft.Container(content=ft.Column(controls=[
                                                                    ft.Row([container_1, container_2]),
                                                                    self.divider,
                                                                    container_3, container_4]
                                                            ),margin=50, padding=30, width=1050,
                                                            border=extras.main_container_border,
                                                            border_radius=extras.main_container_border_radius, 
                                                            bgcolor=extras.main_container_bgcolor)
    
# main tab property, which contains all tabs
        self.tabs = ft.Tabs(
                    animation_duration=300,
                    on_change=self.on_tab_change,
                    tab_alignment=ft.TabAlignment.START_OFFSET,
                    expand=True,
                    selected_index=1,
                    tabs=[
                        # ft.Tab(
                        #     text="Bulk(s)",
                        #     content=ft.Container(ft.Column([ft.Text("Coming Soon.", size=26, weight=ft.FontWeight.BOLD)],
                        #                                     horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        #                                     ))
                        # ),
                        ft.Tab(
                            text="One-by-One",
                            content=ft.Container(ft.Column([self.file_picker, self.main_container], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
                        ),
                    ],
                )
        
# main tab added to page
        self.controls = [self.tabs]

# triggered when joining dropdown changes, means when user change the joining date.
    def joining_tf_change(self, e):
        if re.match(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$', self.joining_tf.value):
            self.fees_pay_tf.value = (datetime.strptime(self.joining_tf.value, "%d-%m-%Y") + relativedelta(months=1)).strftime("%d-%m-%Y")
            self.fees_pay_tf.update()

# triggered when shift dropdown changes, means when user select a shift.
    def shift_dd_change(self, e):
        self.timing_dd.value = None
        self.start_tf.value = ""
        self.start_dd.value = None
        self.end_tf.value = ""
        self.end_dd.value = None
        self.timing_dd.options=[ft.dropdown.Option(timing) for timing in self.shift_options[self.shift_dd.value]]
        self.timing_dd.options.append(ft.dropdown.Option("Custom"))
        self.timing_container.visible = False
        self.timing_container.update()
        self.timing_dd.visible=True
        self.timing_dd.update()
        
# triggered when timing dropdown changes, means when user select a timing
    def timing_dd_change(self, e):
        if self.timing_dd.value == "Custom":
            self.timing_dd.focus()
            self.timing_dd.visible = False
            self.timing_dd.update()
            self.timing_container.visible = True
            self.timing_container.update()       

# triggerd when tab changes
    def on_tab_change(self, e):
        if e.control.selected_index == 0:
            pass
        elif e.control.selected_index == 1:
            pass
    
# add - after and each 4 digits of aadhar no.
    def format_aadhaar_number(self, e):
        text = e.control.value.replace("-", "")  # Remove existing hyphens
        if len(text) > 12:  # Limit the input to 12 digits
            text = text[:12]
        formatted_text = '-'.join([text[i:i+4] for i in range(0, len(text), 4)])
        e.control.value = formatted_text
        e.control.update()
    
# used to open the camera window for capute the image using camera
    def open_camera_window(self, e):
        app = QApplication(sys.argv)
        camera_window = CameraWindow()
        camera_window.show()
        app.exec()
        try:
            self.img.src = camera_window.captured_filename
        except Exception:
            self.img.src = f"{self.base_path}/template/user.png"
        finally:
            self.img.update()
    
# in behalf of shift and timing, fetch available seats from database. And show them using alert dialogue box
    def fetch_seat(self, e):

        # it check for conflict timing between new time and olds
        def has_conflict(existing_range, new_student_timing):
            new_start, new_end = new_student_timing.split(" - ")
            existing_start, existing_end = existing_range.split(" - ")
            try:
                existing_start = datetime.strptime(existing_start.strip(), '%I:%M %p')
                existing_end = datetime.strptime(existing_end.strip(), '%I:%M %p')
                new_start = datetime.strptime(new_start.strip(), '%I:%M %p')
                new_end = datetime.strptime(new_end.strip(), '%I:%M %p')
            except ValueError:
                print("Error in time format")
                return False

            # Adjust for overnight shifts
            if existing_end <= existing_start:
                existing_end += timedelta(days=1)
            if new_end <= new_start:
                new_end += timedelta(days=1)

            # Overlap detection
            return not (new_end <= existing_start or new_start >= existing_end)

        # used to change the color of seat button, when seat is selected
        def seat_selected(event):
            self.seat_btn_text.value = f"Seat: {event.control.data}"
            self.seat_btn_text.color = ft.colors.LIGHT_GREEN_ACCENT_400
            self.page.close(self.dlg_modal)
            self.fees_dd.focus()
            self.update()

        # start the main fetch_seat function.
        if not all([self.shift_dd.value, self.timing_dd.value]):
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Please select Shift and Timing.")
            self.page.open(self.dlg_modal)
            self.update()

        elif self.timing_dd.value == "Custom" and not all([self.start_tf.value, self.start_dd.value, self.end_tf.value, self.end_dd.value]):
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Please select Shift and Timing.")
            self.page.open(self.dlg_modal)
            self.update()
        
        else:
            try:
                
                con = sqlite3.connect(f"{self.session_value[1]}.db")
                cursor = con.cursor()
                cursor.execute(f"select seat, timing from users_{self.session_value[1]}")
                reserved_seats = cursor.fetchall()

                if self.timing_dd.value == "Custom":
                    start_time = datetime.strptime(f"{self.start_tf.value} {self.start_dd.value}", "%I %p").strftime("%I:%M %p")
                    end_time = datetime.strptime(f"{self.end_tf.value} {self.end_dd.value}", "%I %p").strftime("%I:%M %p")
                    new_student_timing = f"{start_time} - {end_time}"
                else:
                    new_student_timing = self.timing_dd.value

                self.available_seats = self.seats_options.copy()
                for seat, existing_range in reserved_seats:
                    if has_conflict(existing_range, new_student_timing):
                        if seat in self.available_seats:
                            self.available_seats.remove(seat)
                self.available_seats.append("Random")
                
                # ListView with ListTiles for seat selection
                list_view = ft.ListView(
                    expand=True,
                    height=200,
                    controls=[
                        ft.ListTile(
                            title=ft.Text(seat),
                            data=seat,
                            on_click=seat_selected
                        ) for seat in self.available_seats
                    ],
                    spacing=5,
                )

                self.dlg_modal.title = ft.Text("Available Seats", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400)
                self.dlg_modal.actions=[ft.TextButton("Close", on_click=lambda e: self.page.close(self.dlg_modal))]
                self.dlg_modal.content = list_view
                self.page.open(self.dlg_modal)

            except Exception as e:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)
            finally:
                con.close()
                self.update()

# set image path is equal to choosen photo from file picker dialogue box.
    def on_file_picker_result(self, e):
        if e.files:
            selected_file = e.files[0]
            file_path = selected_file.path
            self.img.src = file_path
            self.update()

# call when fees dropdown's on_change event triggerd.  
    def fees_dd_changed(self, e):
        if self.fees_dd.value == "Custom":
            self.fees_dd.visible = False
            self.fees_tf.visible = True
            self.fees_tf.focus()
        else:
            self.submit_btn.focus()
        self.update()
    
# save photo named as aadhar no, below 150kb and return the path of saved photo
    def save_photo(self, aadhar, target_size_kb=150, quality=85):
        # Create the folder hierarchy if it doesn't exist
        target_folder = os.path.join(os.getcwd(), "photo", "current")
        os.makedirs(target_folder, exist_ok=True)

        input_image = self.img.src
        base_file_name = os.path.basename(input_image)
        _ , file_extension = os.path.splitext(base_file_name)
        file_name = f"{aadhar}{file_extension}"

        # Define the target file path and Copy the file to the target folder
        output_image = f"{target_folder}/{file_name}"

        # Image resizer and compressor process start from here #############################################
        target_size_bytes = target_size_kb * 1024           # Target size in bytes
        
        # Get the size of the input image
        original_size = os.path.getsize(input_image)
        
        # Image ko open karein
        with Image.open(input_image) as img:
            # Agar image PNG format me hai, to usko JPEG me convert karein
            if img.format == 'PNG':
                img = img.convert('RGB')
                output_image = output_image.rsplit('.', 1)[0] + ".jpg"

            # original image ka size 150kb ya usse kam hone pr direct save hogi
            if original_size <= target_size_bytes:
                
                img.save(output_image, "JPEG", quality=quality)
                return output_image
            
            # Initial resize factor
            resize_factor = 1.0
            
            # Resize aur compress process ko repeat karein jab tak desired size achieve na ho
            while True:
                # Current size ka estimation
                estimated_size = os.path.getsize(input_image) * (resize_factor ** 2) * (quality / 100)
                
                # Agar estimated size target se chhota hai to break karein
                if estimated_size <= target_size_bytes:
                    break
                
                # Resize factor ko kam karein (resize_factor < 1.0 means reduction in size)
                resize_factor -= 0.1
                new_size = (int(img.width * resize_factor), int(img.height * resize_factor))
                
                # Naye attribute LANCZOS ka use karein for resizing
                resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Image ko compress karein aur save karein
                resized_img.save(output_image, "JPEG", quality=quality)
                
                # Agar actual file size target se kam hai, to loop break karein
                if os.path.getsize(output_image) <= target_size_bytes:
                    break

        for name in os.listdir(tempfile.gettempdir()):
            if "modal" in name and ".png" in name:
                temp_file_name = os.path.join(tempfile.gettempdir(), name)
                os.remove(temp_file_name)

        return output_image

# fetch next id and generate enrollment no using id.
    def get_enrollment(self):
        try:
            con = sqlite3.connect(f"{self.session_value[1]}.db")
            cur = con.cursor()
            cur.execute(f"SELECT seq FROM sqlite_sequence WHERE name='users_{self.session_value[1]}'")
            
            # Fetch the current sequence value
            result = cur.fetchone()
            if result:
                next_id = result[0] + 1
            else:
                next_id = 1

            # Extract the first character of each word in the bus_name name
            initials = ''.join([word[0] for word in self.session_value[0].split()])
            
            current_year = datetime.now().year
            enrollment = f"{initials}{current_year}{next_id}"
            return enrollment
        
        except Exception as e:
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text(e)
            self.page.open(self.dlg_modal)
        finally:
            con.close()
            self.update()

# validate the values and  pass it to sqlite_server.
    def submit_btn_clicked(self, e):
    # save data into sqlite database
        def sqlite_server():
            try:
                today_date = datetime.today().strftime('%d-%m-%Y')

                con = sqlite3.connect(f"{self.session_value[1]}.db")
                cur = con.cursor()
                sql = f"insert into users_{self.session_value[1]} (name, father_name, contact, aadhar, address, gender, shift, timing, seat, fees, joining, enrollment, payed_till, img_src) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                value = (name, father_name, contact, aadhar, address, gender, shift, timing, seat, fees, joining, enrollment, payed_till, img_src)
                cur.execute(sql, value)

                history_sql = f"insert into history_users_{self.session_value[1]} (date, name, father_name, contact, gender, enrollment, fees) values (?, ?, ?, ?, ?, ?, ?)"
                histroy_value = (today_date, name, father_name, contact, gender, enrollment, fees)
                cur.execute(history_sql, histroy_value)

                history_sql = f"insert into history_fees_users_{self.session_value[1]} (date, name, father_name, contact, gender, enrollment, amount, payed_from, payed_till) values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                histroy_value = (today_date, name, father_name, contact, gender, enrollment, fees, joining, payed_till)
                cur.execute(history_sql, histroy_value)


                con.commit()
                cur.close()
                con.close()

                self.dlg_modal.title = extras.dlg_title_done
                self.dlg_modal.content = ft.Text("Admission process is completed.")
                self.page.open(self.dlg_modal)
                self.dlg_modal.on_dismiss = self.go_to_dashboard

            except sqlite3.IntegrityError:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text("Aadhar is already registerd.")
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
                self.update()

        if not all([self.name_field.value, self.father_name_field.value, self.contact_field.value, self.aadhar_field.value, self.address_field.value, self.gender.value,
                    self.shift_dd.value, self.timing_dd.value, self.seat_btn_text.value != "Select Seat", self.fees_dd.value,
                    re.match(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$', self.joining_tf.value), self.enrollment_tf.value,
                    len(str(self.contact_field.value))==10, len(str(self.aadhar_field.value))==14,
                    ]):
            self.dlg_modal.title = extras.dlg_title_error
            self.dlg_modal.content = ft.Text("Provide all the details properly.")
            self.page.open(self.dlg_modal)
            self.update()
        else:
            name = self.name_field.value.strip()
            father_name = self.father_name_field.value.strip()
            contact = self.contact_field.value.strip()
            aadhar = self.aadhar_field.value.strip()
            address = self.address_field.value.strip()
            gender = self.gender.value.strip()
            shift = self.shift_dd.value.strip()

            if self.timing_dd.value == "Custom":
                start_time = datetime.strptime(f"{self.start_tf.value} {self.start_dd.value}", "%I %p").strftime("%I:%M %p")
                end_time = datetime.strptime(f"{self.end_tf.value} {self.end_dd.value}", "%I %p").strftime("%I:%M %p")
                timing = f"{start_time} - {end_time}".strip()
            else:
                timing = self.timing_dd.value.strip()

            seat = self.seat_btn_text.value.replace("Seat: ", "").strip()
            if self.fees_dd.value == "Custom":
                fees = self.fees_tf.value.strip()
            else:
                fees = self.fees_dd.value.strip()
            joining = self.joining_tf.value.strip()
            payed_till = self.fees_pay_tf.value.strip()
            enrollment = self.enrollment_tf.value.strip()
            img_src = self.save_photo(aadhar)
            try:
                
                sqlite_server()
            except Exception as e:
                self.dlg_modal.title = extras.dlg_title_error
                self.dlg_modal.content = ft.Text(e)
                self.page.open(self.dlg_modal)
            finally:
                self.update()
    
# after successfully data saved in server, then go to dashboard page.
    def go_to_dashboard(self, e):
        last_view = self.page.views[-1]
        last_view.controls.clear()
        last_view.controls.append(Dashboard(self.page, self.session_value))
        self.page.update()