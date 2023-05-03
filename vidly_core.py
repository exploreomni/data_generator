import itertools
from dataclasses import dataclass, field, InitVar
from faker import Faker
from dataclass_csv import dateformat
from lib.providers import dates, probability, address  # , movies
from lib.table import Table
from lib import helpers
from datetime import datetime, timedelta
import random

# from sfdc import Account, Opportunity, SFDCUser
from sfdc import Opportunity

from dotenv import load_dotenv

load_dotenv()
import os

DATE_FORMAT = os.environ["DATEFORMAT"]

fake = Faker()
fake.add_provider(dates.dates)
fake.add_provider(probability.probability)
fake.add_provider(address.address_usa)
# fake.add_provider(movies.movies)


@dataclass
# @dateformat(DATE_FORMAT)
class user(metaclass=Table):
    id: int = field(default_factory=itertools.count(1).__next__)
    first_name: str = field(init=False)
    last_name: str = field(default_factory=fake.last_name)
    signup_date: datetime = field(init=False, metadata={"dateformat": DATE_FORMAT})
    email: str = field(init=False)
    address: str = field(init=False)
    city: str = field(init=False)
    state: str = field(init=False)
    zip: str = field(init=False)
    gender: str = field(init=False)
    age: int = field(init=False)
    status: str = field(init=False)

    def __post_init__(self):
        self.gender = fake.random_element(elements=("M", "F"))
        if self.gender == "M":
            # skew older for the male population to create different demographic characteristics
            self.age = abs(int(fake.gaussian(mu=29, sigma=15)))
            self.first_name = fake.first_name_male()
        else:
            self.age = abs(int(fake.gaussian(mu=33, sigma=15)))
            self.first_name = fake.first_name_female()
        if self.age <= 5:
            self.age = random.randint(5, 25)
        self.email = user.unique("user_email", self.user_email)
        self.signup_date = fake.date_time_between(
            start_date=datetime(2019, 1, 1), end_date=datetime.today()
        )
        addr = fake.population_based_address_factors()
        self.address = fake.unique.street_address()
        self.city = addr["city"]
        self.state = addr["state"]
        self.zip = addr["zip"]
        # 1% initial dropoff rate
        if fake.probability(0.01):
            self.status = "Inactive"
        else:
            self.status = "Active"
            for e in range(fake.poisson(3)):
                Session(
                    force_user=self,
                    session_start=fake.date_time_between_dates(
                        start=self.signup_date, end=datetime.today()
                    ),
                )

    def user_email(self):
        return (
            f"{helpers.email_handle_from_name(self.first_name,self.last_name,random.random())}"
            f"@{helpers.consumer_email_domain()}"
        )

    def after_first_run(self):
        # Generate ongoing activity for users -- uses a 0.5% inactivity rate,
        # and a poisson distribution of 5 sessions per ETL run
        if self.status == "Active":
            if fake.probability(0.005):
                self.status = "Inactive"
            else:
                for e in range(fake.poisson(1)):
                    Session(
                        force_user=self,
                        session_start=fake.date_time_this_week(before_today=True),
                    )


@dataclass
@dateformat(DATE_FORMAT)
class Session(metaclass=Table):
    user_id: int = None
    session_id: str = None
    session_start: datetime = field(
        default_factory=None, metadata={"dateformat": DATE_FORMAT}
    )
    current_time: int = None
    user_agent: str = None
    ip: str = None
    force_user: InitVar[user] = None

    def __post_init__(self, force_user: user = None):
        if force_user:
            u = force_user
        else:
            u: user = random.choice(user.instances)
        self.user_id = u.id
        self.session_id = fake.uuid4()
        if not self.session_start:
            self.session_start = fake.date_time_between(
                start_date=u.signup_date, end_date=datetime.today()
            )
        self.current_time = 0
        self.user_agent: str = fake.user_agent()
        self.ip: str = fake.ipv4()

        for e in range(fake.poisson(20)):
            if e == 0:
                app_events(
                    user_id=self.user_id,
                    event_type="login",
                    event_date=self.session_start,
                    user_agent=self.user_agent,
                    ip_address=self.ip,
                    force_user=u,
                    load_existing=False,
                )
            else:
                app_events(
                    user_id=self.user_id,
                    event_type="watch",
                    event_date=fake.date_time_between(
                        start_date=self.session_start,
                        end_date=self.session_start + timedelta(hours=1),
                    ),
                    user_agent=self.user_agent,
                    ip_address=self.ip,
                    force_user=u,
                    load_existing=False,
                )


