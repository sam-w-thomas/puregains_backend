import re


def verify_birth_date(date):
    """
    Verify birth date, returns false if not valid
    :param date:
    :return:
    """
    valid = True
    if not re.match('\d+/\d+/\d+', date):
        valid = False

    return valid


def verify_str(string):
    """
    Verify string, such as name, must not be None. Returns false if not valid
    :param string:
    :return:
    """
    valid = True

    if not isinstance(string, str) or string is None:
        valid = False

    return valid


def verify_str_none(string):
    """
    Verify string, such as name, allows value to be None. Returns false if not valid
    :param string:
    :return:
    """
    valid = True

    if not isinstance(string, str):
        valid = False

    if string is None:
        valid = True

    return valid
