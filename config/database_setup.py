def setup_DB(database_cursor, tables_configuration: dict):
    # reset the database
    database_cursor.reset()

    # configure DB tables
    for table_name in tables_configuration:
        table = tables_configuration[table_name]  # currently iterated table

        # INITIATE SQL query: create table with table name
        sql_table_command = f"CREATE TABLE {table_name} ("

        # APPEND to SQL query: primary key name & data type & PRIMARY KEY constraint
        sql_table_command += f"{table["primary_key"][0]} {table["primary_key"][1]} PRIMARY KEY AUTOINCREMENT"

        # APPEND to SQL query: attribute name & data type
        for attribute in table["attributes"]:
            sql_table_command += f", {attribute[0]} {attribute[1]} NOT NULL"

        # ONLY FOR RELATIONSHIP TABLES: create foreign keys connection
        # sqlite requires foreign key constraints to be at the end of the query -> empty placeholder string 
        fkey_constraint_query = str()
        for connected_table_name in table["foreign_keys"]:
            primary_key_name, primary_key_datatype = tables_configuration[connected_table_name]["primary_key"]  # name of primary key of connected table
            
            for foreign_key_name in table["foreign_keys"][connected_table_name]:
                # APPEND to SQL query: foreign key name & data type
                sql_table_command += f", {foreign_key_name} {primary_key_datatype}"

                # add constraint query to placeholder string
                fkey_constraint_query += f", FOREIGN KEY ({foreign_key_name}) REFERENCES {connected_table_name}({primary_key_name})"
        
        # APPEND to SQL query: foreign key constraints
        sql_table_command += fkey_constraint_query

        # APPEND to SQL query: finish
        sql_table_command += ");"

        # EXECUTE SQL query
        database_cursor.execute(sql_table_command)


if __name__ == "__main__":
    from parse_config import default_config
    import os, sys
    cwd = os.getcwd()
    sys.path.append(cwd)
    from database.database_manager import DataBase

    table_config = default_config.database_tables

    cur = DataBase(cwd + "/database/database.db")

    setup_DB(cur, table_config)