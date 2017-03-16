import sqlite3

conn = sqlite3.connect('csgostats.db')
print "Opened database successfully";

conn.execute("DROP TABLE IF EXISTS Round")

# Create table as per requirement

sql = """CREATE TABLE Round (
        match_id INT NOT NULL,
        map VARCHAR(40),
        number INT,
        side_won CHAR(10),
        team_won INT,
        ct_survived INT,
        t_survived INT,
        ct_startmoney INT,
        t_startmoney INT,
        ct_equipvalue INT,
        t_equipvalue INT,
        ct_saved INT,
        t_saved INT,
        ctlosestreak INT,
        tlosestreak INT,
        plant INT,
        defuse INT,
        bombsite CHAR(10),
        UNIQUE(match_id, map, number))"""

conn.execute(sql)


# disconnect from server
conn.close()
