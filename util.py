from datetime import datetime, timedelta
import yaml
import logger
import os

class GraphqlQueryString:
    def __init__(
        self, query, sort_key="CREATED_AT", reverse=False, count=80, cursor="",
    ):
        self.query = query
        self.sort_key = sort_key
        self.reverse = str(reverse).lower()
        self.count = count
        self.first = self.first_str(cursor)
        self.params = {
            "query": query,
            "sort_key": sort_key,
            "reverse": reverse,
            "first": self.first,
        }

    def __str__(self):
        return "(query: {}, sortKey: {}, reverse: {}, first: {})"\
            .format(self.query, self.sort_key, self.reverse, self.first)

    def first_str(self, cursor):
        return '{} after: "{}"'\
            .format(str(self.count), cursor) if cursor != "" else str(self.count)

    def set_cursor(self, cursor):
        self.first = self.first_str(cursor)


def config():
    """Provides configuration parameters, store information, api_keys
    """
    try:
        with open("config.yml", 'r') as ymlfile:
            return yaml.load(ymlfile, Loader=yaml.BaseLoader)
    except FileNotFoundError:
        logger = app_logger.configure('default')
        logger.error('Could not find configuration file config.yml')
    except:
        logger.error('Invalid key request to config.yml')

def last_day_of_month(any_datetime):
            next_month = any_datetime.replace(day=28) + timedelta(days=4) 
            return next_month - timedelta(days=next_month.day)

def first_day_of_month(any_datetime):
    return datetime(any_datetime.year, any_datetime.month, 1)

def last_months_first_and_last_day():
    last_months_last_day = datetime.now().replace(day=1) - timedelta(days=1) 
    return first_and_last_day_of_month(last_months_last_day)

def first_and_last_day_of_month(any_datetime):
    """Returns first and last day for any given date's month
    
    Arguments:
        any_datetime {[datetime]} -- [any datetime]
    
    Returns:
        [tuple of datetime's] -- [1st and last day of a month]
    """    
    return (first_day_of_month(any_datetime), last_day_of_month(any_datetime))

def last_month_as_str():
    last_month = datetime.now().replace(day=1) - timedelta(days=1) 
    return last_month.strftime('%Y-%m')

def log_filename(): 
    if not os.path.exists('data'):
        os.makedirs('data')
    return 'data/shopify_{}.log'.format(datetime.now().strftime('%Y_%m_%d'))

def first_key_of_dict(d):
    return next(iter(d))




