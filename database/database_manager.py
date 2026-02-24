import sqlite3


class DataBase(sqlite3.Cursor):
    DATATYPES = ["INTEGER", "REAL", "TEXT", "BLOB"]

    def __init__(self, db_path: str) -> None:
        self.path = db_path
        super().__init__(sqlite3.connect(db_path))

        # fetch all current tables
        table_names = self.execute("SELECT name FROM sqlite_schema WHERE type = 'table';", ifReturnOutput=True)

        self.tables = dict()  # tables and their structures in the DB
        for table_name in table_names:
            table_name = table_name[0]  # because "(table_name, )" returned
            table_structure = dict()  # structure of the currently iterated table

            columns = self.execute(f"SELECT * FROM PRAGMA_TABLE_INFO('{table_name}');", ifReturnOutput=True)  # get column structure of the table
            for column in columns:
                # TODO do something with 'notnull' not accepted as selectable column OR do something with cid and dflt_value
                cid, column_name, datatype, ifNotNull, dflt_value, ifPrimaryKey = int(column[0]), str(column[1]), str(column[2]), bool(column[3]), str(column[4]), bool(column[5])
                # add info on the column
                table_structure[column_name] = {
                    "datatype": datatype,
                    "ifNotNull": ifNotNull,
                    "ifPrimaryKey": ifPrimaryKey,
                }

            self.tables[table_name] = table_structure  # add currently iterated table's structure to the global structure variable

    # clears the database
    def reset(self) -> None:
        with open(self.path, "w") as file:
            file.write("")

    # execute, but with an option to return the output
    def execute(self, sql_query, ifReturnOutput = False, parameters = ()):
        out = super().execute(sql_query, parameters)
        if ifReturnOutput:
            out = out.fetchall()
        return out
    
    def create_table(self, table_name, table_structure):
        query = f"CREATE TABLE {table_name} ("

        columns = list()
        for column_name in table_structure:
            datatype, ifNotNull, ifPrimaryKey = table_structure["datatype"], table_structure["ifNotNull"], table_structure["ifPrimaryKey"]
            column_query = f"{column_name} {datatype}"
            if ifNotNull: column_query += "NOT NULL"
            if ifPrimaryKey: column_query += "PRIMARY KEY AUTOINCREMENT"
            # TODO



if __name__ == "__main__":
    test_db = DataBase("test/test.db")
    print(test_db.tables)
