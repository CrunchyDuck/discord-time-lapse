import sqlite3

con = sqlite3.connect("activity.db")
cur = con.cursor()

cur.execute("SELECT * FROM activity ORDER BY time DESC")
for e in cur.fetchall():
	print(e)