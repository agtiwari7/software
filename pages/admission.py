import flet as ft
import os
import utils.cred as cred

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
        self.page.overlay.append(self.file_picker)

        self.img = ft.Image(src="/images/user.jpg", height=150, width=150)
        self.choose_photo_btn = ft.ElevatedButton("Choose Photo", color="Black", bgcolor=ft.colors.GREY_400, on_click=lambda _: self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "png", "jpeg"]))

        name_row = ft.Row([ft.Text("Name:", size=16, weight=ft.FontWeight.W_500), ft.TextField(max_length=30)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        contact_row = ft.Row([ft.Text("Contact:", size=16, weight=ft.FontWeight.W_500), ft.TextField(prefix_text="+91 ", max_length=10,)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        aadhar_row = ft.Row([ft.Text("Aadhar:", size=16, weight=ft.FontWeight.W_500), ft.TextField( max_length=12)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        fees_row = ft.Row([ft.Text("Fees:", size=16, weight=ft.FontWeight.W_500), ft.TextField()], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        timing_row = ft.Row([ft.Text("Timing:", size=16, weight=ft.FontWeight.W_500), ft.TextField()], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        shift_row = ft.Row([ft.Text("Shift:", size=16, weight=ft.FontWeight.W_500), ft.TextField()], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        seat_row = ft.Row([ft.Text("Seat:", size=16, weight=ft.FontWeight.W_500), ft.TextField()], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        joining_date_row = ft.Row([ft.Text("Joining:", size=16, weight=ft.FontWeight.W_500), ft.TextField()], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        submit_btn = ft.ElevatedButton("Submit", color="Black", width=100, bgcolor=ft.colors.GREY_400, on_click=lambda _: self.page.open(self.dlg_modal))


        container_1 = ft.Container(content=ft.Column(controls=[self.img, ft.Container(self.choose_photo_btn, margin=20)],width=400, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        container_2 = ft.Container(content=ft.Column(controls=[name_row, contact_row, aadhar_row], horizontal_alignment=ft.CrossAxisAlignment.CENTER ), padding=10, width=400)
        self.divider = ft.Divider(height=1, thickness=3, color=ft.colors.LIGHT_BLUE_ACCENT_700)
        container_3 = ft.Container(content=ft.Column(controls=[fees_row, timing_row, shift_row], horizontal_alignment=ft.CrossAxisAlignment.CENTER,), padding=10, width=400)
        container_4 = ft.Container(content=ft.Column(controls=[seat_row, joining_date_row, ft.Container(submit_btn, margin=20)], horizontal_alignment=ft.CrossAxisAlignment.CENTER,), padding=10, width=400)

        self.main_container = ft.Container(content=ft.Column(controls=[
            ft.Row([container_1, container_2], alignment=ft.MainAxisAlignment.END),
            self.divider,
            ft.Row([container_3, container_4])]),
        width=870,
        margin=50,
        padding=30,
        
        border_radius=15, bgcolor="#44CCCCCC", border=ft.border.all(2, ft.colors.BLACK)
        )

        self.controls = [self.main_container]
    
    def on_file_picker_result(self, e):
        if e.files:
            selected_file = e.files[0]
            file_path_with_name = selected_file.path
            if os.name == 'nt':  # Check if the operating system is Windows
                file_path_with_name = file_path_with_name.replace('\\', '/')
            self.img.src = file_path_with_name
            self.update()