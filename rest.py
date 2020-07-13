
from shopify import Shopify
from util import config
from time import sleep
from json import loads
from requests.utils import parse_header_links
import logger

class REST(Shopify):
    """Class for submitting REST requests to Shopify
    Usage: 

    #from queries_payout_transactions import url, payload, headers
    #shopify = REST(url=url, headers=headers)

    Args:
        Shopify (ABC): Base class for REST and GraphQL
    """

    def __init__(self, url, headers, payload=None):
        super().__init__()
        self.log = logger.configure("default")
        self.__url = url
        self.__headers = headers
        
    def method(self):
        return 'GET'
    
    def url(self, response=None):
        try:
            link = response.headers['Link']
            #last element in list contains next link
            u = parse_header_links(link)[-1]['url'] 
            return u
        except (KeyError, AttributeError):
            return self.__url

    def payload(self, response=None):
        return ""

    def headers(self, response=None):
        return self.__headers

    def json_data(self, response=None):
        data = loads(response.text)
        try:   
            first_key_of_dict = next(iter(data))  
        except:
            self.log.error('Can`t extract name of API object from the JSON response.\nresponse.text =\n{}'\
                .format(response))
        return data[first_key_of_dict]

    def has_next(self, response=None):
        try:
            link = response.headers['Link']
            rel = parse_header_links(link)[-1]['rel'] #last element in list contains next link
        except KeyError:
            return False

        if (response == None) or (rel == 'next'):
            return True
        else:
            return False

    def delay(self, response):
        sleep(1)
        self.log.debug('Slept 1 sec. Continuing to request data')
    

    

    
    