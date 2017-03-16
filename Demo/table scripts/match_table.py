import sqlite3

conn = sqlite3.connect('csgostats.db')
print "Opened database successfully";

conn.execute("DROP TABLE IF EXISTS Match")

# Create table as per requirement

sql = """CREATE TABLE Match (
        match_id INT NOT NULL,
        date VARCHAR(40),
        team1_id INT,
        team2_id INT,
        winner INT,
        format CHAR(20),
        player1_id INT,
        player2_id INT,
        player3_id INT,
        player4_id INT,
        player5_id INT,
        player6_id INT,
        player7_id INT,
        player8_id INT,
        player9_id INT,
        player10_id INT,
        team1picks VARCHAR(200),
        team2picks VARCHAR(200),
        team1bans VARCHAR(200),
        team2bans VARCHAR(200),
        UNIQUE(match_id) )"""

conn.execute(sql)


# disconnect from server
conn.close()
