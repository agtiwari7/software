import mysql.connector
from utils import cred

connection = mysql.connector.connect(
    host = cred.host,
    user = cred.user,
    password = cred.password,
    database = cred.database
)
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS soft_reg (bus_name VARCHAR(30), bus_contact BIGINT UNIQUE, bus_password VARBINARY(255), valid_till VARCHAR(15));")
cursor.execute("CREATE TABLE IF NOT EXISTS act_key (soft_reg_contact BIGINT, act_key VARCHAR(50) UNIQUE, valid_till VARCHAR(15), sys_hash VARCHAR(100), FOREIGN KEY (soft_reg_contact) REFERENCES soft_reg(bus_contact));")
connection.commit()


# cursor.execute("drop table act_key")
# cursor.execute("drop table soft_reg")
# connection.commit()

cursor.execute("select * from soft_reg")
for row in cursor.fetchall():
    print(row)

cursor.execute("select * from act_key")
for row in cursor.fetchall():
    print(row)


cursor.close()
connection.close()