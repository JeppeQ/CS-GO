import sqlite3

conn = sqlite3.connect('csgostats.db')
print "Opened database successfully";

conn.execute("DROP TABLE IF EXISTS Player2")

# Create table as per requirement

sql = """CREATE TABLE Player2 (
        player_id INT NOT NULL,
        alias VARCHAR(100),
        hltv_id INT )"""

conn.execute(sql)


# disconnect from server
conn.close()
