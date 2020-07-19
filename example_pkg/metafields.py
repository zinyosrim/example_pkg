import logger
import os
import numpy as np
import pandas as pd
from queries import GetProductsByTag
from graphql import GraphQL

class Metafields:
    """
    Class handling metafields creation based on CSV data

    """
    def __init__(self, csv_path, tag):
        """Constructor

        Args:
            csv_path (str): [description]
            tag (str): Tag to filter products
        """
        self.__csv_path = csv_path
        self.__tag = tag

    def product_handle_to_id(self) -> dict:
        """Return dict with all products, filtered by a tag.

        Args:
            tag (str): Tag used to filter relevant products

        Returns:
            dict: a dictionary with key: handle, value: id
        """
        query_params = {}
        # if tag is specified, filter products by tag
        if self.__tag:
            query_params['tag'] = self.__tag 

        # Get list of all products
        query = GetProductsByTag(**query_params)
        shopify = GraphQL  (url=query.url(), headers=query.headers(), 
                            payload=query.payload(), query_filter=query.query_filter())
        products = shopify.data()
        # Make a dict to retrieve the product id by product handle
        return { product['node']['handle']:product['node']['id'] for product in products }

    def csv_to_dict(self):
        """Return handle and product metafield values from a Shopify product import file, 
        extended by columns for each metafield

        Args:
            csv_path (String): Shopify product import file

        Raises:
            SystemExit: When file doesn't exist
            SystemExit: when necessary columns `Handle` and `metafields...` don't exist.

        Returns:
            dict: with key: handle, value: dict with metafield information
        """
        log = logger.configure("default")
        try: 
            df = pd.read_csv(self.__csv_path)
        except IOError as e:
            # file not found
            log.error('Could not import {}. Got error {}'.format(self.__csv_path, e))
            raise 
        else:
            cols = list(df.columns)
            metafield_cols = [col for col in cols if 'metafields' in col]
            if metafield_cols == [] or 'Handle' not in cols:
                # relevant columns don't exist
                log.error('{} does not contain `Handle` or `metafields` named columns'.format(self.__csv_path))
                raise
            else:
                new_cols = ['Handle'] + metafield_cols
                df = df[new_cols].set_index('Handle')
                df = df[~df.index.duplicated(keep='first')]
                return df.to_dict('index')

    def metafields(self):
        ids = self.product_handle_to_id()
        products = self.csv_to_dict()
        for product in products.items():
            handle = product[0]
            metafields = product[1].items()
            for metafield in metafields:
                metafield_attributes = metafield[0].split('.')
                namespace, key, value = metafield_attributes[1], metafield_attributes[2], metafield[1]
                yield {"id": ids[handle.lower()], "namespace": namespace, "key": key, "value": value}