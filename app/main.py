from fastapi import FastAPI
from timeit import default_timer as timer
from models import User, Wallet, Transaction
from utils import check_email, gen_wallet_address, \
    authenticate_token, btc_to_usd

import mysql.connector


cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    database='paxful',
    password='password',
    auth_plugin='mysql_native_password'
)


app = FastAPI()


@app.post("/v1/users/")
async def create_user(user: User):
    '''
    Endpoint to create new users

    requirement:
        JSON body with 'name' and 'email'
    
    return:
        JSON with 'name', 'email', 'token', max_wallet,
        date_created and api_response_time
    '''
    start = timer()
    cursorA = cnx.cursor(buffered=True)
    cursorB = cnx.cursor(buffered=True)
 
    user_dict = user.dict()

    if check_email(email=user_dict['email']) is False:
        return {'ERROR': 'email invalid!', 'email': user_dict['email']}

    add_user_sql = "INSERT INTO users(name, email) VALUES(%s, %s)"
    add_user_values = (user_dict['name'], user_dict['email'])
    
    try:
        cursorA.execute(add_user_sql, add_user_values)
        new_user_id = cursorA.lastrowid
        cnx.commit()
    except Exception as err:
        return {'ERROR': err}

    query = ("SELECT name, email, BIN_TO_UUID(token), max_wallet, date_created FROM users WHERE user_id = %s")
    cursorB.execute(query, (new_user_id,))

    for (name, email, token, max_wallet, date_created) in cursorB:
        user_dict.update({'name': name,
                         'email': email,
                         'token': token,
                         'max_wallet': max_wallet,
                         'date_created': date_created})

    cnx.close()
    end = timer()
    user_dict.update({'api_response_time': end - start})        

    return user_dict


@app.post("/v1/wallets/")
async def create_wallet(wallet: Wallet):
    '''
    Endpoint to create new wallets

    requirement:
        JSON body with 'token' to authenticate the user
        (only users registered can create wallets)

    return:
        JSON with 'coin', 'seed', 'private_key', public_key,
        xprivate_key, xpublic_key, address, wif, children(data),
        xpublic_key_prime, balance, date_created, token, api_response_time
    '''
    start = timer()
    cursorA = cnx.cursor(buffered=True)
    cursorB = cnx.cursor(buffered=True)
    cursorC = cnx.cursor(buffered=True)

    wallet_dict = wallet.dict()

    valid = authenticate_token(token=wallet_dict['token'],
                               cursor=cnx.cursor(buffered=True))[0]

    if valid is not 1:
        return {'NOT AUTHENTICATED': 'Invalid Token!', 'token': wallet_dict['token']}

    wallet_data = gen_wallet_address()

    get_user_id = ("SELECT user_id FROM users WHERE BIN_TO_UUID(token) = %s")
    cursorA.execute(get_user_id, (wallet_dict['token'],))

    for user_id in cursorA:
        wallet_dict.update({'user_id': user_id[0]})

    add_wallet_sql = "INSERT INTO wallets(address, user_id) VALUES(%s, %s)"
    add_wallet_values = (wallet_data['address'], wallet_dict['user_id'])
    
    try:
        cursorB.execute(add_wallet_sql, add_wallet_values)
        cnx.commit()
    except Exception as err:
        return {'ERROR': err}

    getting_wallet_result = ("SELECT balance, date_created from wallets WHERE user_id = %s")
    cursorC.execute(getting_wallet_result, (wallet_dict['user_id'],))

    for (balance, data_created) in cursorC:
        wallet_data['balance'] = balance
        wallet_data['date_created'] = data_created
        wallet_data['token'] = wallet_dict['token']

    cnx.close()
    end = timer()
    wallet_data['api_response_time'] =  end - start

    return wallet_data


