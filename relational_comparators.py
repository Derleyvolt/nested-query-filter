import re
import datetime

def _format_if_is_date(value):
    if isinstance(value, str) and re.match(r"\d{4}-\d{1,2}-\d{1,2}", value):
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    return value

def gt(target, value):
    value = _format_if_is_date(value)
    return target > value

def gte(target, value):
    value = _format_if_is_date(value)
    return target >= value

def lt(target, value):
    value = _format_if_is_date(value)
    return target < value

def lte(target, value):
    value = _format_if_is_date(value)
    return target <= value

def eq(target, value):
    value = _format_if_is_date(value)
    return target == value

def btw(target, min, max):
    min = _format_if_is_date(min)
    max = _format_if_is_date(max)
    return target >= min and target <= max

def sw(target, value):
    value = _format_if_is_date(value)
    return target.startswith(str(value))

def ew(target, value):
    value = _format_if_is_date(value)
    return target.endswith(str(value))

def ct(target, value):
    value = _format_if_is_date(value)
    return str(value) in target

def nct(target, value):
    value = _format_if_is_date(value)
    return str(value) not in target