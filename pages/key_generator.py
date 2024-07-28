import flet as ft
import base64
import datetime

def main(page: ft.Page):
    page.title = "Key Generator"
    # page.theme_mode = "light"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.appbar = ft.AppBar()

    def generate_btn_clicked(e):
        if dd_menu.value is not None:
            if dd_menu.value == "7 Days":
                days = "007"
            elif dd_menu.value == "3 Months":
                days = f"0{3*30}"
            elif dd_menu.value == "6 Months":
                days = f"{6*30}"
            elif dd_menu.value == "12 Months":
                days = f"{12*30}"
            
            time_stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")    # %S for seconds
            key_format = f"KEY-{time_stamp}-{days}"

            binary = key_format.encode("utf-8")
            b64encode = base64.b64encode(binary).decode("utf-8")
            str_1 = b64encode.replace("=", "")
            str_2 = str_1.swapcase()
            key = str_2[::-1]
            key_text_box.value = key
            page.update()

    title = ft.Row(controls=[ft.Text("Key Generator", size=30, weight=ft.FontWeight.BOLD)],alignment=ft.MainAxisAlignment.CENTER)
    divider = ft.Divider(height=1, thickness=3, color=ft.colors.LIGHT_BLUE_ACCENT_700)
    duration_txt = ft.Text(value="Duration:", size=20, weight=ft.FontWeight.W_500)
    dd_menu = ft.Dropdown(
        options=[
            ft.dropdown.Option("7 Days"),
            ft.dropdown.Option("6 Months"),
            ft.dropdown.Option("12 Months"),
        ],
        width=330,
        )
    duretion_menu_row = ft.Row(controls=[duration_txt, dd_menu],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    key_text = ft.Text(value="KEY:", size=20, weight=ft.FontWeight.W_500)
    key_text_box = ft.TextField(read_only=True, width=330)
    key_row = ft.Row(controls=[key_text, key_text_box], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    generate_btn = ft.ElevatedButton(text="GENERATE", color="Black", bgcolor=ft.colors.GREY_400, on_click=generate_btn_clicked, width=150, height=50)

    container_1 = ft.Container(content=
                                ft.Column(controls=
                                        [duretion_menu_row]), padding=10, margin=15)
    
    container_2 = ft.Container(content=
                            ft.Column(controls=
                                    [key_row]), padding=10, margin=15)
    container_3 = ft.Container(content=
                            ft.Row(controls=
                                    [generate_btn], alignment=ft.MainAxisAlignment.CENTER), padding=10,)

    main_container = ft.Container(content=
                                    ft.Column(controls=
                                                [title, divider, container_1, container_2, container_3]),
                                                padding=15,
                                                border_radius=15, 
                                                bgcolor="#44CCCCCC", 
                                                border=ft.border.all(2, ft.colors.BLACK),
                                                width=530,
                                                margin=15
                                                )

    page.add(main_container)
    page.update()
ft.app(target=main)