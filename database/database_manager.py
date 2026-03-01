import sqlite3


# Column and subclasses
'''
Column class
'''
class Column:
    DATATYPES = ["INTEGER", "REAL", "TEXT", "BLOB"]  # valid datatypes

    # no constraints given by default
    def __init__(self, name: str, datatype: str, ifNotNull: bool = False, ifPrimaryKey: bool = False, ifAutoIncrement: bool = False, ifForeignKey: bool = False, foreign_table_name: str = None, foreign_column_name: str = None) -> None:
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
            raise TypeError(f"column '{name}':  invalid datatype: '{datatype}', select from {Column.DATATYPES}")
        
        if (ifAutoIncrement) and (datatype != "INTEGER"):  # check if autoincrement valid
            raise TypeError(f"column '{name}':  can't have autoincrement with {datatype} datatype")
        
        if ifForeignKey and not (foreign_table_name and foreign_column_name):  # check if all required information for foreign key given
            raise Exception(f"column '{name}':  set as foreign key, but connected table and/or name of connected column not given")
        if not ifForeignKey and (foreign_table_name or foreign_column_name):  # check if no redundant foreign key information given
            raise Exception(f"column '{name}':  not set as foreign key, but connected table and/or name of connected column given")

# special column types
'''
Primary Key column
'''
class PrimaryKey(Column):
    # default PK is assumed to be "ID INTEGER NOT NULL AUTOINCREMENT"
    def __init__(self, name: str = "ID", datatype: str = "INTEGER", ifNotNull: bool = True, ifAutoIncrement: bool = True) -> None:
        super().__init__(name=name, datatype=datatype, ifNotNull=ifNotNull, ifPrimaryKey=True, ifAutoIncrement=ifAutoIncrement)

'''
Foreign Key column
'''
class ForeignKey(Column):
    # default FK assumed to accept NULL. AUTOINCREMENT not possible
    def __init__(self, name: str, datatype: str, ifNotNull: bool = False, foreign_table_name: str = None, foreign_column_name: str = None) -> None:
        super().__init__(name=name, datatype=datatype, ifNotNull=ifNotNull, ifForeignKey=True, foreign_table_name=foreign_table_name, foreign_column_name=foreign_column_name)


'''
Array of values for a particular column (vertical) 
!!! NOT A ROW / DATA TUPLE (horizontal) !!!
For INSERTABLE horizontal data entries see DataRows
'''
class ColumnData:
    def __init__(self, column: Column, values: list) -> None:
        self.column = column
        self.values = tuple(values)


'''
Array of data rows (horizontal form)
Made for easy INSERT
Index of a value inside of its row is index of the corresponding column in self.columns
'''
class DataMatrix:
    def __init__(self, *column_data_array: ColumnData) -> None:
        # check if amount of given values (=> amount of rows) consistant across every ColumnValueList
        rows_amount = len(column_data_array[0].values)
        for column_data in column_data_array[1:]:
            if len(column_data.values) != rows_amount:
                raise Exception(f"amount of rows not consistant in every attribute list: {column_data} of {column_data.column.name}")

        # combine data of all columns
        columns = list()  # list of columns
        column_data_values_array = list()  # list of all .values attributes of ColumnData instances (=> 2d array: column_data_values_array[column_data.values])
        for column_data in column_data_array:
            columns.append(column_data.column)
            column_data_values_array.append(column_data.values)
        
        # spread column data onto rows
        data_rows = zip(*column_data_values_array)  # unpack array into arguments with *
        
        self.columns = tuple(columns)  # array of columns => fixed amount
        self.data_rows = list(data_rows)  # flexible array of data rows => flexible amount


