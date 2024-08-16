import os 
import sqlite3

path = os.path.join(os.getenv('LOCALAPPDATA'), "Programs", "modal", "config")
os.makedirs(path, exist_ok=True)
os.chdir(path)

con = sqlite3.connect("modal.db")
cur = con.cursor()

cur.execute("create table if not exists soft_reg (bus_name varchar(30), bus_contact bigint unique, bus_password varchar(30), valid_till varchar(15), sys_hash varchar(100));")
cur.execute("create table if not exists act_key (soft_reg_contact bigint, act_key varchar(50) unique, valid_till varchar(15), sys_hash varchar(100), FOREIGN KEY (soft_reg_contact) REFERENCES soft_reg(bus_contact));")
con.commit()

res = cur.execute("select * from soft_reg")
for row in res.fetchall():
    print(row)

res = cur.execute("select * from act_key")
for row in res.fetchall():
    print(row)

con.close()
