import flet as ft

class Admission(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page

        self.dlg_modal = ft.AlertDialog(
            modal=True,
            actions=[
                ft.TextButton("Okey!", on_click=lambda e: self.page.close(self.dlg_modal), autofocus=True),
            ],
            title=ft.Text("Done!"),
            content=ft.Text("everything is working fine"),
            actions_alignment=ft.MainAxisAlignment.END, surface_tint_color=ft.colors.LIGHT_BLUE_ACCENT_700)
        
        name_field = ft.TextField(label="Name")
        contact_field = ft.TextField(label="Contact")
        submit_btn = ft.ElevatedButton("Submit", on_click=lambda _: self.page.open(self.dlg_modal))

        self.controls = [name_field, contact_field, submit_btn]