'''
Database Table
'''
class DBTable:
    def __init__(self, name: str, columns: list[Column] = []) -> None:
        self.name = name

        self.column_map = dict()  # map column names to instances if given. otherwise just create dict
        for column in columns:
            self.column_map[column.name] = column
    
    # check if valid column name or instance given and return instance. raises exception if validity check failed
    # TODO: Ask Hr Stresing about validy of such syntax (calling private method outside)
    def _verify_column(self, column: Column | str) -> Column:
        ifInstance: bool
        # check whether column is an instance or name
        if isinstance(column, Column):  # instance
            column_name = column.name
            ifInstance = True
        else:  # name
            column_name = column
            ifInstance = False

        expected_instance = self.fetch_column(column_name=column_name)  # column instance mapped in the table structure, or None if not found
        if not expected_instance:  # column name not in DB structure
            raise Exception(f"Column '{column_name}' not in the table '{self.name}'")
        elif ifInstance and (expected_instance != column):  # table name in DB structure but instance is different
            raise Exception(f"Wrong Column instance given (expected {expected_instance}, but got {column})")

        return expected_instance
    
    # fetch a column from the table by name, return None if not found
    def fetch_column(self, column_name: str) -> Column | None:
        return self.column_map.get(column_name)


'''
Database
'''
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

    # check if valid table name or instance given and return instance. raises exception if validity check failed
    def _verify_table(self, table: DBTable | str) -> DBTable:
        ifInstance: bool
        # check whether table is an instance or name
        if isinstance(table, DBTable):  # instance
            table_name = table.name
            ifInstance = True
        else:  # name
            table_name = table
            ifInstance = False

        expected_instance = self.fetch_table(table_name=table_name)  # table instance mapped in the DB structure, or None if not found
        if not expected_instance:  # table name not in DB structure
            raise Exception(f"DBTable '{table_name}' not in the database '{self.path}'")
        elif ifInstance and (expected_instance != table):  # table name in DB structure but instance is different
            raise Exception(f"Wrong DBTable instance given (expected {expected_instance}, but got {table})")

        return expected_instance

    # clears the database
    def reset(self) -> None:
        with open(self.path, "w") as file:
            file.write("")

    # execute, but with an option to return the output
    def execute(self, sql_query: str, ifReturnOutput: bool = False) -> list | None:
        super().execute(sql_query)
        out = None
        if ifReturnOutput:
            out = self.fetchall()
        return out

    # fetch table based on the name, return None if not found
    def fetch_table(self, table_name: str) -> DBTable | None:
        return self.table_map.get(table_name)
    
    def create_table(self, table_name: str, columns: list[Column]) -> DBTable:
        # create instance of the table and add it to the table map
        table = DBTable(name=table_name)
        self.table_map[table_name] = table

        column_strings = list()  # strings for creating a column
        fk_constraint_strings = list()  # strings for creating foreign key constraints
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
            column_strings.append(column_query)

            # add foreign key constraints
            if column.ifForeignKey:
                constraint_string = f"FOREIGN KEY ({column.name}) REFERENCES {column.foreign_table_name}({column.foreign_column_name})"
                fk_constraint_strings.append(constraint_string)
        
        # combine columns and foreign key constraint queries
        column_strings.extend(fk_constraint_strings)
        # add all queries
        columns_string = ", ".join(column_strings)

        sql_query = f"CREATE TABLE {table_name} ({columns_string});"
        self.execute(sql_query)

        return table

    def insert_values(self, table: DBTable | str, data_matrix: DataMatrix) -> None:  # parameter table accepts both DBTable instance and valid table name
        table = self._verify_table(table=table)  # verify table validity
        table_name = table.name

        column_names = list(column.name for column in data_matrix.columns)  # list of column names
        column_names_string = ", ".join(column_names)  # convert list of column names to a string

        rows_strings = list()  # array of rows as strings
        for row in data_matrix.data_rows:
            values_strings = list()  # array of values from row as strings
            for value, column in zip(row, data_matrix.columns):  # iterate over both arrays to also return column
                value_string: str  # value converted to string
                if value == None:  # convert python None to SQL null
                    value_string = "null"
                elif column.datatype == "TEXT":  # add ''
                    value_string = f"'{value}'"
                else:
                    value_string = f"{value}"
                values_strings.append(value_string)
            values_string = ", ".join(values_strings)  # convert list of value strings to a string
            row_string = f"({values_string})"  # put the values into brackets, fulfill row string
            rows_strings.append(row_string)
        data_string = ", ".join(rows_strings)  # convert list of row strings to a string
                
        sql_query = f"INSERT INTO {table_name} ({column_names_string}) VALUES {data_string};"
        self.execute(sql_query)
    
    def singleSelect(self, table: DBTable, columns_list: list[Column], ifDistinct: bool = False) -> list:
        return self.complexSelect(table_array=[table], columns_list_array=[columns_list], ifDistinct=ifDistinct)

    def complexSelect(self, table_array: list[DBTable] | list[str] = [], columns_list_array: list[list[Column] | list[str]] = [], ifDistinct: bool = False) -> list:  # idx of DBTable has to equal to idx of corresponding columns list
        # TODO: add functionality like WHERE constraint or *
        # validate input
        # check if all * selected
        tables_amount = len(table_array)
        # TODO: check if all tables selected
        # check if arguments are of correct data type
        if (not isinstance(table_array, list)) or (not isinstance(columns_list_array, list)):
            raise Exception("Wrong data type of argument(s). table_array should be a list and columns_list_array should be a 2d list")
        # check length consistency
        if tables_amount != len(columns_list_array):
            raise Exception(f"Length of table_array ({len(table_array)}) doesn't match length of columns_list_array ({len(columns_list_array)})")
        
        # verify tables and columns
        for idx in range(tables_amount):
            table = table_array[idx]  # access table
            table_instance = self._verify_table(table=table)  # get table instance
            table_array[idx] = table_instance  # replace unknown type of table with table instance

            columns_list = columns_list_array[idx]  # access columns list
            column_instances_list = list(table_instance._verify_column(column=column) for column in columns_list)  # create list with column instances
            columns_list_array[idx] = column_instances_list  # replace list of columns with unknown type with lists of confirmed column instances

        table_names_list = list()  # list of tables as strings / table names
        column_strings_list = list()  # list of columns as strings
        for table, columns_list in zip(table_array, columns_list_array):
            table_names_list.append(table.name)
            # record strings in the 'table.column' format
            for column in columns_list:
                column_string = f"{table.name}.{column.name}"
                column_strings_list.append(column_string)
        
        table_names_string = ", ".join(table_names_list)
        columns_string = ", ".join(column_strings_list)

        distinct_constraint_string = ""
        if ifDistinct:
            distinct_constraint_string = "DISTINCT "

        # construct sql query
        sql_query = f"SELECT {distinct_constraint_string}{columns_string} FROM {table_names_string};"
        return self.execute(sql_query=sql_query, ifReturnOutput=True)
        
        


