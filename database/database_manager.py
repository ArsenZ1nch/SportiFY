import sqlite3


class DataBase(sqlite3.Cursor):
    def __init__(self, db_path: str) -> None:
        self.path = db_path
        self.db_connection = sqlite3.connect(db_path)
        super().__init__(self.db_connection)

    def execute(self, sql):
        out = super().execute(sql)
        self.db_connection.commit()
        return out
    
    # execute, but return output
    def output(self, sql_query: str) -> list:
        command = super().execute(sql_query)
        return command.fetchall()
    
    # clears the database
    def reset(self) -> None:
        with open(self.path, "w") as file:
            file.write("")

    # TODO: built in INSERT INTO method


if __name__ == "__main__":
    db = DataBase("database/database.db")
    db.reset()
