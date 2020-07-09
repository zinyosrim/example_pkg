from graphql import GraphQL
from rest import REST
import logger
import numpy as np
import pandas as pd

def main():
    log = logger.configure("default")

    # Example Query Filter
    qf = ('query:"created_at:<=2020-07-01 ' +
            'AND created_at:>=2020-01-20 ' +
            'AND source_name:web", ' +
            'sortKey: CREATED_AT, first: 200, reverse:true')

    
    #REST
    #from query_parameters_payout_transactions import url, payload, headers
    #shopify = REST(url=url, headers=headers)
    
    # GraphQL
    from query_parameters_orders import url, payload, headers
    #qf = ""
    #payload= "{{shop {{name description email}}}}"
    shopify = GraphQL(url=url, headers=headers, payload=payload, query_filter=qf)
    data = shopify.data()


if __name__ == '__main__':   
    main()
    

