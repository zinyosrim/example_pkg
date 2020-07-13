import json
from datetime import datetime, timedelta
import app_logger
from shopify_request import ShopifyRequest
from response_processor import ResponseProcessor
from util import config
from math import ceil
from time import sleep
from queries_orders import url, headers, payload


class Orders:
    
    def __init__(self, from_date, to_date):
        self.logger = app_logger.configure('default')
        # load some earlier orders as well due to delayed financial transactions
        from_date = from_date - timedelta(days=10)
        self.query_params = {'from_date': from_date.strftime('%Y-%m-%d'), 
                             'to_date':to_date.strftime('%Y-%m-%d'), 
                             'number_of_orders': config()['general']['max_orders'], 
                             'cursor':''}
    
    def search_string(self):
        # build search string for filtering orders
        if self.query_params['cursor'] == "":     
            search_string = '(query:"created_at:>={} AND created_at:<={} AND source_name:web", sortKey: CREATED_AT, reverse:true, first: {})'\
                .format(self.query_params['from_date'], self.query_params['to_date'], self.query_params['number_of_orders'], self.query_params['cursor'])
        else: 
            search_string = '(query:"created_at:>={} AND created_at:<={} AND source_name:web", sortKey: CREATED_AT, reverse:true, first: {} after: "{}")'\
                .format(self.query_params['from_date'], self.query_params['to_date'], self.query_params['number_of_orders'], self.query_params['cursor'])

        return(search_string)

    def data(self):
        graphql = GraphQL(self.search_string())