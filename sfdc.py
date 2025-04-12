
import itertools
from dataclasses import dataclass, field, InitVar
from faker import Faker
from dataclass_csv import dateformat

# from lib.providers import fortune500, sfdc_ids, dates, probability
from lib.providers import companies, dates, probability, sfdc
from lib.table import Table
from lib import helpers
from datetime import datetime, date, timedelta
import random
from dotenv import load_dotenv

load_dotenv()
import os

DATE_FORMAT = os.environ.get("DATEFORMAT", "%Y-%m-%d")

fake = Faker()
fake.add_provider(sfdc.sfdc_ids)
fake.add_provider(companies.fortune500)
fake.add_provider(dates.dates)
fake.add_provider(probability.probability)
fake.add_provider(companies.MixedCompanyProvider)

OPWORDS = [
    "marketing team",
    "ad spend",
    "sales team",
    "r&d",
    "Target Demo",
    "corporate marketing",
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
@dateformat(DATE_FORMAT)
class Product(metaclass=Table):
    id: str = field(init=False)
    name: str = field(default_factory=lambda: fake.unique.word().title())

    def __post_init__(self):
        self.id = Product.unique("product_id", fake.uuid4)


@dataclass
@dateformat(DATE_FORMAT)
class SFDCUser(metaclass=Table):
    id: str = field(init=False)
    first_name: str = field(default_factory=fake.first_name)
    last_name: str = field(default_factory=fake.last_name)
    email: str = field(init=False)
    role_id: str = field(default_factory=fake.sfdc_role_id)
    created_date: datetime = field(init=False)
    account_id: str = field(init=False)

    def __post_init__(self):
        account = Account.pick_existing_object()
        self.account_id = account.id
        self.id = SFDCUser.unique("sfdc_user_id", fake.sfdc_user_id)
        self.email = f"{self.first_name}.{self.last_name}@vidly.com"
        self.created_date = fake.date_time_between_dates(
            start=datetime(year=2023, month=1, day=1), end=datetime.today()
        )
    
    def after_first_run(self):
        if not self.created_date:
            self.created_date = fake.date_time_between_dates(
                start=datetime(year=2023, month=1, day=1), end=datetime.today()
            )


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


def random_account_created_date():
    today = datetime.today()
    start_date = datetime(year=2023, month=1, day=1)
    # Triangular distribution (bias toward earlier dates)
    random_days = int(random.triangular(0, (today - start_date).days, 90))
    return start_date + timedelta(days=random_days)

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
    industry: str = field(init=False)
    website: str = field(init=False)
    segment: str = field(init=False)
    status: str = field(init=False)
    created_date: datetime = field(init=False)

    INDUSTRIES = [
        "Technology",
        "Finance",
        "Healthcare",
        "Retail",
        "Manufacturing",
        "Media",
        "Education",
        "Hospitality",
        "Real Estate",
        "Energy",
    ]

    def __post_init__(self):
        self.status = "Prospect"
        self.__company__ = Account.unique("__company__", fake.mixed_company, hash_key="NAME")
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
        self.owner_id = None
        self.created_date = random_account_created_date()

        # Set segment based on provided category from mixed_company
        category = self.__company__["CATEGORY"]
        self.segment = category if category in ("SMB", "MM") else "Enterprise"

        # Assign a random industry
        self.industry = random.choice(Account.INDUSTRIES)

        # Generate associated opportunities
        self.opportunities = [
            Opportunity(
                opened_on=fake.date_time_between_dates(
                    start=self.created_date,
                    end=min(self.created_date + timedelta(days=random.randint(30, 365)), datetime.today())
                ),
                account=self,
            )
            for _ in range(fake.poisson(3))
        ]

    def after_first_run(self):
        # Assign owner_id now that users exist
        if not self.owner_id and SFDCUser.instances:
            self.owner_id = SFDCUser.pick_existing("id")
        
        additional_opps = fake.poisson(1)
        self.opportunities += [
            Opportunity(
                opened_on=fake.date_time_between_dates(
                    start=self.created_date, end=datetime.today()
                ),
                account=self,
            )
            for _ in range(additional_opps)
        ]

        if not self.products:
            self.products = random.sample(Product.instances, random.randint(1, 10))

def generate_opportunity_value():
    # Use a triangular distribution with min=30k, max=100k, mode=50k
    value = random.triangular(30000, 100000, 50000)
    return int(round(value / 1000)) * 1000

@dataclass
@dateformat(DATE_FORMAT)
class Opportunity(metaclass=Table):
    id: str = field(default=None)
    value: int = field(default_factory=generate_opportunity_value)
    account_id: str = field(init=False)
    owner_id: str = field(init=False)
    opened_date: date = field(init=False, metadata={"dateformat": DATE_FORMAT})
    closed_date: date = field(init=False, metadata={"dateformat": DATE_FORMAT})
    name: str = field(init=False)
    status: str = field(init=False)
    stage_name: str = field(init=False)
    forecast_category: str = field(init=False)
    business_type: str = field(init=False)  # New field added here
    opened_on: InitVar[date] = None
    account: InitVar[Account] = None

    def __post_init__(self, opened_on: date, account: Account):
        if account:
            self.id = Opportunity.unique("id", fake.sfdc_opportunity_id)

            # Owner assignment logic
            eligible_users = [u for u in SFDCUser.instances if u.role_id.endswith("09yOipW000000")]
            if eligible_users:
                counts = {u.id: 0 for u in eligible_users}
                for opp in Opportunity.instances:
                    if opp.owner_id in counts:
                        counts[opp.owner_id] += 1
                selected_user = min(eligible_users, key=lambda u: counts[u.id])
                self.owner_id = selected_user.id
            else:
                self.owner_id = None

            # Set opened_date
            self.opened_date = opened_on or fake.date_time_between_dates(
                start=account.created_date, end=datetime.today()
            )

            # Link to account
            self.account = account
            self.account_id = account.id

            # Opportunity name logic
            opword = random.choice(OPWORDS)
            opword = f"{opword} {self.opened_date.year}/{self.opened_date.month}"
            self.name = f"{account.name} {opword}"

            # Stage and status assignment
            self.stage_name = fake.random_element(elements=(
                "Prospecting",
                "Qualification",
                "Needs Analysis",
                "Value Proposition",
                "Negotiation/Review",
                "Closed Won",
                "Closed Lost",
            ))

            if self.stage_name in ("Closed Won", "Closed Lost"):
                self.status = "Closed"
                delay = timedelta(days=random.randint(30, 90))
                self.closed_date = min(self.opened_date + delay, datetime.today())
                self.forecast_category = "Closed"
                if self.stage_name == "Closed Won":
                    account.status = "Customer"
            else:
                self.status = "Open"
                future_delay = timedelta(days=random.randint(15, 90))
                self.closed_date = datetime.today() + future_delay
                self.forecast_category = "Pipeline"

            # Determine business type explicitly:
            if account.status == "Customer":
                # Established customers: mostly Add-On
                self.business_type = random.choices(
                    ["Add-On", "New Business"], weights=[0.8, 0.2]
                )[0]
            else:
                # Prospects: mostly New Business
                self.business_type = random.choices(
                    ["New Business", "Add-On"], weights=[0.9, 0.1]
                )[0]

    def after_first_run(self):
        if self.status == "Open":
            days_open = (datetime.today() - self.opened_date).days
            probability = min(0.2 + 0.01 * max(days_open - 30, 0), 0.95)
            
            if fake.probability(probability):
                self.stage_name = random.choice(["Closed Won", "Closed Lost"])
                self.status = "Closed"
                delay = timedelta(days=random.randint(60, 90))
                self.closed_date = min(self.opened_date + delay, datetime.today())
                self.forecast_category = "Closed"
                
                if self.stage_name == "Closed Won":
                    account = Account.pick_existing("id", id=self.account_id)
                    account.status = "Customer"

@dataclass
@dateformat(DATE_FORMAT)
class Usage(metaclass=Table):
    id: str = field(init=False)
    account_id: str
    user_id: str
    product_id: str
    usage_date: date
    usage_min: int

    def __post_init__(self):
        self.id = Usage.unique("usage_id", fake.uuid4)

def generate_usage(max_days=30):
    start_date = datetime(year=2023, month=1, day=1)
    end_date = datetime.today()

    # Only generate for recent days to control volume
    date_cursor = max(end_date - timedelta(days=max_days), start_date)

    for account in Account.instances:
        if account.status != "Customer":
            continue  # Skip prospects / non-customers

        account_users = [u for u in SFDCUser.instances if u.account_id == account.id]

        while date_cursor <= end_date:
            for user in account_users:
                for product in account.products:
                    baseline = random.randint(10, 120)
                    noise = random.randint(-5, 5)
                    Usage(
                        account_id=account.id,
                        user_id=user.id,
                        product_id=product.id,
                        usage_date=date_cursor.date(),
                        usage_min=max(1, baseline + noise),
                    )
            date_cursor += timedelta(days=1)

if __name__ == "__main__":
#     ...
#     # Should be generated in the correct DAG order:
#     # step 1: ensure Opportunity.id is set to field(init=False)
    Product.generate(count=10, load_existing=True)
    
    Account.generate(count=fake.poisson(1000), load_existing=True)
    SFDCUser.generate(count=fake.poisson(10), load_existing=True)
    Contact.generate(count=fake.poisson(200), load_existing=True)
    generate_usage(max_days=30)
    Table.writeall()