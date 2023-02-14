import os, random, json, re, csv, itertools, datetime
from faker import Faker

from google.cloud import storage, bigquery
from dataclasses import dataclass, field, astuple, asdict, InitVar
from typing import Any

import faker
fake = faker.Faker()

#https://github.com/russlooker/vision_image/blob/main/main.py

##########
#Datatypes needed:
#random integer
#random choice weighted probability
#random date within range


##########  Vidly ###########
# Salesforce -> ad accounts
# Salesforce -> ad opportunities
# Salesforce -> ad leads
# Salesforce -> ad contacts
# users ->
# user_billing 
# payment methods
# app_events
# video
# video_regions
# reccomendations
# producers
# marketing -> google analytics
# producer_royalties
######################3








@dataclass
class Document(object):
    document_id:int = field(default_factory=itertools.count().__next__)
    person_id:int = field(init=False)
    type:str = field(init=False)
    location:str = field(init=False)
    _type:InitVar[str] = ''
    person:InitVar[Any] = None

    def __post_init__(self, _type='', person=None):
        self.type = _type
        self.person_id = person.person_id

