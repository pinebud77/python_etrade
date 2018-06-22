#!/usr/bin/env python3
import logging
from . import accounts
from . import login
from . import stocks


class Client:
    def __init__(self):
        self.session = None

    def login(self, client_key, client_secret, username, passwd):
        self.session = login.etrade_login(client_key,
                                          client_secret,
                                          username,
                                          passwd)
        if not self.session:
            return False
        return True

    def renew_connection(self):
        if not self.session:
            logging.error('no session')
            raise BrokenPipeError

        result = login.renew_token(self.session)
        if not result:
            self.session = None
            return False
        return True

    def logout(self):
        if not self.session:
            logging.error('no session')
            raise BrokenPipeError

        login.revoke_token(self.session)
        self.session = None
        return True

    def get_account(self, account_id):
        if not self.session:
            logging.error('no session')
            raise BrokenPipeError

        account = accounts.Account(account_id, self.session)
        if not account.update():
            logging.error('update of account info failed')
            return None

        if account.net_value is None:
            logging.error('update of account info failed : net_value is None')
            return None
        return account

    def get_quote(self, symbol):
        if not self.session:
            logging.error('no session')
            raise BrokenPipeError

        quote = stocks.Quote(symbol, self.session)
        if not quote.update():
            logging.error('update of quote failed')
        if quote.ask is None:
            return None
        return quote
