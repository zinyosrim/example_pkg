from abc import ABC, abstractmethod
import requests
import logger
from json import loads
from util import config
from pprint import pprint
from time import sleep

class Shopify(ABC):

    def __init__(self, max_retries=5):
        super().__init__()
        self.__max_retries = max_retries
        self.log = logger.configure("default")

    @abstractmethod
    def method(self):
        """Return HTTP method for building request

        Returns:
            String: HTTP method
        """
        pass

    @abstractmethod    
    def url(self, response=None):
        """Return HTTP URL for building HTTP request

        Args:
            response (Request): HTTP Response of API request 

        Returns:
            String: URL
        """
        pass

    @abstractmethod
    def payload(self, response=None):
        """Return HTTP data for building HTTP request

        Args:
            response (Request): HTTP Response of API request 

        Returns:
            String: Payload data
        """
        pass

    @abstractmethod
    def headers(self, response=None):
        """Return HTTP headers of request

        Args:
            response ([type], optional): [description]. Defaults to None.

        Returns:
            String: HTTP headers
        """
        pass

    @abstractmethod
    def json_data(self, response=None):
        """Return actual API object data

        Args:
            response (Request): HTTP Response of API request 

        Returns:
            List of Dicts: API object nodes
        """
        pass

    @abstractmethod
    def has_next(self, response=None):
        """Returns boolean indicating if there is a next page

        Args:
            response (Request): HTTP Response of API request 

        Returns:
            Boolean: True if there is additiona data to initiate another request, 
            else False
        """
        pass

    @abstractmethod
    def delay(self, response=None):
        """Computes the necessary delay time from the Shopify throtteling data to
        prevent blocking by the server. Sleep for the duration of waiting time (seconds).
        Max. allowed cost is 
        
        Arguments:
            shopify_data {ShopifyGraphqlData} -- Wrapper class for JSON response of query
        """
        pass

    def request(self, *args, **kwargs):
        """Create a single HTTP network request to Shopify. In case of connection issues
        repeat request a certain number of times, after waiting a couple of seconds. 
        Starting from 1s delay, after each failure the waiting time is doubled.

        Returns:
            Dict -- complete JSON data of the response loaded into a dict
        """
        retries_count, wait_seconds = 0, 1
        while retries_count < self.__max_retries:
            response = requests.request(*args, **kwargs)
            if response.status_code == 200:
                return response
            else:
                self.log.debug(
                    "Delaying next Shopify query for {} seconds".format(wait_seconds)
                )
                sleep(wait_seconds)
                response = requests.request(*args, **kwargs)
                wait_seconds *= 2
                retries_count += 1

        self.log.error(
            "Tried {} times to submit a Shopify query to {}. Waited {} seconds between "\
            "last two queries. Failed with HTTP return code {}"\
                .format(retries_count, args[1], wait_seconds / 2, response.status_code
            )
        )

    def session(self):
        """Cursor based query of Shopify resource data. Queries the first n records -
        n can be set in config.yml. If there is more data, the additional data
        is requested based on cursors until all data is collected.

        Yields:
            List of Dicts -- Generator yielded data
        """
        method, url, payload, headers = self.method(), self.url(),\
                                        self.payload(), self.headers()
        has_next = True
        counter = 0
        self.log.debug('Starting session -  method={}, url={}, payload={}, headers={}'\
            .format(method, url, payload, headers))
        
        while has_next:
            counter = counter + 1
            self.log.info("Initiate single API request #{}".format(counter))
            response = self.request(method, url, data=payload, headers=headers)
            yield self.json_data(response)

            if self.has_next(response):
                self.delay(response)
                url, payload = self.url(response), self.payload(response)
                self.log.debug("has_next = {}. Getting next piece of data from {}"\
                    .format(has_next, url))
            else:
                has_next = False
                self.log.info("No additional data available. Done with Shopify requests")

    def data(self):
            """Wrapper to fetch all requested Shopify data packing it into a 
            list of dicts.nInitiate all requests and return the complete data.

            Returns:
                List of Dicts -- All requested data collected from a number of requests
            """
            self.log.info("Starting to request data from Shopify")
            data = []
            for json_data in self.session():
                if type(json_data) == list:
                    data.extend(json_data)
                else:
                    data.append(json_data)
            self.log.info("Shopify returned a total of {} records:".format(len(data),data))
            return data