@app.get("/v1/wallets/{address}&{token}")
async def get_wallet_info(address: str, token: str):
    '''
    Endpoint to get info from a wallet

    requirement:
        Pass as parameter wallet 'address' and 'token'
        to authenticate the user.
        (only the owner of wallet address can request it)
    
    return:
        JSON with 'address', 'balance'(in BTC), 'balance_usd(in USD)',
        user_id, token, api_response_time
    '''
    start = timer()
    cursorA = cnx.cursor(buffered=True)
    cursorB = cnx.cursor(buffered=True)

    wallet_dict = dict()
    wallet_dict['token'] = token
    wallet_dict['address'] = address

    valid = authenticate_token(token=wallet_dict['token'],
                               cursor=cnx.cursor(buffered=True))[0]

    if valid is not 1:
        return {'NOT AUTHENTICATED': 'Invalid Token!', 'token': wallet_dict['token']}

    get_user_id = ("SELECT user_id FROM users WHERE BIN_TO_UUID(token) = %s")
    cursorA.execute(get_user_id, (wallet_dict['token'],))

    for user_id in cursorA:
        wallet_dict['user_id'] = user_id[0]

    get_wallet_info = ("SELECT balance FROM wallets WHERE user_id = %s and address = %s")
    cursorB.execute(get_wallet_info, (wallet_dict['user_id'], wallet_dict['address']))

    for balance in cursorB:
        wallet_dict['balance'] = balance[0]

    try:
        if 'balance' in wallet_dict.keys():
            pass
        else:
            raise Exception
    except Exception:
        return {'NOT AUTHORIZED': 'This token is not owner of this address!',
               'token': wallet_dict['token'], 'address': wallet_dict['address']}
 
    wallet_dict['balance_usd'] = btc_to_usd(balance=wallet_dict['balance'])

    end = timer()
    wallet_dict['api_response_time'] =  end - start

    return wallet_dict


@app.post("/v1/transactions/")
async def create_transactions(transaction: Transaction):
    '''
    Endpoint to create transactions

    requirement:
        JSON body with 'token' to authenticate the user &
        'address_income', 'address_outcome' and 'amount'.
        (only users owner of wallet 'address_outcome' can
        create transactions to spend his money)
    
    return:
        JSON with 'address_income', 'address_outcome', 'amount',
        user_id, date_created, token, api_response_time
    '''
    start = timer()
    cursorA = cnx.cursor(buffered=True)
    cursorB = cnx.cursor(buffered=True)
    cursorC = cnx.cursor(buffered=True)
    cursorD = cnx.cursor(buffered=True)

    transaction_dict = transaction.dict()

    valid = authenticate_token(token=transaction_dict['token'],
                               cursor=cnx.cursor(buffered=True))[0]

    if valid is not 1:
        return {'NOT AUTHENTICATED': 'Invalid Token!', 'token': transaction_dict['token']}

    get_user_id = ("SELECT user_id FROM users WHERE BIN_TO_UUID(token) = %s")
    cursorA.execute(get_user_id, (transaction_dict['token'],))

    for user_id in cursorA:
        transaction_dict.update({'user_id': user_id[0]})

    get_wallet_info = ("SELECT balance FROM wallets WHERE user_id = %s and address = %s")
    cursorB.execute(get_wallet_info, (transaction_dict['user_id'], transaction_dict['address_outcome']))

    for balance in cursorB:
        transaction_dict['balance_outcome'] = balance[0]

    try:
        if 'balance_outcome' in transaction_dict.keys():
            pass
        else:
            raise Exception
    except Exception:
        return {'NOT AUTHORIZED': 'This token is not owner of this address_outcome!',
               'token': transaction_dict['token'], 'address': transaction_dict['address_outcome']}

    add_transaction_sql = "INSERT INTO transactions(address_income, address_outcome, amount, user_id) VALUES(%s, %s, %s, %s)"
    add_transaction_values = (transaction_dict['address_income'], transaction_dict['address_outcome'], transaction_dict['amount'], transaction_dict['user_id'])

    try:
        cursorC.execute(add_transaction_sql, add_transaction_values)
        new_transaction_id = cursorC.lastrowid
        cnx.commit()
    except Exception as err:
        return {'ERROR': err}

    transaction_dict['balance_outcome'] = float(transaction_dict['balance_outcome']) - float(transaction_dict['amount'])

    get_transaction_info = ("SELECT date_created FROM transactions WHERE transaction_id = %s")
    cursorD.execute(get_transaction_info, (new_transaction_id,))

    for date_created in cursorD:
        transaction_dict['date_created'] = date_created[0]

    end = timer()
    transaction_dict['api_response_time'] =  end - start

    return transaction_dict


