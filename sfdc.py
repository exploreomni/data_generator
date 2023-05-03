import itertools
from dataclasses import dataclass, field, InitVar
from faker import Faker
from dataclass_csv import dateformat

# from lib.providers import fortune500, sfdc_ids, dates, probability
from lib.providers import companies, dates, probability, sfdc
from lib.table import Table
from lib import helpers
from datetime import datetime, date
import random
from dotenv import load_dotenv

load_dotenv()
import os

DATE_FORMAT = os.environ["DATEFORMAT"]

fake = Faker()
fake.add_provider(sfdc.sfdc_ids)
fake.add_provider(companies.fortune500)
fake.add_provider(dates.dates)
fake.add_provider(probability.probability)

OPWORDS = [
    "marketing team",
    "ad spend",
    "sales team",
    "r&d",
    "Taget Demo" "corporate marketing",
    "product marketing",
    "ad buy",
    "Digital ad buy",
    "Digital initiative",
    "Digital retargeting",
    "Millenial hi-pro buyer targeting",
    "Rebrand",
    "recurring ad placement",
    "Social media campaign",
    "Social media buy",
    "Social media retargeting",
    "Social media targeting",
    "Social media",
    "Lead gen",
    "Promotional campaign",
    "Promo",
    "Event Promotion",
    "Affiliate marketing",
    "Targeted Affiliate marketing",
    "Geo-location targeting",
    "Western digital native ad buy",
    "East coast digital native ad buy",
    "south east / florida ad buy",
    "classic content ad buy",
    "18 - 35 eng ex-US ",
    "35 - 65 eng ex-US ",
    "65+ regional ad buy: soCal, AZ, NV, NM",
    "Default ad roll / zero target low comp rate",
    "Geo spec Primetime default ad roll",
    "High affinity persona, cookie based ID",
    "Custom click through rate - primetime ad roll",
    "Device ID based ad roll, high pro / affinity",
    "Action content propensity",
    "Drama content propensity",
    "Female likely propensity",
    "Male likely propensity",
]


@dataclass
class SFDCUser(metaclass=Table):
    id: str = field(init=False)
    first_name: str = field(default_factory=fake.first_name)
    last_name: str = field(default_factory=fake.last_name)
    email: str = field(init=False)
    role_id: str = field(default_factory=fake.sfdc_role_id)

    def __post_init__(self):
        self.id = SFDCUser.unique("sfdc_user_id", fake.sfdc_user_id)
        self.email = f"{self.first_name}.{self.last_name}@vidly.com"


@dataclass
class Contact(metaclass=Table):
    id: str = field(init=False)
    first_name: str = field(default_factory=fake.first_name)
    last_name: str = field(default_factory=fake.last_name)
    email: str = field(init=False)
    account_id: str = field(init=False)

    def __post_init__(self):
        account: Account = random.choice(Account.instances)
        self.account_id = account.id
        self.email = f"{helpers.email_handle_from_name(self.first_name,self.last_name,random.random())}@{helpers.email_domain_from_url(account.website)}"
        self.id = Contact.unique("sfdc_contact_id", fake.sfdc_contact_id)

    def after_first_run(self):
        ...


