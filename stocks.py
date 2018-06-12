#!/usr/bin/env python3

import json
import logging


quote_url = 'https://etws.etrade.com/market/rest/quote/'
place_order_url = 'https://etws.etrade.com/order/rest/placeequityorder'


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
        self.last_value = 0.0
        self.last_sell_price = 0.0
        self.last_buy_price = 0.0
        self.last_count = 0
        self.budget = 0.0
        self.algorithm_string = 'ahnyung'
        self.stance = 1

    def market_order(self, count, order_id):
        if not self.session:
            raise BrokenPipeError
        if count == 0:
            raise ValueError

        outer_dict = dict()
        outer_dict['PlaceEquityOrder'] = dict()
        order_dict = outer_dict['PlaceEquityOrder']
        order_dict['-xmlns'] = 'http://order.etws.etrade.com'
        order_dict['EquityOrderRequest'] = dict()
        input_dict = order_dict['EquityOrderRequest']

        input_dict['accountId'] = self.account.id
        input_dict['symbol'] = self.symbol
        if count > 0:
            logging.info('account %s - buy %s: %d' % (self.account.id, self.symbol, count))
            input_dict['orderAction'] = 'BUY'
            input_dict['quantity'] = count
        else:
            logging.info('account %s - sell %s: %d' % (self.account.id, self.symbol, count))
            input_dict['orderAction'] = 'SELL'
            input_dict['quantity'] = -count
        input_dict['clientOrderId'] = order_id
        input_dict['priceType'] = 'MARKET'
        input_dict['marketSession'] = 'REGULAR'
        input_dict['orderTerm'] = 'GOOD_FOR_DAY'

        response = self.session.post(place_order_url, json=outer_dict)
        res_string = response.content.decode('utf-8')
        if 'ErrorMessage' in res_string:
            logging.error(res_string)
            return False

        self.count += count
        if count > 0:
            self.last_buy_price = self.value
        else:
            self.last_sell_price = self.value

        return True

    def get_total_value(self):
        if self.count is None:
            return None
        if self.value is None:
            return None

        return self.count * self.value
