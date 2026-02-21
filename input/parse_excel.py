import sys, os
sys.path.append(os.getcwd())
from config.parse_config import Configuration, default_config
from database.database_manager import DataBase
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

    # row of the categories
    categories_row = categorycell_map["VorName"].row

    '''
    ERROR CHECKS
    !!! TODO: raise Errors !!!
    '''
    EXPECTED_CATEGORY_AMOUNT = 9
    if len(categorycell_map) < EXPECTED_CATEGORY_AMOUNT:  # not all categories found
        pass  # error
    if len(categorycell_map) > EXPECTED_CATEGORY_AMOUNT:  # too many categories
        pass  # error

    for category in categorycell_map:
        if categorycell_map[category].row == categories_row:  # expected row idx of categories
            continue
        pass  # error

    # determine range of data
    first_data_row = categories_row + 1  # one below categories row
    last_data_row = last_data_row_tuple[0].row  # get row idx of random cell in the row

    # generate a list of students with mapped attributes
    students = list()
    for row_idx in range(first_data_row, last_data_row+1):
        student_info = dict()
        for category in categorycell_map:
            column_idx = categorycell_map[category].column
            data_cell = worksheet.cell(row=row_idx, column=column_idx)

            student_info[category] = data_cell.value
        students.append(student_info)

    return students


def fill_student_DB(database: DataBase, students_info: dict, config: Configuration) -> None:
    students_DBtable = config.database_tables["schueler"]

    # INITIALIZE sql query: insert values
    sql_query = "INSERT INTO schueler ("
    # APPEND to sql query: attributes of values
    sql_query += ", ".join(attr[0] for attr in students_DBtable["attributes"])  # separates all attr names with a comma
    # APPEND to sql query: initialize giving values
    sql_query += ") VALUES "

    # creates list of values to be added by rows
    rows = list()
    for student in students_info:
        row_query = "("
        attribute_values = list()
        for attribute_name, _ in students_DBtable["attributes"]:  # attr datataype given to _
            attribute_values.append(f"'{student[attribute_name]}'")
        row_query += ", ".join(attribute_values)
        row_query += ")"
        rows.append(row_query)

    # APPEND to sql query: attribute values
    sql_query += ", ".join(rows)

    # FINISH sql query:
    sql_query += ";"

    # EXECUTE sql query
    database.execute(sql_query)
    database.db_connection.commit()



if __name__ == "__main__":
    db = DataBase("database/database.db")
    worksheet = open_excel_sheet("test/test.xlsx")
    student_info = get_student_info(worksheet)

    # fill_student_DB(database=db, students_info=student_info, config=default_config)


    def fill_courses_db():
        sport_courses = set()
        for student in student_info:
            for attr_name in student:
                if "Wunsch" not in attr_name:
                    continue
                sport_courses.add(student[attr_name])
        
        sql_query = "INSERT INTO sportkurs (KursName, Sporthalle, Lehrkraft, Themenfeld, Wochentag, ifMinAnzahlVorhanden, PlatzanzahlMAX) VALUES "
        rows = []
        for course in sport_courses:
            row = f"('{course}', 'M101', 'Herr Lange', 'Jagd', 'Samstag', 0, 67)"
            rows.append(row)
        sql_query += ", ".join(rows)

        sql_query += ";"

        db.execute(sql_query)
        db.db_connection.commit()

    
    def fill_wishes():
        for student in student_info:
            sql_query = "UPDATE schueler SET "

            wishes = list()
            for attr_name in student:
                if "Wunsch" not in attr_name:
                    continue
                sport_id = db.output(f"SELECT ID FROM sportkurs WHERE KursName='{student[attr_name]}'")[0][0]
                wish = f"{attr_name}_ID = {sport_id}"
                wishes.append(wish)
            
            sql_query += ", ".join(wishes)

            sql_query += f" WHERE VorName = '{student["VorName"]}' AND NachName = '{student["NachName"]}';"
            print(sql_query)
            db.execute(sql_query)
            db.db_connection.commit()

    fill_wishes()

