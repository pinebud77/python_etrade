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

    def update(self):
        if not self.session:
            raise BrokenPipeError

        response = self.session.get(balance_url + str(self.id) + '.json')
        res_dict = json.loads(response.content.decode('utf-8'))

        cont_dict = res_dict['json.accountBalanceResponse']
        self.net_value = float(cont_dict['accountBalance']['netAccountValue'])
        self.cash_to_trade = float(cont_dict['accountBalance']['cashAvailableForWithdrawal'])

        response = self.session.get(position_url + str(self.id) + '.json')
        res_dict = json.loads(response.content.decode('utf-8'))

        logging.debug(res_dict)

        cont_dict = res_dict['json.accountPositionsResponse']
        for json_position in cont_dict['response']:
            symbol = json_position['productId']['symbol']
            count = json_position['qty']
            value = json_position['marketValue']

            stock = stocks.Stock(symbol, self, self.session)
            stock.count = int(count)
            stock.value = float(value)

            self.stock_list.append(stock)

    def get_stock(self, symbol):
        for stock in self.stock_list:
            if stock.symbol == symbol:
                return stock

        return None

