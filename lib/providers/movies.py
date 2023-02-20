import random
from faker.providers import BaseProvider
import csv
import collections


class movies(BaseProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open('lib/data/movies.csv', 'r') as f:
            reader = csv.DictReader(f)
            video = collections.namedtuple('video', reader.fieldnames)
            self.data = [video(**row) for row in reader]

    def movie(self):
        return random.choice(self.data)