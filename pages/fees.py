import flet as ft
import sqlite3

class Fees(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page

        self.search_tf = ft.TextField(label="Name / Contact / Aadhar / Fees / Joining / Shift", capitalization=ft.TextCapitalization.WORDS, width=500)
        self.search_btn = ft.ElevatedButton("Search", on_click=self.fetch_data)
        self.text = ft.Text()

        self.controls = [ft.Row([self.search_tf,self.search_btn]),  self.text]

    def fetch_data(self, e):
        con = sqlite3.connect("software.db")
        cur = con.cursor()

        sql = "select * from users where name=? or contact=? or aadhar=? or fees=? or joining=? or shift=? or seat=?"
        value = (self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value, self.search_tf.value)

        res = cur.execute(sql, value)

        data = ""
        for row in res.fetchall():
            print(row)
            data = f"{row}\n"+data
        self.text.value = data
        con.close()
        self.update()








        