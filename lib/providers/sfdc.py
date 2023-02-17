from faker.providers import BaseProvider
import random

def random_character(len:int):
    '''Returns a random string of length len, comprising strings and numbers'''
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(len))

class sfdc_ids(BaseProvider):
     instance = random_character(2)
     #Account	  001
     def sfdc_account_id(self):
         return f'001{self.instance}0{random_character(12)}'
        # Standard Object API Name	Object Id Prefixes
        # Account	001
        # Activity	007
        # Approval	806
        # Attachment	00P
        # CampaignMember	00v
        # Campaigns	701
     def sfdc_campaign_id(self):
         return f'701{self.instance}0{random_character(12)}'
        # Case	500
     def sfdc_case_id(self):
         return f'500{self.instance}0{random_character(12)}'
        # Contact	003
     def sfdc_contact_id(self):
         return f'003{self.instance}0{random_character(12)}'
        # Contract	800
        # Dashboard	01Z
        # DashboardComponent	01a
        # EmailTemplate	00X
        # Event	00U
        # Folder	00l
        # Group	00G
        # Page Layout	00h
        # Lead	00Q
     def sfdc_lead_id(self):
         return f'00Q{self.instance}0{random_character(12)}'
        # ListView	00B
        # Opportunity	006
     def sfdc_opportunity_id(self):
         return f'006{self.instance}0{random_character(12)}'
        # OpportunityLineItem	00k
     def sfdc_opplineitem_id(self):
         return f'00k{self.instance}0{random_character(12)}'
        # Order	801
        # OrderItem	802
        # Pricebook	00i
        # Pricebook2	01s
        # Product	00j
        # Product2	01t
     def sfdc_product2_id(self):
         return f'01t{self.instance}0{random_character(12)}'
        # Profile	00e
        # Report	00O
        # Sharing Rule	02c
        # Task	00T
        # User	005
     def sfdc_user_id(self):
         return f'005{self.instance}0{random_character(12)}'
        # UserRole	00E
     def sfdc_role_id(self):
         return random.choice([
                f'005{self.instance}09yOipW000000', #sales
                f'005{self.instance}09yOipAA00000', #sdr/bizdev
                f'005{self.instance}084A7iuH00000', #user
         ])