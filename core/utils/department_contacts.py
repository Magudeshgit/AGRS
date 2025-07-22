DEPARTMENT_PHONE_NUMBERS = {
    "Academics": "9080783845",
    "Hostel & Facilities": "+918838492241",
    "Administration": "9876543212",
    "Library": "9876543213",
    "Transport": "9876543214",
    "Placement & Training": "9876543215",
    "Examination Cell": "9876543216",
}
def classify_rule_based(title, description):
    text = (title + " " + description).lower()

    categories = {
        "Academics": [
            "subject", "syllabus", "faculty", "lecture", "attendance", "classroom", "notes",
            "internal", "project", "assignment", "mentor", "hod", "staff"
        ],
        "Hostel & Facilities": [
            "hostel", "water", "electricity", "fan", "ac", "food", "mess", "warden",
            "bathroom", "room", "cleaning", "wifi", "noise"
        ],
        "Administration": [
            "id card", "bonafide", "admission", "fee", "scholarship", "principal",
            "certificate", "hall ticket", "transfer", "admin block"
        ],
        "Transport": [
            "bus", "transport", "driver", "delay", "route", "pickup", "drop", "late"
        ],
        "Library": [
            "library", "books", "book", "issue", "return", "fine", "reference", "journal"
        ],
        "Examination Cell": [
            "marks", "result", "exam", "exam cell", "internal", "external", "arrear", "revaluation"
        ],
        "Placement & Training": [
            "placement", "internship", "company", "drive", "training", "mock", "aptitude", "resume"
        ]
    }

    for department, keywords in categories.items():
        if any(kw in text for kw in keywords):
            return department
    return "General"