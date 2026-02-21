import openpyxl


if __name__ == "__main__":
    from openpyxl import Workbook

    EXCEL_PATH = "test/test.xlsx"
    workbook = openpyxl.load_workbook(EXCEL_PATH)
    worksheet = workbook.active

    for column in worksheet.columns:
        for cell in column:
            print(cell, cell.value)
