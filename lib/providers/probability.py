from faker.providers import BaseProvider
import numpy as np
import random

class probability(BaseProvider):
    @staticmethod
    def probability(p:float):
        '''Returns True with probability p'''
        return random.random() < p
    
    @staticmethod  
    def bernoulli(p:float):
        '''Returns a boolean value with probability p'''
        return random.random() < p
    
    @staticmethod
    def poisson(lam:float):
        '''
            Returns a random integer value, based on lambda the average number of events per interval
            e.g. for a daily ETL, we might use a lambda of 10 for a user creation event which is expected to occur on average, 
            10 times per day. the integer returned is the number of times the event occurred, which can be used to randomly simulate
            growth
        '''
        return np.random.poisson(lam)
    
    @staticmethod 
    def gaussian(mu:float, sigma:float):
        '''Returns a random integer value with mean mu and standard deviation sigma
            mu = population mean
            sigma = population standard deviation
            e.g. for iq, the mean is 100 and the standard deviation is 15
        '''
        return random.gauss(mu, sigma)

    @staticmethod
    def pareto(alpha:float = 1.16, mu:float = 1):
        '''
            Returns a random sythetic observation from a Pareto distribution
            alpha = 1.16 is the classic 80/20 value for the Pareto distribution
            mu is the mean value of the distribution
            e.g. for income,          
        '''
        return (random.paretovariate(alpha)/100) * mu