@dataclass
@dateformat(DATE_FORMAT)
class Account(metaclass=Table):
    id: str = field(init=False)
    name: str = field(init=False)
    owner_id: str = field(init=False)
    billing_address: str = field(init=False)
    billing_address2: str = field(init=False)
    billing_city: str = field(init=False)
    billing_state: str = field(init=False)
    billing_zip: str = field(init=False)
    billing_county: str = field(init=False)
    employees_c: int = field(init=False)
    revenue_c: int = field(init=False)
    website: str = field(init=False)
    segment: str = field(init=False)
    status: str = field(init=False)
    created_date: datetime = field(init=False)

    def __post_init__(self):
        # hash_key is the key to use to check for uniqueness on an unhashable type, such as a dict
        self.status = "Prospect"
        self.__company__ = Account.unique(
            "__company__", fake.fortune500Company, hash_key="NAME"
        )
        self.name = self.__company__["NAME"]
        self.billing_address = self.__company__["ADDRESS"]
        self.billing_address2 = self.__company__["ADDRESS2"]
        self.billing_city = self.__company__["CITY"]
        self.billing_state = self.__company__["STATE"]
        self.billing_zip = str(self.__company__["ZIP"])
        self.billing_county = self.__company__["COUNTY"]
        self.employees_c = self.__company__["EMPLOYEES"]
        self.revenue_c = self.__company__["REVENUES"]
        self.website = self.__company__["WEBSITE"].lower()
        self.id = Account.unique("sfdc_account_id", fake.sfdc_account_id)
        self.owner_id = SFDCUser.pick_existing("id")
        self.created_date = fake.date_time_between_dates(
            start=datetime(year=2015, month=1, day=1), end=datetime.today()
        )
        if self.employees_c < 100:
            self.segment = "SMB"
        elif self.employees_c < 1000:
            self.segment = "Corporate"
        else:
            self.segment = "Enterprise"
        # self.opportunities = []
        self.opportunities = [
            Opportunity(
                account=self,
                opened_date=fake.date_time_between_dates(
                    start=self.created_date, end=datetime.today()
                ),
            )
            for i in range(fake.poisson(3))
        ]

    def after_first_run(self):
        poisson_result = fake.poisson(
            1
        )  # 1 opportunity per account on average, each ETL instance
        self.opportunities += [
            Opportunity(
                account=self,
                opened_date=fake.date_time_this_quarter(before_today=True),
            )
            for i in range(poisson_result)
        ]


@dataclass
@dateformat(DATE_FORMAT)
class Opportunity(metaclass=Table):
    # id: str = field(init=False) #### THIS IS NEEDED FOR SFDC, UNCOMMENT ME
    id: str = field(default=None)  #### This is needed for vidly core, uncomment me
    value: int = field(default_factory=fake.random_int)
    account_id: str = field(init=False)
    owner_id: str = field(init=False)
    opened_date: date = field(
        default_factory=fake.date_time_recent, metadata={"dateformat": DATE_FORMAT}
    )
    closed_date: date = field(init=False, metadata={"dateformat": DATE_FORMAT})
    name: str = field(init=False)
    status: str = field(init=False)
    stage_name: str = field(init=False)
    forecast_category: str = field(init=False)
    account: InitVar[Account] = None
    opened_date: InitVar[date] = None

    def __post_init__(self, opened_date: date, account: Account):
        if account:
            self.id = Opportunity.unique("id", fake.sfdc_opportunity_id)
            self.owner_id = SFDCUser.pick_existing(
                "id", filter_func=lambda x: x.role_id.endswith("09yOipW000000")
            )
            if not self.opened_date:
                self.opened_date = fake.date_time_between_dates(
                    start=account.created_date, end=datetime.today()
                )
            else:
                self.opened_date = opened_date

            self.account = account
            self.account_id = account.id
            opword = random.choice(OPWORDS)
            opword = f"{opword} {self.opened_date.year}/{self.opened_date.month}"
            self.name = f"{account.name} {opword}"
            self.status = fake.random_element(elements=("Open", "Closed"))
            self.stage_name = fake.random_element(
                elements=(
                    "Qualify",
                    "Develop",
                    "Develop Postive",
                    "Closed Won",
                    "Closed Lost",
                )
            )
            if self.stage_name.startswith("Closed"):
                self.closed_date = fake.date_time_between_dates(
                    start=self.opened_date, end=datetime.today()
                )
                self.forecast_category = self.stage_name
                if self.stage_name == "Closed Won":
                    account.status = "Customer"
            else:
                self.forecast_category = "Pipeline"
                self.closed_date = None

    def after_first_run(self):
        if self.status == "Open":
            if fake.probability(0.5):
                self.status = "Closed"
                self.stage_name = fake.random_element(
                    elements=("Closed Won", "Closed Lost")
                )
                if self.stage_name == "Closed Won":
                    self.forecast_category = "Closed"
                    Account.pick_existing("id", id=self.account_id).status = "Customer"
                self.closed_date = fake.date_time_this_quarter(before_today=True)


if __name__ == "__main__":
    # Should be generated in the correct DAG order
    # SFDCUser.generate(count=fake.poisson(10), load_existing=True)
    # Account.generate(count=fake.poisson(15), load_existing=True)
    # Contact.generate(count=fake.poisson(100), load_existing=True)
    ###
    # SFDCUser.generate(count=fake.poisson(150), load_existing=True)
    # Account.generate(count=fake.poisson(5000), load_existing=True)
    # Contact.generate(count=fake.poisson(10000), load_existing=True)
    # Table.writeall()
    Table.pushall()
