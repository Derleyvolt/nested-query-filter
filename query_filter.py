import random_table as ct

TABLE_LENGTH = 10000

class IQueryFilter:
    _operators = {
        # arity is usefull to check if the number of values in query is the same as expected
        # for example, the operator "btw" expects 2 values in query
        # it avoids IndexError when trying to access query values
        "gt": {
            'method': lambda table_data, query_value: table_data > query_value[0],
            'arity': 1,
        }, 
        "lt": {
            'method': lambda table_data, query_value: table_data < query_value[0],
            'arity': 1,
        },
        "eq": {
            'method': lambda table_data, query_value: table_data == query_value[0],
            'arity': 1,
        },
        "neq": {
            'method': lambda table_data, query_value: table_data != query_value[0],
            'arity': 1,
        },
        "gte": {
            'method': lambda table_data, query_value: table_data >= query_value[0],
            'arity': 1,
        },
        "lte": {
            'method': lambda table_data, query_value: table_data <= query_value[0],
            'arity': 1,
        },
        "btw": {
            'method': lambda table_data, query_value: table_data >= query_value[0] and table_data <= query_value[1],
            'arity': 2,
        },
        "in": {
            'method': lambda table_data, query_value: query_value[0] in table_data,
            'arity': 1
        },
        "nin": {
            'method': lambda table_data, query_value: query_value[0] not in table_data,
            'arity': 1,
        },
        "sw": {
            'method': lambda table_data, query_value: table_data.startswith(query_value[0]),
            'arity': 1,
        },
        "ew": {
            'method': lambda table_data, query_value: table_data.endswith(query_value[0]),
            'arity': 1,
        },
    }

    # used to verify if the key is valid in table
    _table_keys = [
        'number', 
        'account', 
        'favorecido', 
        'debit', 
        'credit', 
        'balance', 
        'competencia', 
        'balance_type', 
        'document', 
        'posted', 
        'date', 
        'payment_date', 
        'note'
    ]

    # check if key is valid in table
    def _valid_table_keys(self, key):
        if key not in self._table_keys:
            raise KeyError("Key '{0}' not found in table keys".format(key))

    def _get_data(self):
        return self._table

    def _get_operator_by_name(self, operator_name):
        if operator_name not in self._operators:
            raise ValueError("Operator '{0}' not founded".format(operator_name))
        return self._operators[operator_name]['method']

    def _get_arity_by_name(self, operator_name):
        if operator_name not in self._operators:
            raise ValueError("Operator '{0}' not founded".format(operator_name))
        return self._operators[operator_name]['arity']

    def _get_query(self):
        return self._query

    # should be overriden to normalize data before comparison
    # it normalize both data and return them
    # this method receive both target and entry_value because
    # some normalizations need to use both to get normalized
    def _normalize_data(self, target_value, entry_values, field_name):
        return [target_value, entry_values]

    def _operator_method(self, operator_name, target_value, entry_values):
        # check if operator has the same arity that entry_values
        if self._get_arity_by_name(operator_name) != len(entry_values):
            raise ValueError("Operator '{0}' expects {1} values".format(operator_name, self._get_arity_by_name(operator_name)))
        return self._get_operator_by_name(operator_name)(target_value, entry_values)

    # check if operation is a dict with expected keys 
    def _operation_dict_validation(self, operation_dict):
        if not isinstance(operation_dict, dict):
            raise TypeError("Operation is not a dict")
        
        if "field" not in operation_dict:
            raise KeyError("Field key not found in operation dict")
        
        if "operator" not in operation_dict:
            raise KeyError("Operator key not found in operation dict")
        
        if "value" not in operation_dict:
            raise KeyError("Value key not found in operation dict")

        self._operation_fields_validation(operation_dict)

    # check if every field in operation dict is a expected type
    def _operation_fields_validation(self, operation_dict):
        if not isinstance(operation_dict["field"], str):
            raise TypeError("Field is not a string")
        
        if not isinstance(operation_dict["operator"], str):
            raise TypeError("Operator is not a string")
        
        if not isinstance(operation_dict["value"], list):
            raise TypeError("Value is not a list")

        for value in operation_dict["value"]:
            if not isinstance(value, (str)):
                raise TypeError("Value is not a str")

    # operation_dict is a valid dict but there is no garantee that
    # your fields are valid
    def _evaluate_operation(self, operation_query, table_record):
        # check if key exists in table
        self._valid_table_keys(operation_query["field"])

        target = table_record[operation_query["field"]]

        # normalize both data
        norm_target_value, norm_entry_values = self._normalize_data(
                                                target, 
                                                operation_query["value"],
                                                operation_query["field"]
                                            )

        return self._operator_method(operation_query["operator"], norm_target_value, norm_entry_values)

    def _evaluate(self, query, table_record):
        and_op = query.get("AND")
        or_op  = query.get("OR")

        # then we have a operation
        if not and_op and not or_op:
            self._operation_dict_validation(query)
            return self._evaluate_operation(query, table_record)
        
        if and_op and all([self._evaluate(dict, table_record) for dict in and_op]):
            return True
        
        if or_op and any([self._evaluate(dict, table_record) for dict in or_op]):
            return True
        
        return False

    def evaluate(self):
        ret = []
        for row in self._get_data():
            if self._evaluate(self._get_query(), row):
                ret.append(row)
        return ret

