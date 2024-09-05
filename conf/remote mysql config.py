import mysql.connector
import mysql.connector.locales.eng

connection = mysql.connector.connect(
    host = "sql.freedb.tech",
    user = "freedb_random",
    password = "tShRRj6$caS2uzF",
    database = "freedb_software"
)
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS soft_reg (bus_name VARCHAR(30), bus_contact BIGINT UNIQUE, bus_password VARBINARY(255), valid_till VARCHAR(15), sys_hash VARCHAR(100));")
cursor.execute("CREATE TABLE IF NOT EXISTS act_key (soft_reg_contact BIGINT, act_key VARCHAR(50) UNIQUE, valid_till VARCHAR(15), sys_hash VARCHAR(100), FOREIGN KEY (soft_reg_contact) REFERENCES soft_reg(bus_contact));")
connection.commit()


# cursor.execute("delete from act_key where soft_reg_contact=7777777777")
# cursor.execute("delete from soft_reg where bus_contact=7777777777")
# connection.commit()

cursor.execute("select * from soft_reg")
for row in cursor.fetchall():
    print(row)

cursor.execute("select * from act_key")
for row in cursor.fetchall():
    print(row)


cursor.close()
connection.close()