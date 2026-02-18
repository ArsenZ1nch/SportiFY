import sqlite3
import json


if __name__ == "__main__":
    try:
        with open("test.db", "w") as f:
            f.write("")
    except Exception:
        open("test.db", "x")

    database_connection = sqlite3.connect("test.db")
    database_cursor = database_connection.cursor()
    
    with open("config/config.json") as config_file:
        parsed_config = json.load(config_file)
    database_tables = parsed_config["database_tables"]
    
    sql_command = str()
    for table_name in database_tables:
        sql_command += f"CREATE TABLE {table_name} (\n{database_tables[table_name]["PRIMARY_KEY"][0]} {database_tables[table_name]["PRIMARY_KEY"][1]} NOT NULL, \n"
        for secondary_key in database_tables[table_name]["SECONDARY_KEYS"]:
            sql_command += f"{secondary_key[0]} {secondary_key[1]} NOT NULL,\n"
        sql_command += f"PRIMARY KEY ({database_tables[table_name]["PRIMARY_KEY"][0]})\n);"
    
    print(sql_command)
        
        

