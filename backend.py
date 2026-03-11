from database.database_manager import *
from input.parse_excel import *
import random


def main(schueler_data: dict, sportkurse_data: dict, sonderkurse_data: dict, sportkurse_zuteilung: dict, sonderkurse_zuteilung: dict):
    # randomize students order for fairness
    studentID_list = schueler_data.keys()
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
                schueler_data[studentID]["wuenscheID_list"].remove(wishID)  # remove wunsch course from priority list
        # all wishes removed
        if not schueler_data[studentID]["wuenscheID_list"]:
            raise Exception("all wishes were removed in step 1)")
    
    """
    2) Überschneidungen
    """
    for zuteilung in sonderkurse_zuteilung.values():
        studentID = zuteilung["schueler_ID"]
        wishesID_list = schueler_data[studentID]["wuenscheID_list"]
        sonderkursID = zuteilung["sonderkurs_ID"]
        sonderkurs_data = sonderkurse_data[sonderkursID]
        # check ueberschneidungen with every wunschkurs
        for wishID in wishesID_list:
            sportkurs_data = sportkurse_data[wishID]
            if sportkurs_data["Wochentag"] != sonderkurs_data["Wochentag"]:
                schueler_data[studentID]["wuenscheID_list"].remove(wishID)  # remove wunsch course from priority list
        # all wishes removed
        if not schueler_data[studentID]["wuenscheID_list"]:
            raise Exception("all wishes were removed in step 2)")
        

if __name__ == "__main__":
    test_schuelerdata = {
        "1": {"wuenscheID_list": [1, 6, 7, 9, 3, ]}
    }
