#!/usr/bin/env python3

import logging
import json
from . import stocks


balance_url = 'https://etws.etrade.com/accounts/rest/accountbalance/'
position_url = 'https://etws.etrade.com/accounts/rest/accountpositions/'


class Account:
    def __init__(self, id, session):
        self.id = id
        self.session = session
        self.net_value = None
        self.cash_to_trade = None
        self.stock_list = []
        self.mode = 'setup'

    def update(self):
        if not self.session:
            logging.error('session does not exist')
            raise BrokenPipeError

        response = self.session.get(balance_url + str(self.id) + '.json')
        res_dict = json.loads(response.content.decode('utf-8'))

        try:
            cont_dict = res_dict['json.accountBalanceResponse']
        except KeyError:
            logging.error('failed to get the account balance')
            return False
        self.net_value = float(cont_dict['accountBalance']['netAccountValue'])
        self.cash_to_trade = float(cont_dict['cashAccountBalance']['cashAvailableForInvestment'])

        response = self.session.get(position_url + str(self.id) + '.json')
        res_dict = json.loads(response.content.decode('utf-8'))

        logging.debug(res_dict)

        cont_dict = res_dict['json.accountPositionsResponse']
        if cont_dict['count'] == 0:
            logging.info('there is no stock in this account')
            return True

        for json_position in cont_dict['response']:
            symbol = json_position['productId']['symbol']
            count = json_position['qty']
            value = json_position['marketValue']

            stock = stocks.Stock(symbol, self, self.session)
            stock.count = int(count)
            stock.value = float(value) / count

            self.stock_list.append(stock)

        return True

    def get_stock(self, symbol):
        for stock in self.stock_list:
            if stock.symbol == symbol:
                return stock

        return None

    def new_stock(self, symbol):
        stock = stocks.Stock(symbol, self, self.session)
        quote = stocks.Quote(symbol, self.session)
        if not quote.update():
            logging.error('getting quote failed')
            return None
        stock.value = (quote.ask + quote.bid) / 2
        stock.count = 0

        self.stock_list.append(stock)
        return stock
