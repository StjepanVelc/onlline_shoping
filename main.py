import sqlite3

conn = sqlite3.connect("data/shop.db")
cur = conn.cursor()

cur.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Ana", "ana@mail.com"))
cur.execute(
    "INSERT INTO users (name, email) VALUES (?, ?)", ("Marko", "marko@mail.com")
)

conn.commit()

cur.execute("SELECT * FROM users")
print(cur.fetchall())

conn.close()