@app.get("/v1/transactions/{token}")
async def get_transactions_info(token: str):
    '''
    Endpoint to get info from user's transactions

    requirement:
        Pass as parameter 'token' to authenticate the user.
        (only the owner of transactions can request it)
    
    return:
        JSON with 'transaction_id', 'address_income', 'address_outcome',
        'amount', user_id, date_created, token, api_response_time
    '''
    start = timer()
    cursorA = cnx.cursor(buffered=True)
    cursorB = cnx.cursor(buffered=True)

    transactions_dict = dict()
    transactions_dict['token'] = token

    valid = authenticate_token(token=transactions_dict['token'],
                               cursor=cnx.cursor(buffered=True))[0]

    if valid is not 1:
        return {'NOT AUTHENTICATED': 'Invalid Token!', 'token': transactions_dict['token']}

    get_user_id = ("SELECT user_id FROM users WHERE BIN_TO_UUID(token) = %s")
    cursorA.execute(get_user_id, (transactions_dict['token'],))

    for user_id in cursorA:
        transactions_dict['user_id'] = user_id[0]

    get_transactions_info = ("SELECT transaction_id, address_income, address_outcome, amount, user_id, date_created FROM transactions WHERE user_id = %s")
    cursorB.execute(get_transactions_info, (transactions_dict['user_id'],))

    for (transaction_id, address_income, address_outcome, amount, user_id, date_created) in cursorB:
        transactions_dict[transaction_id] = {}
        transactions_dict[transaction_id]['address_income'] = address_income
        transactions_dict[transaction_id]['address_outcome'] = address_outcome
        transactions_dict[transaction_id]['amount'] = amount
        transactions_dict[transaction_id]['user_id'] = user_id
        transactions_dict[transaction_id]['date_created'] = date_created

    try:
        if 1 in transactions_dict.keys():
            pass
        else:
            raise Exception
    except Exception:
        return {'EMPTY': 'This user_id and token don\'t have transactions!',
               'token': transactions_dict['token'],
               'user_id': transactions_dict['user_id']}

    end = timer()
    transactions_dict['api_response_time'] =  end - start

    return transactions_dict


@app.get("/v1/wallets/transactions/{address}&{token}")
async def get_wallet_transactions(address: str, token: str):
    '''
    Endpoint to get the transactions of a wallet

    requirement:
        Pass as parameter the 'address' and 'token' to authenticate the user.
        (only users registered can request it)
    
    return:
        JSON with 'transaction_id', 'address_income', 'address_outcome',
        'amount', date_created, token, api_response_time
    '''
    start = timer()
    cursorA = cnx.cursor(buffered=True)

    transactions_dict = dict()
    transactions_dict['token'] = token

    valid = authenticate_token(token=transactions_dict['token'],
                               cursor=cnx.cursor(buffered=True))[0]

    if valid is not 1:
        return {'NOT AUTHENTICATED': 'Invalid Token!', 'token': transactions_dict['token']}

    get_transactions_info = ("SELECT transaction_id, address_income, address_outcome, amount, date_created FROM transactions WHERE address_income = %s OR address_outcome = %s")
    cursorA.execute(get_transactions_info, (address, address))

    for (transaction_id, address_income, address_outcome, amount, date_created) in cursorA:
        transactions_dict[transaction_id] = {}
        transactions_dict[transaction_id]['address_income'] = address_income
        transactions_dict[transaction_id]['address_outcome'] = address_outcome
        transactions_dict[transaction_id]['amount'] = amount
        transactions_dict[transaction_id]['date_created'] = date_created

    try:
        if 1 in transactions_dict.keys():
            pass
        else:
            raise Exception
    except Exception:
        return {'EMPTY': 'This address don\'t have transactions!',
               'token': transactions_dict['token'],
               'address': address}

    end = timer()
    transactions_dict['api_response_time'] =  end - start

    return transactions_dict


@app.get("/v1/statistics/{token}")
async def get_statistics(token: str):
    '''
    Endpoint to get statistics of the Paxful platform 

    requirement:
        Hardcoded Token
    
    return:
        JSON with 'profit', 'number_of_transactions', and api_response_time
    '''
    start = timer()
    cursorA = cnx.cursor(buffered=True)

    statistics_dict = dict()
    statistics_dict['token'] = token

    if statistics_dict['token'] != '85d9b183-d1b6-11e9-aae0-0242ac110002-19c663b4-d26c-11e9-aae0-0242ac110002':
        return {'NOT AUTHENTICATED': 'Invalid Token!', 'token': statistics_dict['token']}

    get_statistics = ("SELECT SUM(profit), (SELECT count(*) FROM statistics) FROM statistics")
    cursorA.execute(get_statistics)

    for query in cursorA:
        statistics_dict['profit'] = query[0]
        statistics_dict['number_of_transactions'] = query[1]

    end = timer()
    statistics_dict['api_response_time'] =  end - start

    return statistics_dict
