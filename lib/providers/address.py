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
            # 'state': addr[0].state_id,
            'state': addr[0].state_name,
            'zip': addr[0].zip
        }


# AL	Alabama
# AK	Alaska
# AS	American Samoa
# AZ	Arizona
# AR	Arkansas
# CA	California
# CO	Colorado
# CT	Connecticut
# DE	Delaware
# DC	District Of Columbia
# FL	Florida
# GA	Georgia
# GU	Guam
# HI	Hawaii
# ID	Idaho
# IL	Illinois
# IN	Indiana
# IA	Iowa
# KS	Kansas
# KY	Kentucky
# LA	Louisiana
# ME	Maine
# MD	Maryland
# MA	Massachusetts
# MI	Michigan
# MN	Minnesota
# MS	Mississippi
# MO	Missouri
# MT	Montana
# NE	Nebraska
# NV	Nevada
# NH	New Hampshire
# NJ	New Jersey
# NM	New Mexico
# NY	New York
# NC	North Carolina
# ND	North Dakota
# MP	Northern Mariana Is
# OH	Ohio
# OK	Oklahoma
# OR	Oregon
# PA	Pennsylvania
# PR	Puerto Rico
# RI	Rhode Island
# SC	South Carolina
# SD	South Dakota
# TN	Tennessee
# TX	Texas
# UT	Utah
# VT	Vermont
# VA	Virginia
# VI	Virgin Islands
# WA	Washington
# WV	West Virginia
# WI	Wisconsin
# WY	Wyoming