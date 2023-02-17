import random
from faker.providers import BaseProvider
import csv
import collections


class address_usa(BaseProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open('lib/data/zips.csv', 'r') as f:
            reader = csv.DictReader(f)
            zipcode = collections.namedtuple('zipcode', reader.fieldnames)
            self.data = [zipcode(**row) for row in reader]

    def population_based_address_factors(self, state:str=None):
        if state:
            data = [x for x in self.data if x.state == state]
        else:
            data = self.data
        addr = random.choices(data, weights=[int(x.population) for x in data], k=1)
        return {
            'city': addr[0].city,
            'state': addr[0].state_id,
            'zip': addr[0].zip
        }
