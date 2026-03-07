import sys, os
sys.path.append(os.getcwd())
from database.database_manager import *

def setup_DB(database: DataBase, tables_configuration: dict):
    for table_name, column_map in tables_configuration.items():
        columns_list = list()
        # add primary key data
        pk_name, pk_datatype = column_map["primary_key"]
        columns_list.append(PrimaryKey(name=pk_name, datatype=pk_datatype))
        # add misc columns data
        for column_data in column_map["columns"]:
            col_name, col_datatype = column_data[0:1]
            columns_list.append(Column(name=col_name, datatype=col_datatype))
        # add foreign keys
        for referenced_table_name, fk_list in column_map["foreign_keys"].items():
            for fk_name in fk_list:
                columns_list.append(ForeignKey(name=fk_name, ))
            



if __name__ == "__main__":
    from config import default_config

    print(default_config.database_tables)