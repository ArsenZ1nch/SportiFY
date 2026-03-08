import sys, os
sys.path.append(os.getcwd())
from configuration.config import Configuration, default_config
from database.database_manager import *
import openpyxl


'''
TODO: make possible to choose sheet
'''
def open_excel_sheet(excel_path: str) -> openpyxl.Workbook:
    workbook = openpyxl.load_workbook(excel_path)
    return workbook.active


def get_student_info(worksheet: openpyxl.Workbook) -> dict:
    # map of categories with the corresponding cells
    categorycell_map = {}

    # find cell location of categories
    checks_done = False  # stop checking cell names if all categories found
    for row_tuple in worksheet.rows:
        if not checks_done:
            for cell in row_tuple:
                match cell.value:
                    # TODO: dict keys aus config.json nehmen
                    case "Vorname":
                        categorycell_map["VorName"] = cell
                    case "Nachname":
                        categorycell_map["NachName"] = cell
                    case "Semester":
                        categorycell_map["Semester"] = cell
                    case "1. Wunsch":
                        categorycell_map["Wunsch1"] = cell
                    case "2. Wunsch":
                        categorycell_map["Wunsch2"] = cell
                    case "3. Wunsch":
                        categorycell_map["Wunsch3"] = cell
                    case "4. Wunsch":
                        categorycell_map["Wunsch4"] = cell
                    case "5. Wunsch":
                        categorycell_map["Wunsch5"] = cell
                    case "6. Wunsch":
                        categorycell_map["Wunsch6"] = cell
                        # final category to find -> no more checks needed
                        checks_done = True
        # find last row with data
        last_data_row_tuple = row_tuple

    # expected row of the categories. VorName as example
    categories_row = categorycell_map["VorName"].row

    EXPECTED_CATEGORY_AMOUNT = 9
    if len(categorycell_map) < EXPECTED_CATEGORY_AMOUNT:  # not all categories found
        raise Exception(f"not all categories found. found {len(categorycell_map)}, while {EXPECTED_CATEGORY_AMOUNT} expected")
    if len(categorycell_map) > EXPECTED_CATEGORY_AMOUNT:  # too many categories
        raise Exception(f"too many categories found. found {len(categorycell_map)}, while {EXPECTED_CATEGORY_AMOUNT} expected")

    for category, cell in categorycell_map.items():
        if cell.row != categories_row:  # compare row of category to expected row idx
            raise Exception(f"categories are not in the same row. Anomaly at '{category}' row")

    # determine range of data
    first_data_row = categories_row + 1  # one below categories row
    last_data_row = last_data_row_tuple[0].row  # get row idx of random cell in the row

    # assign an array of values to each category/column
    column_values_map = dict()
    for category, cell in categorycell_map.items():
        column = cell.column
        column_values = list()
        for row_idx in range(first_data_row, last_data_row+1):
            cell = worksheet.cell(column=column, row=row_idx)
            column_values.append(cell.value)
        column_values_map[category] = column_values

    return column_values_map


def fill_student_DB(database: DataBase, column_values_map: dict) -> None:
    db_values = dict()

    db_values["VorName"] = column_values_map["VorName"].copy()
    db_values["NachName"] = column_values_map["NachName"].copy()

    # convert text semester to integer (e. g. Q3 -> 3)
    semester_values = list()
    for semester_string in column_values_map["Semester"]:
        semester_int = int(semester_string.strip("Q "))
        semester_values.append(semester_int)
    db_values["Semester"] = semester_values

    # get unique sport names from Wuensche 1-6
    sport_names_set = set()
    for category_name, values_list in column_values_map.items():
        if category_name.startswith("Wunsch"):
            for sport_name in values_list:
                sport_names_set.add(sport_name)

    # TODO: remove later, instead set up in database_setup.py
    # insert sport name values into DB
    # sportkurs_table = database.fetch_table("sportkurs")
    # sport_name_data = ColumnData(sportkurs_table.fetch_column("KursName"), list(sport_names_set))
    # sportkurse_data = DataMatrix(sport_name_data)
    # database.insert_values(table="sportkurs", data_matrix=sportkurse_data)

    # map ids of sportkurse to their names
    sport_id_map = dict()
    for sport_name in sport_names_set:
        sport_id_row = database.single_select(table="sportkurs", columns=["ID"], where_constraint=f"KursName = '{sport_name}'")  # row sport id data ([(id,)])
        sport_id = sport_id_row[0][0]
        sport_id_map[sport_name] = sport_id

    # put wishes into db_values
    for category_name, values_list in column_values_map.items():
        if category_name.startswith("Wunsch"):
            sport_id_list = list()  # list of sportkurs id corresponding to WunschX
            for sport_name in values_list:
                sport_id = sport_id_map[sport_name]
                sport_id_list.append(sport_id)
            db_column_name = f"{category_name}_ID"
            db_values[db_column_name] = sport_id_list

    # put values into DB
    schueler_table = database.fetch_table("schueler")
    column_data_list = list()
    for column_name, values_list in db_values.items():
        column_data = ColumnData(column=schueler_table.fetch_column(column_name), values=values_list)
        column_data_list.append(column_data)
    insert_data = DataMatrix(*column_data_list)

    database.insert_values("schueler", data_matrix=insert_data)    



if __name__ == "__main__":
    db = DataBase("test/test.db")
    worksheet = open_excel_sheet("test/test.xlsx")
    student_info = get_student_info(worksheet)
    fill_student_DB(database=db, column_values_map=student_info, )
    
    

    # fill_student_DB(database=db, students_info=student_info, config=default_config)


    # def fill_courses_db():
    #     sport_courses = set()
    #     for student in student_info:
    #         for attr_name in student:
    #             if "Wunsch" not in attr_name:
    #                 continue
    #             sport_courses.add(student[attr_name])
        
    #     sql_query = "INSERT INTO sportkurs (KursName, Sporthalle, Lehrkraft, Themenfeld, Wochentag, ifMinAnzahlVorhanden, PlatzanzahlMAX) VALUES "
    #     rows = []
    #     for course in sport_courses:
    #         row = f"('{course}', 'M101', 'Herr Lange', 'Jagd', 'Samstag', 0, 67)"
    #         rows.append(row)
    #     sql_query += ", ".join(rows)

    #     sql_query += ";"

    #     db.execute(sql_query)
    #     db.db_connection.commit()

    
    # def fill_wishes():
    #     for student in student_info:
    #         sql_query = "UPDATE schueler SET "

    #         wishes = list()
    #         for attr_name in student:
    #             if "Wunsch" not in attr_name:
    #                 continue
    #             sport_id = db.output(f"SELECT ID FROM sportkurs WHERE KursName='{student[attr_name]}'")[0][0]
    #             wish = f"{attr_name}_ID = {sport_id}"
    #             wishes.append(wish)
            
    #         sql_query += ", ".join(wishes)

    #         sql_query += f" WHERE VorName = '{student["VorName"]}' AND NachName = '{student["NachName"]}';"
    #         print(sql_query)
    #         db.execute(sql_query)
    #         db.db_connection.commit()

    # fill_wishes()

