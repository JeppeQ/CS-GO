import sqlite3

conn = sqlite3.connect('csgostats.db')
print "Opened database successfully";

conn.execute("DROP TABLE IF EXISTS Player")

# Create table as per requirement

sql = """CREATE TABLE Player (
        player_id INT NOT NULL,
        alias VARCHAR(100),
        UNIQUE(player_id) )"""

conn.execute(sql)


# disconnect from server
conn.close()
