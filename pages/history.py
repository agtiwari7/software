import flet as ft

class History(ft.Column):
    def __init__(self, page, session_value):
        super().__init__()
        self.session_value = session_value
        self.page = page

        self.tabs = ft.Tabs(
                    animation_duration=300,
                    on_change=self.on_tab_change,
                    tab_alignment=ft.TabAlignment.START_OFFSET,
                    expand=True,
                    selected_index=1,
                    tabs=[
                        ft.Tab(
                            text="Admission",
                            content=ft.Text("admission history tab")
                        ),
                        ft.Tab(
                            text="Fees Pay",
                            content=ft.Text("fees pay history tab")
                        ),
                        ft.Tab(
                            text="Deleted Student",
                            content=ft.Text("deleted student history tab")
                        ),

                    ],
                )

        self.controls = [self.tabs]

    def on_tab_change(self, e):
        if e.control.selected_index == 0:
            pass
        elif e.control.selected_index == 1:
            pass
        elif e.control.selected_index == 2:
            pass







        self.controls = [ft.Text("Dashboard page")]