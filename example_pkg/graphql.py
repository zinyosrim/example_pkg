from shopify import Shopify
from math import ceil
from json import loads
from util import config
from time import sleep
import logger

class GraphQL(Shopify):
    """Class for submitting GraphQL requests to Shopify. Handles any kind of
    GraphQL API request to the store including cursor based pagination and throtteling.

    Args:
        Shopify (ABC): Base class for REST and GraphQL
    """

    def __init__(self, url, headers, payload, query_filter=None,
                 max_cost_points=1000, leak_rate=50, max_retries=5 ):
        """Constructor for GraphQL/Shopify request

        Args:
            url (String): Shopify GraphQL API URL
            headers (dict): HTTP headers
            payload (str): Query/Mutation string
            query_filter (str, optional): [description]. Defaults to None.
            max_cost_points (int, optional): [description]. Defaults to 1000.
            leak_rate (int, optional): [description]. Defaults to 50.
            max_retries (int, optional): [description]. Defaults to 5.
        """
        super().__init__(max_retries=max_retries)
        self.log = logger.configure("default")
        self._url = url
        self._headers = headers
        self._payload = payload
        self._query_filter = query_filter
        
    def method(self):
        return 'POST'
    
    def url(self, response=None):
        return self._url

    def payload(self, response=None):
        """Return payload string. If query requires a filter, it is set in 
        ``self._query_filter``and will be inserted into the payload string.
        Otherwise ``self._payload weill be returned.

        Args:
            response (HTTP Response, optional): [description]. Defaults to None.

        Returns:
            str: The payload string which will be used in the HTTP request
        """

        # there is a query filter, insert into payload string
        if self._query_filter:
            try:
                assert '{}' in self._payload, 'Payload should include `{}` to insert query filter'
            except AssertionError:
                self.log.error('Payload must include `{}` to allow insertion of query filter')
            query = '(' + self._query_filter +'{})'
            if not response: 
                query = query.format('')
            else:
                query = query.format(', after: "' + self.cursor(response) + '"')  
            self.log.debug('query filter: {}'.format(query))
            self.log.debug('payload: {}'.format(self._payload))
            return self._payload.format(query)
        # There is nothing to be inserted into the payload string
        else:
            return self._payload


    def headers(self, response=None):
        return self._headers

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
                #self.log.debug('No next page')
                pass
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
        try:
            return object_data['edges'][-1]['cursor'] if has_next_page else ""
        except:
            self.log.debug("There is no cursor. Check if it's included in the query, \
                if not put a line with cursor after node.")

    def delay(self, response):
        """Based on the throtteling information of the response, execute a delay before
        fetching additional data.

        Args:
            response (HTTP Response): Result of a GraphQL request to Shopify
        """
        max_cost_points = int(config()["general"]["max_cost_points"])
        leak_rate = int(config()["general"]["leak_rate"])

        try:
            cost = loads(response.text)['extensions']['cost']
            remaining_cost = cost['throttleStatus']['currentlyAvailable']
            actual_query_cost  = cost['actualQueryCost'] 
        except KeyError as e:
            self.log.error('Can`t extract query cost from JSON response:\n{}, error: {}'\
                .format(response.text, e))

        if remaining_cost < actual_query_cost:
            time_to_sleep = ceil((max_cost_points - remaining_cost)/leak_rate)
            self.log.info('Delaying next API request for {} seconds to avoid blocking'\
                .format(time_to_sleep))
            sleep(time_to_sleep)

    

    

    
    