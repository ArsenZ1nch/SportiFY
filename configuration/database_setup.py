import sys, os
sys.path.append(os.getcwd())
from database.database_manager import *


def configure_DB(database: DataBase, tables_configuration: dict) -> None:
    for table_name, column_map in tables_configuration.items():
        columns_list = list()
        # add primary key data
        pk_name, pk_datatype = column_map["primary_key"]
        columns_list.append(PrimaryKey(name=pk_name, datatype=pk_datatype))
        # add misc columns data
        for column_data in column_map["columns"]:
            col_name, col_datatype = column_data[0:2]
            columns_list.append(Column(name=col_name, datatype=col_datatype))
        # add foreign keys
        for foreign_table_name, fk_list in column_map["foreign_keys"].items():
            referenced_column_name = tables_configuration[foreign_table_name]["primary_key"][0]  # fk assumed to always reference the pk
            for fk_name in fk_list:
                columns_list.append(ForeignKey(name=fk_name, foreign_table_name=foreign_table_name, referenced_column_name=referenced_column_name))  # foreign key assumed to always reference ID INTEGER
        # create table
        database.create_table(table_name=table_name, columns=columns_list)            



if __name__ == "__main__":
    from config import default_config
    db = DataBase("test/test.db")
    db.reset()
    configure_DB(database=db, tables_configuration=default_config.database_tables)
