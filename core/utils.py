def classify_department(text):
    text = text.lower()
    if "exam" in text or "marks" in text or "class" in text:
        return "academics"
    elif "fees" in text or "certificate" in text or "id card" in text:
        return "admin"
    elif "hostel" in text or "water" in text or "cleaning" in text:
        return "facility"
    else:
        return "admin"

def get_staff_department(username):
    mapping = {
        'hostelstaff': 'Hostel & Facilities',
        'academicstaff': 'Academics',
        'examcell': 'Examination Cell',
        'placementstaff': 'Placement & Training',
        'librarian': 'Library',
        'transportadmin': 'Transport',
        'adminstaff': 'Administration',
    }
    return mapping.get(username.lower(), None)
