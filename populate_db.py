import csv
import sqlite3


connection = sqlite3.connect("test.db")
cursor = connection.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS Documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rubrics TEXT NOT NULL,
        text TEXT NOT NULL,
        created_date TEXT NOT NULL
    )
    """
)

with open("posts.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    # Считывает заголовок
    next(reader)

    for row in reader:
        cursor.execute(
            "INSERT INTO Documents (text, created_date, rubrics) VALUES (?, ?, ?)",
            (row[0], row[1], row[2]),
        )

connection.commit()
connection.close()
