import sqlite3

conn = sqlite3.connect('csgostats.db')
print "Opened database successfully";

conn.execute("DROP TABLE IF EXISTS Team")

# Create table as per requirement

sql = """CREATE TABLE Team (
        team_id INT NOT NULL,
        hltv_alias VARCHAR(100),
        pinnacle_alias VARCHAR(100),
        egaming_alias VARCHAR(100),
        UNIQUE(team_id) )"""

conn.execute(sql)


# disconnect from server
conn.close()
