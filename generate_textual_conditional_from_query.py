from cerberus import *
from generate_random_query import *

_relational_operation_schema = {
    'field':    {'type': 'string', 'required': True, 'allowed': fields},
    'operator': {'type': 'string', 'required': True, 'allowed': relational_operators},
    'value': {
        'type': 'list',
        'required': True, 
        'minlength': 1, 
        'maxlength': 2,
    },
}

def _get_formated_value(value, type):
    if type == str:
        return f"\"{value}\""
    if type == datetime.date:
        return f"\"{value}\""
    return type(value)

def _parse_relational_query(query):
    field    = query['field']
    operator = query['operator']
    value    = query['value']

    type = types_from_fields[field]

    if len(value) > 1:
        return f"{operator}({field}, {_get_formated_value(value[0], type)}, {_get_formated_value(value[1], type)})"
    return f"{operator}({field}, {_get_formated_value(value[0], type)})"

def generate_conditional_text(query):
    v = Validator(_relational_operation_schema)
    if v.validate(query):
        return _parse_relational_query(query)
    else:
        op_and = query.get('AND', [])
        op_or  = query.get('OR', [])

        ret = ""

        if op_and:
            ret += (f"({' and '.join([generate_conditional_text(q) for q in op_and])})")

        if op_or:
            if op_and:
                ret += " or "
            ret += (f"({' or '.join([generate_conditional_text(q) for q in op_or])})")

        return ret