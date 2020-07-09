from shopify import Shopify
from math import ceil
from json import loads
from util import config
from time import sleep
import logger

class GraphQL(Shopify):
    """Class for submitting GraphQL requests to Shopify

    Args:
        Shopify (ABC): Base class for REST and GraphQL
    """

    def __init__(self, url, headers, payload, query_filter=None):
        super().__init__()
        self.log = logger.configure("default")
        self.__url = url
        self.__headers = headers
        self.__payload = payload
        self.__query_filter = query_filter
        
    def method(self):
        return 'POST'
    
    def url(self, response=None):
        return self.__url

    def payload(self, response=None):
        query = '(' + self.__query_filter +'{})'
        if not response: 
            query = query.format('')
        else:
            query = query.format(', after: "' + self.cursor(response) + '"')    
        self.log.debug('Payload for next query:\n{}'.format(self.__payload.format(query)))
        return self.__payload.format(query)

    def headers(self, response=None):
        return self.__headers

    def json_data(self, response=None):
        try:
            return self.api_object_data(response)['edges']
        except:
            return self.api_object_data(response)

    def has_next(self, response):
        try:
            return self.api_object_data(response)['pageInfo']['hasNextPage']
        except:
            if response:
                self.log.debug('No next page, "hasNextPage" missing in response')
            else:
                self.log.debug('Response is empty')
    
    def api_object_data(self, response):
        """Returns name of API object from response

        Args:
            response (Request): HTTP Response of API request 

        Returns:
            String: Name of Shopify API object
        """
        try:   
            data = loads(response.text)['data'] 
            first_key_of_dict = next(iter(data))
            return data[first_key_of_dict]
        except:
            self.log.error('Can`t extract name of API object from JSON response:\n{}'\
                .format(response.text))

    def cursor(self, response):
        """Return cursor of last query object

        Args:
            response (Request): HTTP Response of API request 

        Returns:
            String: Cursor
        """
        object_data = self.api_object_data(response)
        has_next_page = object_data['pageInfo']['hasNextPage'] 
        return object_data['edges'][-1]['cursor'] if has_next_page else ""

    def delay(self, response):
        max_cost_points = int(config()["general"]["max_cost_points"])
        leak_rate = int(config()["general"]["leak_rate"])

        try:
            cost = loads(response.text)['extensions']['cost']
            remaining_cost = cost['throttleStatus']['currentlyAvailable']
            actual_query_cost  = cost['actualQueryCost'] 
        except:
            self.log.error('Can`t extract query cost from JSON response:\n{}'\
                .format(response.text))

        if remaining_cost < actual_query_cost:
            time_to_sleep = ceil((max_cost_points - remaining_cost)/leak_rate)
            self.log.info('Delaying next API request for {} seconds to avoid blocking'\
                .format(time_to_sleep))
            sleep(time_to_sleep)

    

    

    
    