import sqlite3


def setup_DB(database_path: str, tables_configuration: dict):
    # empty DB if exists, otherwise create empty 
    with open(database_path, "w") as f:
        f.write("")

    # DB interface
    database_connection = sqlite3.connect(database_path)
    database_cursor = database_connection.cursor()

    # configure DB tables
    for table_name in tables_configuration:
        table = tables_configuration[table_name]  # currently iterated table

        # INITIATE SQL query: create table with table name
        sql_table_command = f"CREATE TABLE {table_name} ("

        # APPEND to SQL query: primary key name & data type & PRIMARY KEY constraint
        sql_table_command += f"{table["primary_key"][0]} {table["primary_key"][1]} NOT NULL PRIMARY KEY"

        # APPEND to SQL query: column name & data type
        for column in table["columns"]:
            sql_table_command += f", {column[0]} {column[1]} NOT NULL"

        # ONLY FOR RELATIONSHIP TABLES: create foreign keys connection
        # sqlite requires foreign key constraints to be at the end of the query -> empty placeholder string 
        fkey_constraint_query = str()
        for connected_table_name in table["foreign_keys"]:
            primary_key_name, primary_key_datatype = tables_configuration[connected_table_name]["primary_key"]  # name of primary key of connected table
            
            for foreign_key_name in table["foreign_keys"][connected_table_name]:
                # APPEND to SQL query: foreign key name & data type
                sql_table_command += f", {foreign_key_name} {primary_key_datatype} NOT NULL"

                # add constraint query to placeholder string
                fkey_constraint_query += f", FOREIGN KEY ({foreign_key_name}) REFERENCES {connected_table_name}({primary_key_name})"
        
        # APPEND to SQL query: foreign key constraints
        sql_table_command += fkey_constraint_query

        # FINISH SQL query
        sql_table_command += ");"

        # EXECUTE SQL query
        database_cursor.execute(sql_table_command)


if __name__ == "__main__":
    from parse_config import Configuration
    import os

    config = Configuration()
    table_config = config.database_tables

    cwd = os.getcwd()
    setup_DB(cwd + "/database/database.db", table_config)