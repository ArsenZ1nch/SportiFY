import sqlite3, json


# scheiss KONSTANTE ist PATH für die Datebank
DATABASE_PATH = "database/database.db"

# öffne den Müll oder erstelle und mach es leer
with open(DATABASE_PATH, "w") as f:
    f.write("")

# behinderte Verbindung mit der Datenbank hinschmeißen
database_connection = sqlite3.connect(DATABASE_PATH)
database_cursor = database_connection.cursor()

# jsonDATEI oeffnen mit der vorgefertigten Struktur weil wir behindert sind und nur json lesen koennen
with open("config/config.json") as config_file:
    parsed_config = json.load(config_file)
database_tables = parsed_config["database_tables"]

for table_name in database_tables:
    sql_table_command = str() # keine ahnung was hier passiert - Andreas
    # weil du Spaßt nichts im Unterricht gemacht hast  - Arsenii

    # dieser Scheiss erstellt SQL COmmand fuer jeweilige Tabelle
    sql_table_command += f"CREATE TABLE {table_name} ({database_tables[table_name]["PRIMARY_KEY"][0]} {database_tables[table_name]["PRIMARY_KEY"][1]} NOT NULL, "
    for secondary_key in database_tables[table_name]["SECONDARY_KEYS"]:
        sql_table_command += f"{secondary_key[0]} {secondary_key[1]} NOT NULL, "
    # TODO: minfiziere den code aber aktuell geht es 
    # was zum fick meinst du  - ScrumMaster
    sql_table_command += f"PRIMARY KEY ({database_tables[table_name]["PRIMARY_KEY"][0]}));"

    # führe SQL Command aus
    database_cursor.execute(sql_table_command)


# ich bin verdammt lost das ist für Scheisstests in der verfickten Zukunft
if __name__ == "__main__":
        pass