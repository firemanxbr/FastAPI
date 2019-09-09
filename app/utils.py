'''
    Group of functions utils to the Paxful API
'''
from pywallet import wallet

import re
import requests


def btc_to_usd(balance):
    '''
    Function to get the value of your BTC balance in USD

    depends:
        API: https://api.cryptonator.com/api/ticker/btc-usd

    param:
        balance: the current balance in BTC

    return: the current balance in USD converted
    '''
    req = requests.get('https://api.cryptonator.com/api/ticker/btc-usd')

    usd = float(req.json()['ticker']['price']) * float(balance)

    return usd


def authenticate_token(token, cursor):
    '''
    Function to authenticate a token

    depends:
        mysql connector config.

    param:
        token: token string
        cursor: a cursor of mysql connection, for example:
                authenticate_token(cursor=cnx.cursor(buffered=True))

    return: 1 is the token is valid
    '''
    query = ('SELECT count(*) FROM users WHERE BIN_TO_UUID(token) = %s')
    cursor.execute(query, (token,))

    for parser in cursor:
        valid = parser

    return valid


def gen_wallet_address():
    '''
    Function to generate a wallet address

    return: A data structure of a BTC wallet
    '''
    seed = wallet.generate_mnemonic()
    data = wallet.create_wallet(network="BTC", seed=seed, children=1)

    return data


def check_email(email):
    '''
    Function to validate the email format

    param:
        email: email address

    return: True if the email is valid or False to invalid
    '''
    regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    return bool(re.search(regex, email))
