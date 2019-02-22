#!/usr/bin/env python3

import logging
from requests_oauthlib import OAuth1Session
import subprocess
from os.path import join, realpath, dirname

CUR_DIR = dirname(realpath(__file__))

renew_success_string = b'Access Token has been renewed'
revoke_success_string = b'Revoked Access Token'

us_base_url = 'https://us.etrade.com'
request_token_url = 'https://etws.etrade.com/oauth/request_token'
authorize_app_url = 'https://us.etrade.com/e/t/etws/authorize'
get_access_token_url = 'https://etws.etrade.com/oauth/access_token'
renew_access_token_url = 'https://etws.etrade.com/oauth/renew_access_token'
revoke_access_token_url = 'https://etws.etrade.com/oauth/revoke_access_token'


def etrade_login(client_key, client_secret, username, passwd):
    oauth = OAuth1Session(client_key, client_secret, callback_uri='oob', signature_type='AUTH_HEADER')
    fetch_response = oauth.fetch_request_token(request_token_url)
    oauth_token = fetch_response.get('oauth_token')
    oauth_token_secret = fetch_response.get('oauth_token_secret')

    verify_url = authorize_app_url + '?key=' + client_key + '&token=' + oauth_token

    args = list()
    args.append(join(CUR_DIR, 'phantomjs'))
    args.append(join(CUR_DIR, 'phantomjs_etrade.js'))
    args.append(verify_url)
    args.append(username)
    args.append(passwd)

    result = subprocess.run(args, stdout=subprocess.PIPE)
    verify_string = result.stdout.decode('utf-8')

    verify_string = verify_string.split('\n')[0]
    verify_string = verify_string.split('\r')[0]
    logging.info(verify_string)

    if not verify_string or verify_string == 'null':
        logging.error('Cannot get the verify string')
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