@dataclass
@dateformat(DATE_FORMAT)
class videos(metaclass=Table):
    title: str = field(default="")
    id: str = field(default="")
    duration: str = field(default="")
    content_type: str = field(default="")
    description: str = field(default="")
    audio_language: str = field(default="")
    image_url: str = field(default="")
    parenttitle_year: str = field(default="")
    parenttitle_title: str = field(default="")


def nothing():
    pass


@dataclass
@dateformat(DATE_FORMAT)
class app_events(metaclass=Table):
    id: int = field(default_factory=itertools.count(1).__next__)
    user_id: int = field(default_factory=nothing)
    event_type: str = field(default_factory=nothing)
    user_agent: str = field(default_factory=fake.user_agent)
    ip_address: str = field(default_factory=fake.ipv4)
    event_date: datetime = field(
        default_factory=nothing, metadata={"dateformat": DATE_FORMAT}
    )
    ad_play_id: str = field(default_factory=nothing)
    video_id: str = field(default_factory=nothing)
    duration: int = field(init=False)
    force_user: InitVar[user] = None

    def __post_init__(self, force_user: user):
        if not force_user:
            raise Exception("app_events must be initialized with a user")

        if self.event_type == "watch":
            # https://www.imdb.com/video/imdb/vi1462938649/imdb/embed?autoplay=false&width=640
            # random_movie = fake.movie()
            interest_function = None
            # attach a filter function to map propensity to demographics
            if force_user.age < 18:
                if fake.probability(0.2):
                    if force_user.gender == "M":
                        interest_function = (
                            lambda x: "Action" in x.title or "Star Wars" in x.title
                        )
                    elif force_user.gender == "F":
                        interest_function = (
                            lambda x: "Up:" in x.title or "Wall E" in x.title
                        )

            random_movie = videos.pick_existing_object(filter_func=interest_function)

            self.video_id = random_movie.id
            self.duration = random.randint(3, int(random_movie.duration))
            self.ad_play_id = None
            if fake.probability(0.3):
                app_events(
                    user_id=self.user_id,
                    event_type="ad_play",
                    event_date=fake.date_time_between(
                        start_date=self.event_date,
                        end_date=self.event_date + timedelta(seconds=self.duration),
                    ),
                    user_agent=self.user_agent,
                    ip_address=self.ip_address,
                    video_id=self.video_id,
                    force_user=force_user,
                    load_existing=False,
                )

        elif self.event_type == "ad_play":
            self.ad_play_id = Opportunity.pick_existing("id")
            self.duration = random.randint(5, 60)
        else:
            self.ad_play_id = None
            self.video_id = None
            self.duration = None
        # self.event_date = fake.date_time_between(start_date=datetime(2019,1,1), end_date=datetime.today())


# user_billing
# payment methods
# app_events
# ad_plays
# video
# reccomendations
# producers


if __name__ == "__main__":
    ...
    # Step 1: ensure Opportunity.id is set to field(default=None)
    # Step 2: run the following block to generate (daily ~250, keep in mind load existing)?
    # Opportunity(load_existing=True, generate_new=False)
    # videos(load_existing=True, generate_new=False)
    # user.generate(count=fake.poisson(100000), load_existing=True)
    # user.write()
    # app_events.write()

    # Step 3: push to DBs
    # user.push_to_dbs()
    # app_events.push_to_dbs()
    # videos.push_to_dbs()


# TODO: techincally I agreed to link back to https://simplemaps.com/data/us-zips in order to get the zip code data. or could buy it for 199
# TODO: consider using themovieDB for movie data, it has commercial licensing
