import openpyxl


EXCEL_PATH = "test/test.xlsx"

# open & parse excel
workbook = openpyxl.load_workbook(EXCEL_PATH)
worksheet = workbook.active

# map of categories with the corresponding cells
categorycell_map = {}

# find cell location of categories
checks_done = False
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

print(students)
