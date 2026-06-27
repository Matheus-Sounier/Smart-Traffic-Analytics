import re

_MERCOSUL = re.compile(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$')  # ABC1D23
_ANTIGA   = re.compile(r'^[A-Z]{3}[0-9]{4}$')             # ABC1234

_CHAR_TO_INT = {'O': '0', 'I': '1', 'J': '3', 'A': '4', 'G': '6', 'S': '5'}
_INT_TO_CHAR = {'0': 'O', '1': 'I', '3': 'J', '4': 'A', '6': 'G', '5': 'S'}

def format_license(text):
    """
    Fixes common OCR mix-ups based on character position
    """
    if len(text) != 7:
        return text

# L L L N L N N
# L L L N N N N
    mapping = {
        0: _INT_TO_CHAR,
        1: _INT_TO_CHAR,
        2: _INT_TO_CHAR,
        3: _CHAR_TO_INT,
        4: _INT_TO_CHAR,
        5: _CHAR_TO_INT,
        6: _CHAR_TO_INT,
    }
    result = ''
    for i, char in enumerate(text):
        result += mapping[i].get(char, char) or char
    return result

def license_complies_format(text):
    """
    Checks if the license plate matches the Brazilian pattern
    """
    return bool(_MERCOSUL.match(text) or _ANTIGA.match(text))

def validate_plate(text):
    """
    Formats and validates the plate
    """
    text = text.upper().replace(' ', '')

    if len(text) < 6:
        return None, False

    formatted = format_license(text)
    is_valid = license_complies_format(formatted)
    return formatted, is_valid