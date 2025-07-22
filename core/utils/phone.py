def format_phone_number(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+91"):
        return phone
    elif phone.startswith("91"):
        return f"+{phone}"
    elif phone.startswith("0"):
        return f"+91{phone[1:]}"
    else:
        return f"+91{phone}"
