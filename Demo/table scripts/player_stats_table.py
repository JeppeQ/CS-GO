import sqlite3

conn = sqlite3.connect('csgostats.db')
print "Opened database successfully";

conn.execute("DROP TABLE IF EXISTS Playerstats")

# Create table as per requirement

sql = """CREATE TABLE Playerstats (
        player_id INT NOT NULL,
        match_id INT,
        map CHAR(20),
        round INT,
        kills INT,
        deaths INT,
        assists INT,
        UNIQUE(player_id, match_id, map, round) )"""

conn.execute(sql)


# disconnect from server
conn.close()
