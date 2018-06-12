#!/usr/bin/env python3

import json
import logging


quote_url = 'https://etws.etrade.com/market/rest/quote/'


class Quote:
    def __init__(self, symbol, session):
        self.symbol = symbol
        self.session = session
        self.ask = None

    def update(self):
        response = self.session.get(quote_url + self.symbol + '.json')
        res_dict = json.loads(response.content.decode('utf-8'))
        logging.debug(res_dict)

        self.ask = float(res_dict['quoteResponse']['quoteData']['all']['ask'])


class Stock:
    def __init__(self, symbol, account, session):
        self.symbol = symbol
        self.account = account
        self.session = session
        self.count = None
        self.value = None
