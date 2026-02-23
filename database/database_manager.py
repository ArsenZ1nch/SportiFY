import sqlite3



class DataBase(sqlite3.Cursor):
    DATATYPES = ["INTEGER", "REAL", "TEXT", "BLOB"]

    def __init__(self, db_path: str) -> None:
        self.path = db_path
        self.db_connection = sqlite3.connect(db_path)
        super().__init__(self.db_connection)
    
    # clears the database
    def reset(self) -> None:
        with open(self.path, "w") as file:
            file.write("")

    # execute, but with an option to return the output
    def execute(self, sql_query, ifReturnOutput = False, parameters = ()):
        out = super().execute(sql_query, parameters)
        if ifReturnOutput:
            out = self.db_connection.fetchall()
        return out
    
    def create_table(self, table_name, attribute_map):
        pass
    # TODO: built in INSERT INTO method, add table with DBTable class


class DBTable:
    def __init__(self, name: str, database: DataBase):
        self.name = name
        self.database = database
        # TODO: 


class Attribute:
    def __init__(self, name: str, datatype: str, notNull: bool = False, autoIncrement: bool = False) -> None:
        # check given datatype validity
        if not datatype:  # case: no datatype given
            raise ValueError(f"no data type given")
        elif datatype not in DataBase.DATATYPES:  # case: not a valid data type
            raise ValueError(f"{datatype} not a valid data type, select from valid data types ({" ,".join(DataBase.DATATYPES)})")
        
        self.name = name
        self.datatype = datatype
        self.notNull = notNull
        self.autoIncrement = autoIncrement

class PrimaryKey(Attribute):
    DEFAULT_NAME = "ID"
    DEFAULT_DATATYPE = "INTEGER"

    def __init__(self, name: str = DEFAULT_NAME, datatype: str = DEFAULT_DATATYPE, autoIncrement: bool = True) -> None:
        notNull = True
        super().__init__(name, datatype, notNull, autoIncrement)


class ForeignKey(Attribute):
    def __init__(self, name, datatype, connected_table, notNull = False, autoIncrement = False):
        super().__init__(name, datatype, notNull, autoIncrement)



if __name__ == "__main__":
    db = DataBase("test/test.db")
    db.reset()
