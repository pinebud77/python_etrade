#!/usr/bin/env python3

import logging
import requests
from requests_oauthlib import OAuth1Session
from html.parser import HTMLParser
from fake_useragent import UserAgent

renew_success_string = b'Access Token has been renewed'
revoke_success_string = b'Revoked Access Token'

us_base_url = 'https://us.etrade.com'
request_token_url = 'https://etws.etrade.com/oauth/request_token'
authorize_app_url = 'https://us.etrade.com/e/t/etws/authorize'
get_access_token_url = 'https://etws.etrade.com/oauth/access_token'
renew_access_token_url = 'https://etws.etrade.com/oauth/renew_access_token'
revoke_access_token_url = 'https://etws.etrade.com/oauth/revoke_access_token'


class FormHTMLParser(HTMLParser):
    def __init__(self, only_hidden=True):
        super(FormHTMLParser, self).__init__()
        self.post_url = None
        self.input_dict = {}
        self.only_hidden = only_hidden

    def handle_starttag(self, tag, attrs):
        if tag == 'form':
            for attr in attrs:
                if attr[0] == 'action':
                    self.post_url = attr[1]

        if tag == 'input':
            if self.only_hidden and not self.post_url:
                return

            hidden = False
            value = ''
            name = ''
            for attr in attrs:
                if attr[0] == 'type' and attr[1] == 'hidden':
                    hidden = True
                if attr[0] == 'value':
                    value = attr[1]
                if attr[0] == 'name':
                    name = attr[1]
            if self.only_hidden and not hidden:
                return

            self.input_dict[name] = value


def etrade_login(client_key, client_secret, username, passwd):
    oauth = OAuth1Session(client_key, client_secret, callback_uri='oob', signature_type='AUTH_HEADER')
    fetch_response = oauth.fetch_request_token(request_token_url)
    oauth_token = fetch_response.get('oauth_token')
    oauth_token_secret = fetch_response.get('oauth_token_secret')

    verify_string = None
    verify_url = authorize_app_url + '?key=' + client_key + '&token=' + oauth_token

    ua = UserAgent()
    headers = {'User-Agent': ua.chrome}
    session = requests.session()
    response = requests.get(verify_url, headers=headers)

    content_string = str(response.content)

    if 'Log On to E*TRADE' in content_string:
        logging.debug('logging in with username + password')
        parser = FormHTMLParser()
        parser.feed(content_string)

        parser.input_dict['USER'] = username
        parser.input_dict['PASSWORD'] = passwd
        parser.input_dict['REMEMBER_MY_USER_ID'] = 'true'

        response = session.post(us_base_url + parser.post_url, headers=headers, data=parser.input_dict)
        content_string = str(response.content)
        logging.debug(content_string)

    if 'please acknowledge that you agree to allow the indicated platform' in content_string:
        logging.debug('pressing accept')
        parser = FormHTMLParser()
        parser.feed(content_string)

        parser.input_dict['submit'] = 'Accept'

        response = session.post(us_base_url + parser.post_url, headers=headers, data=parser.input_dict)
        content_string = str(response.content)
        logging.debug(content_string)

    if 'You will then be directed to the next page where you will paste the code' in content_string:
        logging.debug('getting verfication token')
        parser = FormHTMLParser(only_hidden=False)
        parser.feed(content_string)

        verify_string = parser.input_dict['']
        verify_string = verify_string.split('\\')[0]

    if not verify_string:
        return None

    oauth = OAuth1Session(client_key,
                          client_secret,
                          resource_owner_key=oauth_token,
                          resource_owner_secret=oauth_token_secret,
                          verifier=verify_string)
    fetch_response = oauth.fetch_request_token(get_access_token_url)

    logging.debug(fetch_response)

    return oauth


def renew_token(oauth):
    response = oauth.get(renew_access_token_url)
    logging.debug(response.content)
    return response.content == renew_success_string


def revoke_token(oauth):
    response = oauth.get(revoke_access_token_url)
    logging.debug(response.content)
    return response.content == revoke_success_string

