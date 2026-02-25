import sqlite3


class Column:
    DATATYPES = ["INTEGER", "REAL", "TEXT", "BLOB"]

    def __init__(self, name: str, datatype: str, ifNotNull: bool = False, ifPrimaryKey: bool = False, ifAutoIncrement: bool = False, ifForeignKey: bool = False, foreign_table_name: str = None, foreign_column_name: str = None):
        self.name = name
        self.datatype = datatype
        self.ifNotNull = ifNotNull
        self.ifPrimaryKey = ifPrimaryKey
        self.ifAutoIncrement = ifAutoIncrement
        self.ifForeignKey = ifForeignKey
        self.connected_table = foreign_table_name
        self.connected_column = foreign_column_name

        # check if inputs valid
        if datatype not in Column.DATATYPES:  # check if datatype is valid
            raise TypeError(f"invalid datatype: '{datatype}', select from {Column.DATATYPES}")
        if (ifAutoIncrement) and (datatype != "INTEGER"):  # check if autoincrement valid
            raise TypeError(f"can't have autoincrement with {datatype} datatype")
        if ifForeignKey and not (foreign_table_name and foreign_column_name):  # check if all required information for foreign key given
            raise Exception("column set as foreign key, but connected table and/or name of connected column not given")
        if ifForeignKey and (foreign_table_name or foreign_column_name):  # check if not redundant foreign key information given
            raise Exception("column not set as foreign key, but connected table and/or name of connected column given")

class PrimaryKey(Column):
    def __init__(self, name = "ID", datatype = "INTEGER", ifNotNull = True, ifAutoIncrement = True):
        super().__init__(name=name, datatype=datatype, ifNotNull=ifNotNull, ifPrimaryKey=True, ifAutoIncrement=ifAutoIncrement)

class ForeignKey(Column):
    def __init__(self, name, datatype, ifNotNull = False, foreign_table_name = None, foreign_column_name = None):
        super().__init__(name=name, datatype=datatype, ifNotNull=ifNotNull, ifForeignKey=True, foreign_table_name=foreign_table_name, foreign_column_name=foreign_column_name)


class AttributeList:
    def __init__(self, column: Column, value_list: list):
        self.column = column
        self.value_list = value_list


class DataBase(sqlite3.Cursor):
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
    
    def create_table(self, table_name: str, columns: list[Column]):
        sql_query = f"CREATE TABLE {table_name} ("

        queries = list()  # queries for creating a column
        fk_constraint_queries = list()  # queries for creating foreign key constraints
        for column in columns:
            # SQL query: "NAME DATATYPE ..."
            column_query = f"{column.name} {column.datatype}"
            if column.ifNotNull:
                column_query += " NOT NULL"
            if column.ifPrimaryKey:
                column_query += " PRIMARY KEY"  # SQL query: "... PRIMARY KEY ..."
            if column.ifAutoIncrement:
                column_query += " AUTOINCREMENT"  # SQL query: "... AUTOINCREMENT"
            queries.append(column_query)

            # add foreign key constraints
            if column.ifForeignKey:
                constraint_query = f"FOREIGN KEY ({column.name}) REFERENCES {column.connected_table}({column.connected_column})"
                fk_constraint_queries.append(constraint_query)
        
        # combine columns and foreign key constraint queries
        queries.extend(fk_constraint_queries)
        # add all queries
        sql_query += ", ".join(queries)
        # finish sql_query
        sql_query += ");"

        self.execute(sql_query)

    def insert_values(self, table_name: str, values: list[AttributeList]):
        # check if rows amount consistant over all attribute lists
        rows_amount = len(values[0].value_list)  # amount of rows
        for attribute_list in values[1:]:
            if len(attribute_list.value_list) != rows_amount:
                raise Exception(f"amount of rows not consistend in every attribute list: {attribute_list}")
            
        sql_query = f"INSERT INTO {table_name} "

        # get column names of values
        column_names = list()
        for attribute_list in values:
            column_names.append(attribute_list.column.name)
        # convert column names to query
        sql_query += ", ".join(column_names)
        # finish column names
        sql_query += ") VALUES "

        rows_queries = list()
        for row_idx in range(rows_amount):
            row_query = "("

            row_values = list()
            for attribute_list in values:
                # append value to the current row
                # TODO: comments
                value_query = f"'{attribute_list.value_list[row_idx]}'"
                row_values.append(value_query)
            row_query += ", ".join(row_values)

            row_query += ")"
            rows_queries.append(row_query)

        sql_query += ", ".join(rows_queries)
        sql_query += ";"
    
        print(sql_query)



if __name__ == "__main__":
    test_db = DataBase("test/test.db")

    schueler_columns = [PrimaryKey(), Column("vorname", "TEXT", True), Column("nachname", "TEXT"), ForeignKey("wunschID", "INTEGER", foreign_table_name="sportkurs", foreign_column_name="ID")]
    sportkurs_columns = [PrimaryKey(), Column("name", "TEXT", True), Column("sporthalle", "TEXT", True)]

    test_db.reset()

    test_db.create_table("sportkurs", sportkurs_columns)
    test_db.create_table("schueler", schueler_columns)

    names_list = AttributeList("vorname", ["Arsenii", "Andreas", "Markus"])
    lnames_list = AttributeList("nachname", ["Soeder", "Scholz", "Trump"])
    wunsch_list = AttributeList("wunschID", [3, 6, None])

    test_db.insert_values("schueler", values=[names_list, lnames_list, wunsch_list])
