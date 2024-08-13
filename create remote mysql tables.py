import mysql.connector

connection = mysql.connector.connect(
    host = "sql.freedb.tech",
    user = "freedb_random",
    password = "tShRRj6$caS2uzF",
    database = "freedb_software"
)
cursor = connection.cursor()

# cursor.execute("CREATE TABLE IF NOT EXISTS soft_reg (id INT AUTO_INCREMENT PRIMARY KEY, bus_name VARCHAR(30), bus_contact BIGINT UNIQUE, bus_password VARBINARY(255), valid_till VARCHAR(15));")
# cursor.execute("CREATE TABLE IF NOT EXISTS act_key (id INT AUTO_INCREMENT PRIMARY KEY, soft_reg_id INT, act_key VARCHAR(50) UNIQUE, valid_till VARCHAR(15), sys_hash VARCHAR(100), FOREIGN KEY (soft_reg_id) REFERENCES soft_reg(id));")
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