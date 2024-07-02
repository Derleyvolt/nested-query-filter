from cerberus import *
import decimal
import datetime

class CustomValidator(Validator):

    # creating new type for decimal, this don't is supported by default in cerberus
    def _validate_type_decimal(self, value):
        return isinstance(value, decimal.Decimal)

class QueryFilter:
    # can be overrided by subclasses
    _relational_operators = {
        # arity is useful to check if the number of values in query is the same as expected
        # for example, the operator "btw" expects 2 values in query
        # it avoids IndexError when trying to access query values.

        # only_string is flag that indicates if the operator works strictly with strings
        "gt": {
            'method': lambda table_data, query_value: table_data > query_value[0],
            'arity': 1,
            'only_string': False,
        }, 
        "lt": {
            'method': lambda table_data, query_value: table_data < query_value[0],
            'arity': 1,
            'only_string': False,
        },
        "eq": {
            'method': lambda table_data, query_value: table_data == query_value[0],
            'arity': 1,
            'only_string': False,
        },
        "neq": {
            'method': lambda table_data, query_value: table_data != query_value[0],
            'arity': 1,
            'only_string': False,
        },
        "gte": {
            'method': lambda table_data, query_value: table_data >= query_value[0],
            'arity': 1,
            'only_string': False,
        },
        "lte": {
            'method': lambda table_data, query_value: table_data <= query_value[0],
            'arity': 1,
            'only_string': False,
        },
        "btw": {
            'method': lambda table_data, query_value: table_data >= query_value[0] and table_data <= query_value[1],
            'arity': 2,
            'only_string': False,
        },
        "ct": {
            'method': lambda table_data, query_value: query_value[0] in str(table_data),
            'arity': 1,
            'only_string': True,
        },
        "nct": {
            'method': lambda table_data, query_value: query_value[0] not in str(table_data),
            'arity': 1,
            'only_string': True,
        },
        "sw": {
            'method': lambda table_data, query_value: str(table_data).startswith(query_value[0]),
            'arity': 1,
            'only_string': True,
        },
        "ew": {
            'method': lambda table_data, query_value: str(table_data).endswith(query_value[0]),
            'arity': 1,
            'only_string': True,
        },
    }

    def __init__(self, query, table):
        self._query = query
        self._table = table

        # should be overrided by subclasses
        # custom_type_converter is useful to convert a string to a custom type, like a date or a boolean
        # for example: you can want to convert a string "1" to a boolean True but you need to explicit this conversion
        # because python doesn't do it automatically, bool("1") and bool("0") is both True.
        self._table_column_types = {
            'name': {
                'type': 'string',  
                'native_type': str,           
                'nullable': False
            },
            'age': {
                'type': 'integer',   
                'native_type': int,           
                'nullable': False
            },
            'height': {
                'type': 'float',   
                'native_type': float,           
                'nullable': False
            },
            'birth_day': {
                'type': 'date',    
                'native_type': datetime.date,         
                'nullable': True,
                'custom_type_converter': lambda x: datetime.datetime.strptime(x, self.get_date_format()).date()
            },
            'posted': {
                'type': 'boolean',    
                'native_type': bool,
                'nullable': False,
                'custom_type_converter': lambda x: x == '1'
            }
        }

    # can be overload if your date format is different
    _date_format = "%Y-%m-%d"

    def get_date_format(self):
        return self._date_format

    def _get_list_types_from_table(self):
        return list(set([value['type'] for value in self._table_column_types.values()]))

    def _get_type_from_table_column(self, column):
        if column not in self._table_column_types:
            raise ValueError("Column '{0}' is not in table".format(column))
        return self._table_column_types[column]['native_type']

    # garantee table consistency in all rows
    # but how it needs to check all rows, it becomes a heavy operation
    def _table_keys_validation(self, table_record):
        schema = {}

        for column, value in self._table_column_types.items():
            schema[column] = {
                'type':     value['type'],
                'nullable': value['nullable'],
                'required': True
            }

        v = CustomValidator(schema, purge_unknown=True)
        if not v.validate(table_record):
            raise ValueError(v.errors)

    def _logical_layer_query_validation(self, query, raise_exception=True):
        logical_op_schema = {
            'AND': {
                'type': 'list',
                'schema': {
                    'required': True,
                    'type': 'dict'
                }
            },

            'OR': {
                'type': 'list',
                'schema': {
                    'required': True,
                    'type': 'dict'
                }
            }
        }

        v = CustomValidator(logical_op_schema, purge_unknown=True)
        if not v.validate(query):
            if raise_exception:
                raise ValueError(v.errors)
            return False
        return True

    # types that query can have are all types that are in the table
    def _relational_layer_query_validation(self, query, type_validation=True, raise_exception=True):
        relational_operation_schema = {
            'field':    {'type': 'string', 'required': True, 'allowed': list(self._table_column_types.keys())},
            'operator': {'type': 'string', 'required': True, 'allowed': list(self._relational_operators.keys())},
            'value': {
                'type': 'list',
                'required': True,
                'minlength': 1,
                'maxlength': 2,
            },
        }

        if type_validation:
            relational_operation_schema['value']['schema'] = {
                'type': self._get_list_types_from_table()
            }

        v = CustomValidator(relational_operation_schema, purge_unknown=True)
        if not v.validate(query):
            if raise_exception:
                raise ValueError(v.errors)
            return False
        return True

    def _get_data(self):
        return self._table

    def _get_operator_by_name(self, operator_name):
        return self._relational_operators[operator_name]['method']

    def _get_arity_by_name(self, operator_name):
        return self._relational_operators[operator_name]['arity']

    def _get_query(self):
        return self._query

    def _normalize_data_type(self):
        query = self._get_query()

        def _normalize_recursive(query):
            if "AND" in query or "OR" in query:
                self._logical_layer_query_validation(query)

                # this point query is a valid dict with AND or OR key
                for key in query.keys():
                    logical_list = query[key]
                    for sub_query in logical_list:
                        _normalize_recursive(sub_query)
            else:
                # garantee that query is a valid dict in field terms but don't
                # check if value types are valid, yet
                self._relational_layer_query_validation(query, type_validation=False)

                # this point is reached when we have a relational operation
                only_string = self._relational_operators[query["operator"]]['only_string']
                values = query["value"]
                type = self._get_type_from_table_column(query["field"])
                for index, value in enumerate(values):
                    # check if operator is strict with strings
                    if not only_string:
                        try:
                            if 'custom_type_converter' in self._table_column_types[query["field"]]:
                                custom_type_converter = self._table_column_types[query["field"]]['custom_type_converter']
                                query["value"][index] = custom_type_converter(value)
                            else:
                                query["value"][index] = type(value)
                        except Exception as e:
                            print(e)
                            raise ValueError("Value '{0}' is not in valid format to be normalized to '{1}'".format(value, type))
                
                # garantee that relational layer query is a valid 
                # in terms of keys and values types
                self._relational_layer_query_validation(query)
            
        _normalize_recursive(query)

    def _execute_relational_comparison(self, operator_name, target_value, entry_values):
        # check if operator has the same arity that entry_values
        if self._get_arity_by_name(operator_name) != len(entry_values):
            raise ValueError("Operator '{0}' expects {1} values".format(operator_name, self._get_arity_by_name(operator_name)))
        return self._get_operator_by_name(operator_name)(target_value, entry_values)

    def _evaluate_relational_query(self, query, table_record):
        target_value = table_record[query["field"]]
        
        # check if current row is None
        # because we can't compare None with any value
        if target_value is None:
            return False
    
        # This point we have valid operation and valid types
        query_values  = query["value"]
        operator_name = query["operator"]

        return self._execute_relational_comparison(operator_name, target_value, query_values)

    def _evaluate(self, sub_query, table_record):
        and_op = sub_query.get("AND", None)
        or_op  = sub_query.get("OR",  None)

        if not and_op and not or_op:
            # here we have a relational query
            # check if table row is valid
            # this check is so heave, so should be used in small tables
            # self._table_keys_validation(table_record)
            return self._evaluate_relational_query(sub_query, table_record)
        
        if and_op is not None and all([self._evaluate(dict, table_record) for dict in and_op]):
            return True
        
        if or_op is not None and any([self._evaluate(dict, table_record) for dict in or_op]):
            return True
        
        return False

    def run_query(self):
        # check if query is empty
        if not self._get_query():
            return self._get_data()

        # normalize data before comparisons
        self._normalize_data_type()
        return list(filter(lambda row: self._evaluate(self._get_query(), row), self._get_data()))
