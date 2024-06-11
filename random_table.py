from random_services import *

def create_random_table(number_records):
    table = []

    for i in range(number_records):
        table.append({
            "name": random_service.get_random_string(5, 10),
            "age": random_service.get_random_intenger_between(1, 1000),
            "height": random_service.get_random_decimal_between(1, 1000),
            "birth_day": random_service.get_random_date(),
        })

    return table
