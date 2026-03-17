from database.database_manager import *
from input.parse_excel import *
import random


def depracated(student_data: dict, sport_courses_data: dict, special_courses_data: dict, special_assignment_data: dict):
    # copy dicts to not change arguments directly
    student_data = student_data.copy()
    sport_courses_data = sport_courses_data.copy()
    special_courses_data = special_courses_data.copy()
    special_assignment_data = special_assignment_data.copy()

    # randomize students order for fairness
    studentID_list = list(student_data.keys())
    random.shuffle(studentID_list)

    """
    1) semesterspezifische Kurse
    """
    for student_ID in studentID_list:
        student_info = student_data[student_ID]
        wishesID_list = student_info["wuenscheID_list"]
        # check every wunschkurs
        for wish_ID in wishesID_list:
            sport_course_info = sport_courses_data[wish_ID]
            if student_info["Semester"] != sport_course_info["Semester"]:
                print(f"Student {student_ID} has a wish for course {wish_ID}, semester {sport_course_info['Semester']} that is not in their semester {student_info['Semester']}.")
                student_data[student_ID]["wuenscheID_list"].remove(wish_ID)  # remove wunsch course from priority list
        # all wishes removed
        if not student_data[student_ID]["wuenscheID_list"]:
            raise Exception("all wishes were removed in step 1)")
    
    """
    2) Überschneidungen
    """
    for assignment_info in special_assignment_data.values():
        student_ID = assignment_info["schueler_ID"]
        student_info = student_data[student_ID]
        wishesID_list = student_info["wuenscheID_list"]
        special_course_ID = assignment_info["sonderkurs_ID"]
        special_course_info = special_courses_data[special_course_ID]
        # check ueberschneidungen with every wunschkurs
        for wish_ID in wishesID_list:
            sport_course_info = sport_courses_data[wish_ID]
            if (sport_course_info["Wochentag"] == special_course_info["Wochentag"]) and (student_info["Semester"] == assignment_info["Semester"]):
                print(f"Student {student_ID} has a wish for course {wish_ID}, weekday {sport_course_info['Wochentag']} that overlaps with their assigned sonderkurs {special_course_ID} on weekday {special_course_info['Wochentag']} in semester {special_course_info['Semester']}.")
                student_data[student_ID]["wuenscheID_list"].remove(wish_ID)  # remove wunsch course from priority list
        # all wishes removed
        if not student_data[student_ID]["wuenscheID_list"]:
            raise Exception("all wishes were removed in step 2)")
    
    """
    3) Felderdeckung
    """
    for student_ID in studentID_list:
        student_info = student_data[student_ID]
        student_semester = student_info["Semester"]
        if student_semester == 1:  # skip student if in 1st semester
            continue

        # check themenfelder
        # for assignment_semester in range(1, student_semester)

        wishesID_list = student_info["wuenscheID_list"]
        for wish_ID in wishesID_list:
            themenfeld = sport_courses_data[wish_ID]["Themenfeld"]

        # generate a map of unique themenfelder with corresponding wish IDs and their priority
        themenfelder_wishes_map = dict()
        for priority_idx, wish_ID in enumerate(wishesID_list):
            themenfeld = sport_courses_data[wish_ID]["Themenfeld"]
            wish_priority_map = {wish_ID: priority_idx}
            if themenfeld not in themenfelder_wishes_map:
                themenfelder_wishes_map[themenfeld] = [wish_priority_map]
            else:
                themenfelder_wishes_map[themenfeld].append(wish_priority_map)
        print(themenfelder_wishes_map)

        # if semester == 1 or semester == 2:  # prioritize different themenfelder if in q1 or q2


def main(database: DataBase):
    students_table = database.fetch_table("schueler")
    sport_courses_table = database.fetch_table("sportkurs")
    spec_courses_table = database.fetch_table("sonderkurs")
    sport_assignment_table = database.fetch_table("sportkurse_zuteilung")
    spec_assignment_table = database.fetch_table("sonderkurse_zuteilung")

    # randomize student order for fairness
    out = database.single_select(table=students_table, columns=["ID"])
    students_ID_list = [out_row[0] for out_row in out]  # convert tuple items to single numbers
    random.shuffle(students_ID_list)
    
    """
    1) semesterspezifische Kurse
    """
    for student_ID in students_ID_list:
        out = database.single_select(table=students_table, columns=["Semester", "Wunsch1_ID", "Wunsch2_ID", "Wunsch3_ID", "Wunsch4_ID", "Wunsch5_ID", "Wunsch6_ID"], where_constraint=f"ID={student_ID}")
        print(out)
        student_info = student_data[student_ID]
        wishesID_list = student_info["wuenscheID_list"]
        # check every wunschkurs
        for wish_ID in wishesID_list:
            sport_course_info = sport_courses_data[wish_ID]
            if student_info["Semester"] != sport_course_info["Semester"]:
                print(f"Student {student_ID} has a wish for course {wish_ID}, semester {sport_course_info['Semester']} that is not in their semester {student_info['Semester']}.")
                student_data[student_ID]["wuenscheID_list"].remove(wish_ID)  # remove wunsch course from priority list
        # all wishes removed
        if not student_data[student_ID]["wuenscheID_list"]:
            raise Exception("all wishes were removed in step 1)")


            
        

if __name__ == "__main__":
    test_schuelerdata = {
        1: {"Semester": 1, "wuenscheID_list": [1, 6, 7, 4, 3, 2]},
        2: {"Semester": 2, "wuenscheID_list": [4, 2, 5, 6, 1, 3]}
    }
    test_sportkurse_data = {
        1: {"Semester": 1, "Wochentag": "Montag", "Themenfeld": "Bewegen"},
        2: {"Semester": 1, "Wochentag": "Dienstag", "Themenfeld": "Bewegen"},
        3: {"Semester": 1, "Wochentag": "Mittwoch", "Themenfeld": "Ball"},
        4: {"Semester": 2, "Wochentag": "Montag", "Themenfeld": "Ball"},
        5: {"Semester": 2, "Wochentag": "Dienstag", "Themenfeld": "Ball"},
        6: {"Semester": 2, "Wochentag": "Mittwoch", "Themenfeld": "Bewegen"},
        7: {"Semester": 2, "Wochentag": "Donnerstag", "Themenfeld": "Schwimmen"}
    }
    test_sonderkurse_data = {
        1: {"Semester": 1, "Wochentag": "Montag"},
        2: {"Semester": 1, "Wochentag": "Dienstag"},
        3: {"Semester": 2, "Wochentag": "Mittwoch"},
    }
    test_sonderkurse_zuteilung = {
        1: {"schueler_ID": 1, "sonderkurs_ID": 1, "Semester": 1},
        2: {"schueler_ID": 2, "sonderkurs_ID": 2, "Semester": 2}
    }

    db = DataBase("test/test.db")
    main(db)
