import re

def extract_phone(text):
    """
    Extracts a phone number from the given text.
    Supports different formats including country codes.
    """
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?(?:\d{10}|\d{3}[-.\s]\d{3}[-.\s]\d{4})"
    phones = re.findall(phone_pattern, text)

    valid_phones = [num for num in phones if re.sub(r'\D', '', num)[-10:].isdigit()]
    return valid_phones[0] if valid_phones else "No phone number found"
