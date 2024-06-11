import random
import datetime
import calendar

class RandomService:
    def __init__(self, seed=None):
        if seed:
            random.seed(seed)

    def get_random_intenger_between(self, min, max):
        return random.randint(min, max)

    def get_random_string(self, min, max):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        ret = []

        len = self.get_random_intenger_between(min, max)

        for _ in range(len):
            ret.append(random.choice(alphabet))

        return "".join(ret)
    
    def str_date_to_native_date(self, date):
        try:
            return datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Must be YYYY-MM-DD")

    def get_random_date(self, min_year = 1970, max_year = 2060):
        if min_year < 0:
            raise ValueError("min_year must be greater than 0")
        if max_year < 0:
            raise ValueError("max_year must be greater than 0")
        if min_year > max_year:
            raise ValueError("min_year must be less than or equal max_year")
        
        year  = self.get_random_intenger_between(min_year, max_year)
        month = self.get_random_intenger_between(1, 12)
        day   = self.get_random_intenger_between(1, calendar.monthrange(year, month)[1])

        return self.str_date_to_native_date(
            "{2}-{1}-{0}".format(day, month, year))

    def get_random_date_between(self, min, max):
        min = self.str_date_to_native_date(min)
        max = self.str_date_to_native_date(max)

        if min > max:
            raise ValueError("min must be less than or equal max")
        # get difference between dates in days
        days = self.get_random_intenger_between(1, (max - min).days)
        return min + datetime.timedelta(days=days)

    def get_random_date_pair_min_max(self, max_distance_days=5000):
        if max_distance_days <= 0:
            raise ValueError("max_distance_days must be greater than 0")
        min_date = self.get_random_date()
        max_date = min_date + datetime.timedelta(days=self.get_random_intenger_between(1, max_distance_days))
        return min_date, max_date
    
    def get_random_decimal_between(self, min, max):
        integer = self.get_random_intenger_between(min, max)
        return integer + random.random()
    
random_service = RandomService()