
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

PRODUCT_NAMES = [
    "Core Platform",
    "Data API",
    "User Analytics",
    "Admin Dashboard",
    "Mobile SDK",
    "Billing Engine",
    "Customer Portal",
    "Notification Service",
    "Reporting Suite",
    "Authentication Module",
]


REGIONS = ["West", "East", "Central"]

@dataclass
@dateformat(DATE_FORMAT)
class SFDCUser(metaclass=Table):
    id: str = field(init=False)
    first_name: str = field(default_factory=fake.first_name)
    last_name: str = field(default_factory=fake.last_name)
    email: str = field(init=False)
    region: str = field(init=False)
    role_id: str = field(default_factory=fake.sfdc_role_id)
    created_date: datetime = field(init=False)

    def __post_init__(self):
        self.id = SFDCUser.unique("sfdc_user_id", fake.sfdc_user_id)
        self.email = f"{self.first_name}.{self.last_name}@vidly.com"
        self.region = random.choice(REGIONS)
        self.created_date = fake.date_time_between_dates(
            start=datetime(year=2023, month=1, day=1), end=datetime.today()
        )

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
        "Technology", "Finance", "Healthcare", "Retail", "Manufacturing",
        "Media", "Education", "Hospitality", "Real Estate", "Energy",
    ]

    def __post_init__(self):
        self.status = "Prospect"
        self.owner_id = None  # Delay until after_all_generated()
        self.products = []    # Delay until after_all_generated()

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
        self.created_date = random_account_created_date()

        # Set segment
        category = self.__company__["CATEGORY"]
        self.segment = category if category in ("SMB", "MM") else "Enterprise"

        # Assign industry
        self.industry = random.choice(Account.INDUSTRIES)

        # Generate initial Opportunities
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
        # Generate extra Opps (local logic only)
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

    def after_all_generated(self):
        # Assign owner_id now that Users exist
        if not self.owner_id:
            self.owner_id = random.choice(SFDCUser.instances).id

        # Ensure the owner_id matches the first Opportunity's owner_id
        if self.opportunities:
            self.owner_id = self.opportunities[0].owner_id

        self.products = random.sample(PRODUCT_NAMES, random.randint(1, 10))

        # Assign biased weights: one or two products get heavy weight
        num_products = len(self.products)
        weights = [random.expovariate(1.0) for _ in range(num_products)]
        total = sum(weights)
        self.product_weights = [w / total for w in weights]  # Normalize to sum to 1

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
                    account = Account.pick_existing("id", self.account_id)
                    account.status = "Customer"
        
        # # Generate historical snapshots for the opportunity
        # snapshot_dates = generate_daily_snapshots(self.opened_date, self.closed_date)
        
        # for snapshot_date in snapshot_dates:
        #     OpportunityHistory(opportunity=self, snapshot_date=snapshot_date)


def generate_daily_snapshots(opened_date, closed_date):
    # Generate a list of dates from opened_date to closed_date (inclusive)
    return [opened_date + timedelta(days=i) for i in range((closed_date - opened_date).days + 1)]

# @dataclass
# @dateformat(DATE_FORMAT)
# class OpportunityHistory(metaclass=Table):
#     id: str = field(init=False)
#     opportunity_id: str = field(init=False)
#     snapshot_date: datetime = field(init=False)
#     value: int = field(init=False)
#     account_id: str = field(init=False)
#     owner_id: str = field(init=False)
#     opened_date: date = field(init=False, metadata={"dateformat": DATE_FORMAT})
#     closed_date: date = field(init=False, metadata={"dateformat": DATE_FORMAT})
#     name: str = field(init=False)
#     status: str = field(init=False)
#     stage_name: str = field(init=False)
#     forecast_category: str = field(init=False)
#     business_type: str = field(init=False)

#     def __post_init__(self, opportunity: Opportunity, snapshot_date: datetime):
#         self.id = OpportunityHistory.unique("history_id", fake.uuid4)
#         self.opportunity_id = opportunity.id
#         self.snapshot_date = snapshot_date
#         self.value = opportunity.value
#         self.account_id = opportunity.account_id
#         self.owner_id = opportunity.owner_id
#         self.opened_date = opportunity.opened_date
#         self.closed_date = opportunity.closed_date
#         self.name = opportunity.name
#         self.status = opportunity.status
#         self.stage_name = opportunity.stage_name
#         self.forecast_category = opportunity.forecast_category
#         self.business_type = opportunity.business_type

@dataclass
@dateformat(DATE_FORMAT)
class ProductUser(metaclass=Table):
    id: str = field(init=False)
    account_id: str
    first_name: str = field(default_factory=fake.first_name)
    last_name: str = field(default_factory=fake.last_name)
    created_date: datetime = field(init=False)


    def __post_init__(self):
        account = Account.pick_existing_object(lambda a: a.id == self.account_id)

        self.id = ProductUser.unique("product_user_id", fake.uuid4)
        self.created_date = fake.date_time_between_dates(
            start=datetime(year=2023, month=1, day=1), end=datetime.today()
        )

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

def generate_usage(max_days=180, max_rows=10_000_000):
    start_date = datetime(year=2023, month=1, day=1)
    end_date = datetime.today()
    date_cursor = max(end_date - timedelta(days=max_days), start_date)

    account_map = {a.id: a for a in Account.instances}

    customer_users = [
        u for u in ProductUser.instances
        if u.account_id in account_map and account_map[u.account_id].status == "Customer"
    ]

    row_count = 0

    while date_cursor <= end_date:
        for user in customer_users:
            account = account_map[user.account_id]
            products = account.products
            weights = account.product_weights

            # Biased sampling: pick N products with skew
            n = random.randint(1, min(3, len(products)))
            sampled_products = random.choices(products, weights=weights, k=n)

            for product_name in sampled_products:
                Usage(
                    account_id=user.account_id,
                    user_id=user.id,
                    product_id=product_name,
                    usage_date=date_cursor.date(),
                    usage_min=max(1, random.randint(10, 120) + random.randint(-5, 5)),
                )
                row_count += 1

                if row_count >= max_rows:
                    print(f"Reached max row count of {max_rows}")
                    return
        date_cursor += timedelta(days=1)

if __name__ == "__main__":
    # Generate Accounts
    Account.generate(count=fake.poisson(100))

    # Generate Internal Users (30 AEs)
    SFDCUser.generate(count=30)

    # Finalize Accounts (assign owner_id + products)
    for account in Account.instances:
        account.after_all_generated()

    # Generate External Product Users
    for account in Account.instances:
        if account.segment == "Enterprise":
            num_users = random.randint(200, 1000)
        elif account.segment == "MM":
            num_users = random.randint(20, 100)
        else:  # SMB
            num_users = random.randint(1, 20)

        # create users
        users = [ProductUser(account_id=account.id) for _ in range(num_users)]

        # assign products to users explicitly AFTER account products set
        for user in users:
            num_products = random.randint(1, len(account.products))
            user.products = random.sample(account.products, num_products)

    # Generate Usage Data (limit to 1.2M rows for 240MB cap)
    generate_usage(max_days=180, max_rows=10_000_000)
    Usage.write()

    # OpportunityHistory.write()

    # Write Dimension Tables
    Table.writeall()