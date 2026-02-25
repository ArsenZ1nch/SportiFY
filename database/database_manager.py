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
        self.foreign_table_name = foreign_table_name
        self.foreign_column_name = foreign_column_name

        # check if inputs valid
        if datatype not in Column.DATATYPES:  # check if datatype is valid
            raise TypeError(f"invalid datatype: '{datatype}', select from {Column.DATATYPES}")
        if (ifAutoIncrement) and (datatype != "INTEGER"):  # check if autoincrement valid
            raise TypeError(f"can't have autoincrement with {datatype} datatype")
        if ifForeignKey and not (foreign_table_name and foreign_column_name):  # check if all required information for foreign key given
            raise Exception("column set as foreign key, but connected table and/or name of connected column not given")
        if not ifForeignKey and (foreign_table_name or foreign_column_name):  # check if not redundant foreign key information given
            raise Exception("column not set as foreign key, but connected table and/or name of connected column given")

class PrimaryKey(Column):
    def __init__(self, name = "ID", datatype = "INTEGER", ifNotNull = True, ifAutoIncrement = True):
        super().__init__(name=name, datatype=datatype, ifNotNull=ifNotNull, ifPrimaryKey=True, ifAutoIncrement=ifAutoIncrement)

class ForeignKey(Column):
    def __init__(self, name, datatype, ifNotNull = False, foreign_table_name = None, foreign_column_name = None):
        super().__init__(name=name, datatype=datatype, ifNotNull=ifNotNull, ifForeignKey=True, foreign_table_name=foreign_table_name, foreign_column_name=foreign_column_name)


class DBTable:
    def __init__(self, name: str, columns: list[Column] = []):
        self.name = name
        # map column names and column instances
        self.column_map = dict()
        for column in columns:
            self.column_map[column.name] = column
    
    def fetch_column(self, column_name: str) -> Column:
        return self.column_map[column_name]


class AttributeList:
    def __init__(self, column_name: Column, value_list: tuple):
        self.column = column_name
        self.value_list = value_list


