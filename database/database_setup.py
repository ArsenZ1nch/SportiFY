import json
import sqlite3


# const paths
DATABASE_PATH = "database/database.db"
CONFIG_PATH = "config/config.json"


# empty DB if exists, otherwise create empty 
with open(DATABASE_PATH, "w") as f:
    f.write("")

# DB interface
database_connection = sqlite3.connect(DATABASE_PATH)
database_cursor = database_connection.cursor()

# open and parse config file
with open(CONFIG_PATH) as config_file:
    parsed_config = json.load(config_file)

# extract DB structure
database_tables = parsed_config["database_tables"]

# configure DB tables
for table_name in database_tables:
    table = database_tables[table_name]  # currently iterated table

    # INITIATE SQL query: create table with table name
    sql_table_command = f"CREATE TABLE {table_name} ("

    # APPEND to SQL query: primary key name & data type & PRIMARY KEY constraint
    sql_table_command += f"{table["primary_key"][0]} {table["primary_key"][1]} NOT NULL PRIMARY KEY"

    # APPEND to SQL query: column name & data type
    for column in table["columns"]:
        sql_table_command += f", {column[0]} {column[1]} NOT NULL"

    # ONLY FOR RELATIONSHIP TABLES: create foreign keys connection
    if table.get("connected_tables"):
        # sqlite requires foreign key constraints to be at the end of the query -> empty placeholder string 
        fkey_constraint_query = str()

        for connected_table_name in table["connected_tables"]:
            primary_key_name, primary_key_datatype = database_tables[connected_table_name]["primary_key"]  # name & data type of primary key of connected table
            foreign_key_name = f"{connected_table_name}_{primary_key_name}"  # unique foreign key name

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
        pass