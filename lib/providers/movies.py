import random
from faker.providers import BaseProvider
import csv
import collections


class movies(BaseProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open ('lib/data/movies.csv', 'r') as f:
            reader = csv.DictReader(f)
            video = collections.namedtuple('video', reader.fieldnames)
            self.data = list()
            for row in reader:
                try:
                    self.data.append(video(**row))
                except:
                    ...

    def movie(self):
        return random.choice(self.data)
    


if __name__ == '__main__':
    from faker import Faker
    fake = Faker()
    fake.add_provider(movies)
    for i in range(10):
        print(fake.movie())