class DataBase(sqlite3.Cursor):
    def __init__(self, db_path: str) -> None:
        self.path = db_path
        super().__init__(sqlite3.connect(db_path, autocommit=True))

        # turn on Foreign Key constraint
        self.execute("PRAGMA foreign_keys = ON;")

        # fetch all current tables
        table_names = self.execute("SELECT name FROM sqlite_schema WHERE type = 'table' AND name NOT LIKE 'sqlite_%';", ifReturnOutput=True)  # dont return sqlite_sequence table

        self.table_map = dict()  # tables with their name and corresponding table instance
        for table_name in table_names:
            table_name = table_name[0]  # because "(table_name, )" returned
            table = DBTable(table_name)  # create table instance
            self.table_map[table_name] = table  # map the instance to table name

            # get column structure of the table, no foreign key information
            columns = self.execute(f"SELECT * FROM PRAGMA_TABLE_INFO('{table_name}');", ifReturnOutput=True)  # get infos of each column; have to extract * due to wrong interpretation of 'notnull'
            for column_info in columns:
                # TODO comment
                column_name, datatype, ifNotNull, ifPrimaryKey = str(column_info[1]), str(column_info[2]), bool(column_info[3]), bool(column_info[5])
                # check if primary key, add info on the column
                if ifPrimaryKey:
                    column = PrimaryKey(name=column_name, datatype=datatype, ifNotNull=ifNotNull)  # autoincrement assumed to true for PKs, otherwise false
                else:
                    column = Column(name=column_name, datatype=datatype, ifNotNull=ifNotNull)
                table.column_map[column.name] = column  # map column instance to its name in the table instance

            # record foreign key information
            foreign_keys = self.execute(f"SELECT * FROM PRAGMA_FOREIGN_KEY_LIST('{table_name}');", ifReturnOutput=True)  # get infos of each foreign key; have to extract * due to wrong interpretation of 'from', 'table' and 'to'
            for fk_info in foreign_keys:
                foreign_table_name, fk_name, foreign_column_name = fk_info[2], fk_info[3], fk_info[4]
                foreign_key_column = table.column_map[fk_name]  # get the column, falsely unclassified as foreign key
                # update the column to an instance of ForeignKey
                foreign_key_column = ForeignKey(
                    name=foreign_key_column.name, datatype=foreign_key_column.datatype, ifNotNull=foreign_key_column.ifNotNull,     # transfer the old attributes
                    foreign_table_name=foreign_table_name, foreign_column_name=foreign_column_name                                  # enter new foreign key connection info
                    )
                table.column_map[fk_name] = foreign_key_column  # update the column in the map

    # fetch table based on the name
    def fetch_table(self, table_name: str) -> DBTable:
        return self.table_map[table_name]

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
        # create instance of the table and add it to the table map
        table = DBTable(name=table_name)
        self.table_map[table_name] = table

        sql_query = f"CREATE TABLE {table_name} ("

        queries = list()  # queries for creating a column
        fk_constraint_queries = list()  # queries for creating foreign key constraints
        for column in columns:
            # add column to the table
            table.column_map[column.name] = column

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
                constraint_query = f"FOREIGN KEY ({column.name}) REFERENCES {column.foreign_table_name}({column.foreign_column_name})"
                fk_constraint_queries.append(constraint_query)
        
        # combine columns and foreign key constraint queries
        queries.extend(fk_constraint_queries)
        # add all queries
        sql_query += ", ".join(queries)
        # finish sql_query
        sql_query += ");"

        return self.execute(sql_query, ifReturnOutput=True)


    def insert_values(self, table: DBTable, values: tuple[AttributeList]):
        # check if rows amount consistant over all attribute lists
        rows_amount = len(values[0].value_list)  # amount of rows
        for attribute_list in values[1:]:
            if len(attribute_list.value_list) != rows_amount:
                raise Exception(f"amount of rows not consistant in every attribute list: {attribute_list}")
            
        sql_query = f"INSERT INTO {table.name} ("

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
                value = attribute_list.value_list[row_idx]
                if value == None:  # convert python None to SQL null
                    value_query = "null"
                elif attribute_list.column.datatype == "TEXT":  # add '' in case text
                    value_query = f"'{value}'"
                else:
                    value_query = f"{value}"
                row_values.append(value_query)

            row_query += ", ".join(row_values)

            row_query += ")"
            rows_queries.append(row_query)

        sql_query += ", ".join(rows_queries)
        sql_query += ";"
    
        return self.execute(sql_query, ifReturnOutput=True)



if __name__ == "__main__":
    test_db = DataBase("test/test.db")
    test_db.reset()

    schueler_columns = [PrimaryKey(), Column("vorname", "TEXT", True), Column("nachname", "TEXT"), ForeignKey("wunschID", "INTEGER", foreign_table_name="sportkurs", foreign_column_name="ID")]
    sportkurs_columns = [PrimaryKey(), Column("name", "TEXT", True), Column("sporthalle", "TEXT", False)]

    test_db.create_table("sportkurs", sportkurs_columns)
    test_db.create_table("schueler", schueler_columns)
    
    schuler_table = test_db.fetch_table("schueler")
    names_list = AttributeList(schuler_table.fetch_column("vorname"), ("Jonas", "Andreas", "Markus"))
    lnames_list = AttributeList(schuler_table.fetch_column("nachname"), ("Soeder", "Merz", "Trump"))
    wunsch_list = AttributeList(schuler_table.fetch_column("wunschID"), (3, 2, None))

    sportkurs_table = test_db.fetch_table("sportkurs")
    sportkurs_name_list = AttributeList(sportkurs_table.fetch_column("name"), ("Jagd", "Glueckspiel", "Schach", "Motorsport"))

    test_db.insert_values(sportkurs_table, values=[sportkurs_name_list])
    test_db.insert_values(schuler_table, values=[names_list, lnames_list, wunsch_list])

    test_db.execute("SELECT schueler.vorname, schueler.nachname")


    # for table in test_db.table_map.values():
    #     print(table.column_map)
    #     for column in table.column_map.values():
    #         print(column, column.name, column.datatype, column.ifNotNull, column.ifPrimaryKey, column.ifAutoIncrement, column.ifForeignKey, column.foreign_table_name, column.foreign_column_name)
