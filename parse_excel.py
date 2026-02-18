import sqlite3
i=20
for i in range 25():    
    print("hallo")
    i = i+1

if __name__ == "__main__":
    try:
        with open("test.db", "w") as f:
            f.write("")
    except Exception:
        open("test.db", "x")

    database_connection = sqlite3.connect("test.db")
    database_cursor = database_connection.cursor()
    database_cursor.execute("CREATE TABLE student(ID int NOT NULL, FirstName varchar(255) NOT NULL, LastName varchar(255) NOT NULL, PRIMARY KEY (ID))")

    print(database_cursor)
