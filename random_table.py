import random

# random.seed(42)

def _random_between(min, max):
    return random.randint(min, max)

def _create_random_name(min, max):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    ret = []

    len = _random_between(min, max)

    for _ in range(len):
        ret.append(random.choice(alphabet))

    return "".join(ret)

def create_random_table(number_records):
    table = []

    for i in range(number_records):
        table.append({
            "name": _create_random_name(5, 10),
            "age": str(_random_between(10, 99)),
            "height": str(_random_between(1, 2) + random.random()),
            "date": "{0}/{1}/{2}".format(_random_between(1, 31), _random_between(1, 12), _random_between(1980, 2050))
        })

    return table