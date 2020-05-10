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
        self.bid = None

    def update(self):
        response = self.session.get(quote_url + self.symbol + '.json')
        res_dict = json.loads(response.content.decode('utf-8'))
        logging.debug(res_dict)

        try:
            self.ask = float(res_dict['quoteResponse']['quoteData']['all']['ask'])
        except KeyError:
            return False

        try:
            self.bid = float(res_dict['quoteResponse']['quoteData']['all']['bid'])
        except KeyError:
            return False

        return True


class Stock:
    def __init__(self, symbol, account, session):
        self.symbol = symbol
        self.account = account
        self.session = session
        self.count = None
        self.value = None
        self.last_value = 0.0
        self.budget = 0.0
        self.in_algorithm = 0
        self.in_stance = 1
        self.out_algorithm = 0
        self.out_stance = 1
        self.failure_reason = 'success'
        self.float_trade = False

    def market_order(self, count, order_id):
        if not self.session:
            logging.error('no session for order')
            raise BrokenPipeError
        if count == 0:
            logging.error('the count is 0 for order')
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
            self.failure_reason = res_string.split('<ErrorMessage>')[1].split('</ErrorMessage>')[0]
            logging.error(self.failure_reason)
            return False

        self.failure_reason = 'success'

        self.count += count

        return True

    def get_failure_reason(self):
        return self.failure_reason

    def get_total_value(self):
        if self.count is None:
            return None
        if self.value is None:
            return None

        return self.count * self.value
