import datetime
import json
from random_services import *

relational_operators = ['gt', 'gte', 'lt', 'lte', 'eq', 'neq', 'btw', 'sw', 'ew', 'ct', 'nct']
fields = ['name', 'age', 'height', 'birth_day']

relational_operators_suitable_fields = {
    'name':       ['eq', 'neq', 'sw', 'ew',  'ct', 'nct'],
    'age':        ['gt', 'gte', 'lt', 'lte', 'eq', 'btw'],
    'height':     ['gt', 'gte', 'lt', 'lte', 'eq', 'btw'],
    'birth_day':  ['gt', 'gte', 'lt', 'lte', 'eq', 'btw'],
}

_types_from_fields = {
    'name':        str,
    'age':         int,
    'height':      float,
    'birth_day':  datetime.date,
}


def generate_value_from_operator_and_field(operator, field):
    type = _types_from_fields[field]

    if type == str:
        return [random_service.get_random_string(5, 10)]
    elif type == int:
        if operator == 'btw':
            min = random_service.get_random_intenger_between(1, 100)
            max = min + random_service.get_random_intenger_between(1, 20)
            return [str(min), (max)]
        else:
            return [str(random_service.get_random_intenger_between(1, 100))]
    elif type == float:
        if operator == 'btw':
            min = random_service.get_random_decimal_between(1, 100)
            max = min + random_service.get_random_decimal_between(1, 20)
            return [str(min), str(max)]
        else:
            return [str(random_service.get_random_decimal_between(1, 100))]
    elif type == datetime.date:
        if operator == 'btw':
            min, max = random_service.get_random_date_pair_min_max()
            return [str(min), str(max)]
        else:
            return [str(random_service.get_random_date())]

def generate_relational_query():
    query = {}
    query['field']    = random.choice(fields)
    query['operator'] = random.choice(relational_operators_suitable_fields[query['field']])
    query['value']    = generate_value_from_operator_and_field(query['operator'], query['field'])
    return query

def generate_logical_query(type, min_count_relational_queries=2, max_count_relational_queries=5, depth=0):
    query = {}
    query[type] = []
    for _ in range(
                    random_service.get_random_intenger_between(
                        min_count_relational_queries, 
                        max_count_relational_queries
                )):
        sub_query = generate_relational_query() if depth == 0 else (
                        generate_logical_query(random.choice(['OR', 'AND']), 
                                                min_count_relational_queries, 
                                                max_count_relational_queries, depth-1)
                    )
        query[type].append(sub_query)
    return query

def show_as_json(query):
    print(json.dumps(query, indent=2))