if __name__ == "__main__":
    test_db = DataBase("test/test.db")
    # test_db.reset()

    # schueler_columns = [PrimaryKey(), Column("vorname", "TEXT", True), Column("nachname", "TEXT"), ForeignKey("wunschID", "INTEGER", foreign_table_name="sportkurs", foreign_column_name="ID")]
    # sportkurs_columns = [PrimaryKey(), Column("name", "TEXT", True), Column("sporthalle", "TEXT", False)]

    # test_db.create_table("sportkurs", sportkurs_columns)
    # test_db.create_table("schueler", schueler_columns)
    
    schuler_table = test_db.fetch_table("schueler")
    # names_list = ColumnData(schuler_table.fetch_column("vorname"), ("Markus", "Friedrich", "Andreas"))
    # lnames_list = ColumnData(schuler_table.fetch_column("nachname"), ("Soeder", "Merz", "Andreass"))
    # wunsch_list = ColumnData(schuler_table.fetch_column("wunschID"), (3, 2, None))

    sportkurs_table = test_db.fetch_table("sportkurs")
    # sportkurs_name_list = ColumnData(sportkurs_table.fetch_column("name"), ("Jagd", "Glueckspiel", "Schach", "Motorsport"))

    # schuler_data = DataMatrix(names_list, lnames_list, wunsch_list)
    # sportkurs_data = DataMatrix(sportkurs_name_list)


    # test_db.insert_values("sportkurs", data_matrix=sportkurs_data)
    # test_db.insert_values(schuler_table, data_matrix=schuler_data)


    # for table in test_db.table_map.values():
    #     print(table.column_map)
    #     for column in table.column_map.values():
    #         print(column, column.name, column.datatype, column.ifNotNull, column.ifPrimaryKey, column.ifAutoIncrement, column.ifForeignKey, column.foreign_table_name, column.foreign_column_name)

    values = test_db.complexSelect()
    print(values)
    pass
