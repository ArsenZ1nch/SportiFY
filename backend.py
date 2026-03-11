from database.database_manager import *
from input.parse_excel import *
import random


def main(schueler_data: dict, sportkurse_data: dict, sonderkurse_data: dict, sportkurse_zuteilung: dict, sonderkurse_zuteilung: dict):
    # randomize students order for fairness
    studentID_list = list(schueler_data.keys())
    random.shuffle(studentID_list)

    """
    1) semesterspezifische Kurse
    """
    for studentID in studentID_list:
        schueler_info = schueler_data[studentID]
        wishesID_list = schueler_info["wuenscheID_list"]
        # check every wunschkurs
        for wishID in wishesID_list:
            sportkurs_data = sportkurse_data[wishID]
            if schueler_info["Semester"] != sportkurs_data["Semester"]:
                print(f"Student {studentID} has a wish for course {wishID}, semester {sportkurs_data['Semester']} that is not in their semester {schueler_info['Semester']}.")
                schueler_data[studentID]["wuenscheID_list"].remove(wishID)  # remove wunsch course from priority list
        # all wishes removed
        if not schueler_data[studentID]["wuenscheID_list"]:
            raise Exception("all wishes were removed in step 1)")
    
    """
    2) Überschneidungen
    """
    for zuteilung in sonderkurse_zuteilung.values():
        studentID = zuteilung["schueler_ID"]
        schueler_info = schueler_data[studentID]
        wishesID_list = schueler_info["wuenscheID_list"]
        sonderkursID = zuteilung["sonderkurs_ID"]
        sonderkurs_info = sonderkurse_data[sonderkursID]
        # check ueberschneidungen with every wunschkurs
        for wishID in wishesID_list:
            sportkurs_data = sportkurse_data[wishID]
            if (sportkurs_data["Wochentag"] == sonderkurs_info["Wochentag"]) and (schueler_info["Semester"] == zuteilung["Semester"]):
                print(f"Student {studentID} has a wish for course {wishID}, weekday {sportkurs_data['Wochentag']} that overlaps with their assigned sonderkurs {sonderkursID} on weekday {sonderkurs_info['Wochentag']} in semester {sonderkurs_info['Semester']}.")
                schueler_data[studentID]["wuenscheID_list"].remove(wishID)  # remove wunsch course from priority list
        # all wishes removed
        if not schueler_data[studentID]["wuenscheID_list"]:
            raise Exception("all wishes were removed in step 2)")
        

if __name__ == "__main__":
    test_schuelerdata = {
        "1": {"Semester": 1, "wuenscheID_list": [1, 6, 7, 4, 3, 2]},
        "2": {"Semester": 2, "wuenscheID_list": [4, 2, 5, 6, 1, 4]}
    }
    test_sportkurse_data = {
        1: {"Semester": 1, "Wochentag": "Montag"},
        2: {"Semester": 1, "Wochentag": "Dienstag"},
        3: {"Semester": 1, "Wochentag": "Mittwoch"},
        4: {"Semester": 2, "Wochentag": "Montag"},
        5: {"Semester": 2, "Wochentag": "Dienstag"},
        6: {"Semester": 2, "Wochentag": "Mittwoch"},
        7: {"Semester": 2, "Wochentag": "Donnerstag"}
    }
    test_sonderkurse_data = {
        1: {"Semester": 1, "Wochentag": "Montag"},
        2: {"Semester": 1, "Wochentag": "Dienstag"},
        3: {"Semester": 2, "Wochentag": "Mittwoch"},
    }
    test_sonderkurse_zuteilung = {
        1: {"schueler_ID": "1", "sonderkurs_ID": 1, "Semester": 1},
        2: {"schueler_ID": "2", "sonderkurs_ID": 2, "Semester": 2}
    }

    main(test_schuelerdata, test_sportkurse_data, test_sonderkurse_data, {}, test_sonderkurse_zuteilung)
    print(test_schuelerdata)