class NestedQueryFilter(IQueryFilter):
    _table_keys = [
        'name', 
        'age', 
        'height', 
        'date', 
    ]

    def __init__(self, filter_dict, table):
        self._query = filter_dict
        self._table = table

        # self._normalize_data_method = {
        #     "payment_date": self.normalize_date,
        #     "date":   self.normalize_date,
        #     "debit":  self.normalize_decimal,
        #     "credit": self.normalize_decimal,
        #     "number": self.normalize_integer,
        # }

        self._normalize_data_method = {
            "date": self.normalize_date,
            "age":  self.normalize_integer,
            "address": self.normalize_decimal,
        }

    @staticmethod
    def _normalize_integer(target_value, entry_value):
        if len(target_value) > len(entry_value):
            entry_value = entry_value.zfill(len(target_value))
        elif len(entry_value) > len(target_value):
            target_value = target_value.zfill(len(entry_value))

        return [target_value, entry_value]

    # normalize integer values to be properly compared as string
    # expects that entry_values is a list with at most 2 elements
    @staticmethod
    def normalize_integer(target_value, entry_values):
        if len(entry_values) > 1:
            entry_values = NestedQueryFilter._normalize_integer(entry_values[0], entry_values[1])

        for index, value in enumerate(entry_values):
            target_value, entry_values[index] = NestedQueryFilter._normalize_integer(target_value, value)

        return [target_value, list(map(lambda x: x, entry_values))]

    # normalize decimal values to be properly compared as string
    # expects that entry_values is a list with at most 2 elements
    @staticmethod
    def normalize_decimal(target_value, entry_values):
        def _normalize_decimal(target_value, entry_value):
            target_parts = target_value.split('.')
            value_parts = entry_value.split('.')

            target_parts[0], value_parts[0] = NestedQueryFilter._normalize_integer(target_parts[0], value_parts[0])

            def _normalize_decimal_part(target_decimal, value_decimal):
                if len(target_decimal) > len(value_decimal):
                    value_decimal = value_decimal.ljust(len(target_decimal), '0')
                elif len(value_decimal) > len(target_decimal):
                    target_decimal = target_decimal.ljust(len(value_decimal), '0')
                
                return target_decimal, value_decimal

            target_parts[1], value_parts[1] = _normalize_decimal_part(target_parts[1], value_parts[1])

            return ['.'.join(target_parts), '.'.join(value_parts)]

        if len(entry_values) > 1:
            entry_values = _normalize_decimal(entry_values[0], entry_values[1])

        for index, value in enumerate(entry_values):
            target_value, entry_values[index] = _normalize_decimal(target_value, value)

        return [target_value, list(map(lambda x: x, entry_values))]

    # expect that date format is dd/mm/yyyy
    # expects that entry_values is a list with at most 2 elements
    @staticmethod
    def normalize_date(target_value, entry_values):
        def _normalize_date(target_value, entry_value):
            target_parts = target_value.split('/')
            value_parts = entry_value.split('/')

            # garantee that every part of the date has the same length
            target_parts[0], value_parts[0] = NestedQueryFilter._normalize_integer(target_parts[0], value_parts[0])
            target_parts[1], value_parts[1] = NestedQueryFilter._normalize_integer(target_parts[1], value_parts[1])
            target_parts[2], value_parts[2] = NestedQueryFilter._normalize_integer(target_parts[2], value_parts[2])

            return ['/'.join(target_parts), '/'.join(value_parts)]

        if len(entry_values) > 1:
            entry_values = _normalize_date(entry_values[0], entry_values[1])

        for index, value in enumerate(entry_values):
            target_value, entry_values[index] = _normalize_date(target_value, value)

        return ['/'.join(reversed(target_value.split('/'))), list(map(lambda x: '/'.join(reversed(x.split('/'))), entry_values))]

    def _normalize_data(self, target_value, entry_values, field_name):
        if field_name in self._normalize_data_method:
            return self._normalize_data_method[field_name](target_value, entry_values)
        return [target_value, entry_values]

# table with random data
table = ct.create_random_table(TABLE_LENGTH)

query = {
    "AND": [
        {
            "field": "age",
            "operator": "btw",
            "value": ['10', '60']
        }, 
        {
            "field": "date",
            "operator": "btw",
            "value": ["01/01/2024", "01/01/2025"]
        },
        {
            "OR": [
                {
                    "field": "name",
                    "operator": "in",
                    "value": ["ab"]
                },
                {
                    "field": "name",
                    "operator": "eq",
                    "value": ["daxihhexdv"]
                }
            ]
        }
    ],
    "OR": [
        {
            "AND": [
                {
                    "field": "age",
                    "operator": "lte",
                    "value": ['71']
                },
                {
                    "field": "name",
                    "operator": "sw",
                    "value": ["a"]
                },
                {
                    "field": "name",
                    "operator": "ew",
                    "value": ["a"]
                }
            ]
        }
    ]
}

# comparator function to test if a row is valid
def comparator(row):
    [date, my_date] = NestedQueryFilter.normalize_date(row["date"], ["01/01/2024", "01/01/2025"])
    if (row["age"] >= '10' and row["age"] <= '60' and date >= my_date[0] and date <= my_date[1] 
        and ("ab" in row["name"] or row["name"] == "daxihhexdv") or (row["age"] <= '71' and row["name"].startswith("a") and row["name"].endswith("a"))):
        return True
    return False

# naive test to compare with the result of NestedQueryFilter
def naive_test(comparator):
    ret= []
    for row in table:
        if comparator(row):
            ret.append(row)
    return ret

# compare two lists
def compare_list(l1, l2):
    if len(l1) != len(l2):
        return False
    for i in range(len(l1)):
        if l1[i] != l2[i]:
            return False
    return True

list_evaluated = NestedQueryFilter(query, table).evaluate()

real = naive_test(comparator)

print(list_evaluated)
print(real)

print("ARE EQUAL:", "Yes" if compare_list(real, list_evaluated) else "NO")