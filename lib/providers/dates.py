from faker.providers import BaseProvider
from datetime import datetime, timedelta
import random


class dates(BaseProvider):
    def this_quarter_start(self) -> datetime:
        '''Returns the start of the current quarter'''
        now = datetime.now()
        month = now.month
        if month < 4:
            return datetime(now.year, 1, 1, 0, 0, 0)
        elif month < 7:
            return datetime(now.year, 4, 1, 0, 0, 0)
        elif month < 10:
            return datetime(now.year, 7, 1, 0, 0, 0)
        else:
            return datetime(now.year, 10, 1, 0, 0, 0)
        
    def this_quarter_end(self) -> datetime:
        '''Returns the end of the current quarter'''
        now = datetime.now()
        month = now.month
        if month < 4:
            return datetime(now.year, 3, 31, 23, 59, 59)
        elif month < 7:
            return datetime(now.year, 6, 30, 23, 59, 59)
        elif month < 10:
            return datetime(now.year, 9, 30, 23, 59, 59)
        else:
            return datetime(now.year, 12, 31, 23, 59, 59)
        
        
    def this_month_start(self) -> datetime:
        '''Returns the start of the current month'''
        now = datetime.now()
        return datetime(now.year, now.month, 1, 0, 0, 0)
    
    def this_month_end(self) -> datetime:
        '''Returns the end of the current month'''
        now = datetime.now()
        return datetime(now.year, now.month, self.monthrange(now.year, now.month)[1], 23, 59, 59)
    
    def monthrange(self, year, month):
        '''Returns the number of days in a month'''
        if month == 2:
            if year % 4 == 0:
                return 29
            else:
                return 28
        elif month in [4, 6, 9, 11]:
            return 30
        else:
            return 31
        
    def this_week_start(self) -> datetime:
        '''Returns the start of the current week'''
        now = datetime.now()
        return now - timedelta(days=now.weekday())
    
    def this_week_end(self) -> datetime:
        '''Returns the end of the current week'''
        now = datetime.now()
        return now + timedelta(days=6-now.weekday())

    def date_time_this_week(self, before_today=True, after_today=True) -> datetime:
        '''Returns a random datetime in the current week'''
        start = self.this_week_start()
        end = self.this_week_end()
        if before_today:
            end = datetime.now()
        if after_today:
            start = datetime.now()
        return self.date_time_between_dates(start, end)
    
    def date_time_this_month(self, before_today=True, after_today=True) -> datetime:
        '''Returns a random datetime in the current month'''
        start = self.this_month_start()
        end = self.this_month_end()
        if before_today:
            end = datetime.now()
        if after_today:
            start = datetime.now()
        return self.date_time_between_dates(start, end)
    
    def date_time_this_quarter(self, before_today=True, after_today=True) -> datetime:
        '''Returns a random datetime in the current quarter'''
        start = self.this_quarter_start()
        end = self.this_quarter_end()
        if before_today:
            end = datetime.now()
        if after_today:
            start = datetime.now()
        return self.date_time_between_dates(start, end)
    

    def date_time_between_dates(self, start: datetime, end: datetime) -> datetime:
        '''Returns a random datetime between start and end'''
        return start + (end - start) * random.random()


    def date_time_this_year(self, before_today=True, after_today=True) -> datetime:
        '''Returns a random date in the current year'''
        year = datetime.now().year
        start = datetime(year, 1, 1, 0, 0, 0)
        end = datetime(year, 12, 31, 23, 59, 59)
        if before_today:
            end = datetime.now()
        if after_today:
            start = datetime.now()
        return self.date_time_between_dates(start, end)

    def date_time_recent(self, days=365) -> datetime:
        '''Returns a random date in the last 365 days'''
        start = datetime.now() - timedelta(days=days)
        end = datetime.now()
        return self.date_time_between_dates(start, end)

    def date_time_this_decade(self, before_today=True, after_today=True) -> datetime:
        '''Returns a random date in the current decade'''
        year = datetime.now().year
        start = datetime(year - year % 10, 1, 1, 0, 0, 0)
        end = datetime(year - year % 10 + 9, 12, 31, 23, 59, 59)
        if before_today:
            end = datetime.now()
        if after_today:
            start = datetime.now()
        return self.date_time_between_dates(start, end)