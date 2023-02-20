import itertools
from dataclasses import dataclass, field, InitVar
from faker import Faker
from dataclass_csv import dateformat
from lib.providers import dates, probability, address
from lib.table import Table
from lib import helpers
from datetime import datetime
import random
from sfdc import Account

fake = Faker()
fake.add_provider(dates.dates)
fake.add_provider(probability.probability)
fake.add_provider(address.address_usa)
#TODO: pick_existing, filter functionality (helps tie specific records together)
#TODO: create more helper functions for various probability distributions
#TODO: create more helper functions for various geographic distributions (world population distribution, etc)
#TODO: break out a seperate job for other vidly areas
#TODO: create the loader mechanism to send data to the DB


@dataclass
@dateformat('%Y-%m-%dT%H:%M:%S.%fZ')
class user(metaclass=Table):
    id: int = field(default_factory=itertools.count(1).__next__)
    first_name: str = field(init=False)
    last_name: str = field(default_factory=fake.last_name)
    signup_date: datetime = field(init=False)
    email: str = field(init=False)
    address: str = field(init=False)
    city: str = field(init=False)
    state: str = field(init=False)
    zip: str = field(init=False)
    gender: str = field(init=False)
    age: int = field(init=False)

    def __post_init__(self):
        self.gender = fake.random_element(elements=('M','F'))
        if self.gender == 'M':
            #skew older for the male population to create different demographic characteristics
            self.age = abs(int(fake.gaussian(mu=29, sigma=15)))
            self.first_name = fake.first_name_male()
        else:
            self.age = abs(int(fake.gaussian(mu=33, sigma=15)))
            self.first_name = fake.first_name_female()

        self.email = user.unique('user_email', self.user_email)
        self.signup_date = fake.date_time_between(start_date=datetime(2019,1,1), end_date='now')
        addr = fake.population_based_address_factors()
        self.address = fake.unique.street_address()
        self.city = addr['city']
        self.state = addr['state']
        self.zip = addr['zip']

    def user_email(self):
        return (f'{helpers.email_handle_from_name(self.first_name,self.last_name,random.random())}'
                f'@{helpers.consumer_email_domain()}')

    def after_first_run(self):
        ...




# user_billing 
# payment methods
# app_events
# ad_plays
# video
# reccomendations
# producers


if __name__ == '__main__':
    # Account(load_existing=True, generate_new=False)
    for i in range(fake.poisson(500)):
        user(load_existing=True)

    Table.writeall()


#TODO: techincally I agreed to link back to https://simplemaps.com/data/us-zips in order to get the zip code data. or could buy it for 199
#TODO: consider using themovieDB for movie data, it has commercial licensing