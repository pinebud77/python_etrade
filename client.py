#!/usr/bin/env python3

from . import login


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
            return False

        result = login.renew_token(self.session)
        if not result:
            self.session = None

        return result

    def logout(self):
        if not self.session:
            return True

        login.revoke_token(self.session)
        self.session = None
        return True







