#!/usr/bin/env python3

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
        if self.session:
            return True
        return False

    def renew_connection(self):
        if not self.session:
            raise BrokenPipeError

        result = login.renew_token(self.session)
        if not result:
            self.session = None

        return result

    def logout(self):
        if not self.session:
            raise BrokenPipeError

        login.revoke_token(self.session)
        self.session = None
        return True

    def get_account(self, id):
        if not self.session:
            raise BrokenPipeError

        account = accounts.Account(id, self.session)
        account.update()

        if account.net_value is  None:
            return None
        return account

    def get_quote(self, symbol):
        if not self.session:
            raise BrokenPipeError

        quote = stocks.Quote(symbol, self.session)
        quote.update()

        if quote.ask is None:
            return None
        return quote







