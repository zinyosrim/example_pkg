import logger
import os
import numpy as np
import pandas as pd
from pprint import pprint

from graphql import GraphQL
from rest import REST
from metafields import Metafields
from queries import GetProductsByTag


def main():
    log = logger.configure("default")
    os.environ['SHOPIFY_STORENAME'] = 'radiat'
    os.environ['SHOPIFY_STORE_API_PASSWORD'] = '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' 
    os.environ['SHOPIFY_API_VERSION'] = '2020-07'
    
    query = GetProductsByTag(tag="AW2020")
    url, headers, payload, query_filter = query.url(), query.headers(), query.payload(), query.query_filter()

    shopify = GraphQL(url, headers, payload, query_filter)
    print(shopify.data())

if __name__ == '__main__':   
    main()
    

