from abc import ABC, abstractmethod
import os
import logger

class GraphQLRequest(ABC):
    def __init__(self):
        super().__init__()
        self._store = os.environ['SHOPIFY_STORENAME']
        self._password = os.environ['SHOPIFY_STORE_API_PASSWORD']
        self._api_version = os.environ['SHOPIFY_API_VERSION']
        self.log = logger.configure("default")

    def url(self) -> str:
        return 'https://{}.myshopify.com/admin/api/{}/graphql.json'\
            .format(self._store, self._api_version)

    def headers(self) -> dict:
        return {'x-shopify-access-token': self._password,'content-type': 'application/json'}

class GetProductsByTag(GraphQLRequest):
    def __init__(self, tag: str = '', number_of_products: int = 50):
        super().__init__()
        self._number_of_products = number_of_products
        self._tag = tag
        self.run()

    def payload(self) -> str:
        pl =    '{{'\
                    '"query":"{{'\
                        'products {} {{'\
                            'edges {{'\
                                'cursor '\
                                'node {{ '\
                                    'id '\
                                    'handle'\
                                '}}'\
                            '}}'\
                        '}}'\
                    '}}"'\
                '}}'
        return pl

    def query_filter(self) -> str:
        return 'first: {}, query:\\\"{}\\\"'.format(self._number_of_products, self._tag)

    def run(self):
        """Check types of class attributes and placeholder existence ``{}``
        """
        # check input param ``number_of_products``, must be ``int``
        try:
            assert type(self._number_of_products) == int
        except AssertionError:
            self.log.error('Query filter parameter number_of_products must be of type int, received: {} (type: {})'\
                .format(self._number_of_products, type(self._number_of_products)))
            raise
        # check input param ``tag``, must be ``str``
        try:
            assert type(self._tag) == str
        except AssertionError:
            self.log.error('Query filter parameter tag must be of type str, received: {} (type: {})'\
                .format(self._tag, type(self._tag)))
            raise

        # check if `{}` in payload
        try:
            assert '{}' in self.payload()
        except AssertionError:
            self.log.error('Payload String must include `\{\}`to insert Query filter, payload = {}'\
                .format(self.payload()))
            raise

class CreateMetafield(GraphQLRequest):
    def __init__(self, id: str, namespace: str, key: str, value: str, value_type: str = 'STRING' ):
        super().__init__()
        self._id = id
        self._namespace = namespace
        self._key = key
        self._value = value
        self._value_type = value_type 

    def payload(self) -> str:
        pl = '{{'\
                '"query":"mutation($input: ProductInput!) {{'\
                    'productUpdate(input: $input) {{'\
                        'product {{'\
                            'metafields(first: 100) {{'\
                                'edges {{' \
                                    'node {{'\
                                        'id '\
                                        'namespace '\
                                        'key '\
                                        'value '\
                                    '}}'\
                                '}}'\
                            '}}'\
                        '}}'\
                        'userErrors {{'\
                            'field,'\
                            'message'\
                            '}}'\
                        '}} '\
                    '}}'\
                '",' \
                '"variables":'\
                    '{{"input":'\
                        '{{'\
                            '"id":"{}",'\
                            '"metafields":[{{'\
                                '"namespace":"{}",'\
                                '"key":"{}",'\
                                '"value":"{}",'\
                                '"valueType":"{}"'\
                            '}}]'\
                        '}}'\
                    '}}'\
            '}}'
        return pl.format(self._id, self._namespace, self._key, self._value, self._value_type)



