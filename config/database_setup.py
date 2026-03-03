# TODO: import DBTable

def setup_DB(database: DataBase, tables_configuration: dict):
    # TODO: integrate database
    pass    


if __name__ == "__main__":
    from parse_config import default_config
    import os, sys
    cwd = os.getcwd()
    sys.path.append(cwd)
    from database.database_manager import DataBase

    table_config = default_config.database_tables

    cur = DataBase(cwd + "/database/database.db")

    setup_DB(cur, table_config)