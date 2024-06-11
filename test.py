import random_table
import generate_textual_conditional_from_query
import generate_random_query
from relational_comparators import *
import query_filter as qf
import random
import time

random.seed(42)

def filter_table_from_hardcoded_comparison(table):
    records = []
    for record in table:
        height    = record['height']
        name      = record['name']
        age       = record['age']
        birth_day = record['birth_day']

        # this is the hardcoded comparison generated automatically
        if (lt(age, 49) and eq(height, 75.93700792755631)) or (sw(name, "bnxcsesxe") or gt(age, 34)):
            records.append(record)
    return records

def compare_results(query_result, real_result):
    if len(query_result) != len(real_result):
        return False

    for i in range(len(query_result)):
        if query_result[i] != real_result[i]:
            return False

    return True

def table_to_file(table):
    with open('table.txt', 'w') as f:
        for record in table:
            record['birth_day'] = str(record['birth_day'])
            f.write(str(record) + '\n')

table = random_table.create_random_table(10000)

query = {
    **generate_random_query.generate_logical_query('AND', 2, 2, 0),
    **generate_random_query.generate_logical_query('OR', 2, 2, 0),
}

# print query as json idented
generate_random_query.show_as_json(query)

start_time = time.time()

# run query
query_result = qf.NestedQueryFilter(query, table).run_query()
# run hardcoded comparison
real_result  = filter_table_from_hardcoded_comparison(table)

# comparase results
print("Equal: ", compare_results(query_result, real_result))
print('Query result length:', len(query_result))
print('Real result length:', len(real_result))

# print textual conditionals
print('\n')
print('Textual conditionals:', generate_textual_conditional_from_query.generate_conditional_text(query))

end_time = time.time()
print("Elapsed time:", end_time - start_time)