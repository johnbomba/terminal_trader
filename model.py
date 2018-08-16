#!/usr/bin/env

import json

import sqlite3

import requests


def is_admin():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'
    username = current_user()
    username = username
    query = 'SELECT is_admin FROM user WHERE username = "{}"'.format(username)
    cursor.execute(query)
    admin = cursor.fetchone()
#    admin = int(admin[0])
    print(f'this is admin {admin}')

    if admin == (1,):
        connection.commit()
        cursor.close()
        connection.close()
        return True
    else:
        connection.commit()
        cursor.close()
        connection.close()
        return False


def current_user():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT username FROM current_user;'
    cursor.execute(query)
    username = cursor.fetchone()
    print(username)
    return username[0]

def log_in(user_name,password):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT count(*) FROM user WHERE username = "{}" AND password = "{}";'.format(user_name, password)
    cursor.execute(query)
    result_tuple = cursor.fetchone()
#    print(result_tuple)
    if result_tuple[0] == 0:
#        print('false')
        return False
    elif result_tuple[0] == 1:
#        print('true')
        cursor.execute("""
            UPDATE current_user SET username = '{}' WHERE pk = 1;""".format(user_name))
        connection.commit()
        return True
    else:
        pass
    cursor.close()
    connection.close()

def create_(new_user,new_password,new_fund,admin):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(
        """INSERT INTO user(
            username,
            password,
            current_balance,
            is_admin
            ) VALUES(
            "{}",
            "{}",
            {},
            {}
        );""".format(new_user, new_password, new_fund, admin)
    )
    connection.commit()
    cursor.close()
    connection.close()

def updateHoldings():
    username = current_user()
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    query = 'DELETE FROM holdings WHERE num_shares = 0'
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

def sell(username, ticker_symbol, trade_volume):
    #we have to search for how many of the stock we have
    #compare trade volume with how much stock we have
    #if trade_volume <= our stock, proceed
    #else return to menu
    #we need a database to save how much money we have and how much stock
    username = current_user()
    database = 'trade_information.db'
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT count(*), num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, ticker_symbol)
    cursor.execute(query)
    fetch_result = cursor.fetchone()
    if fetch_result[0] == 0:
        number_shares = 0
    else:
        current_number_shares = fetch_result[1]


    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    current_balance = get_user_balance(username) #TODO un-hardcode this value
    print("Price", last_price)
    print("brokerage fee", brokerage_fee)
    print("current balance", current_balance)
    transaction_revenue = (trade_volume * last_price) - brokerage_fee
    print("Total revenue of Transaction:", transaction_revenue)
    agg_balance = float(current_balance) + float(transaction_revenue)
    print("\nExpected user balance after transaction:", agg_balance)
    return_list = (last_price, brokerage_fee, current_balance, trade_volume,agg_balance,username,ticker_symbol, current_number_shares)


    if current_number_shares >= trade_volume:
        return True, return_list #success
    else:
        return False, return_list
    #if yes return new balance = current balance - transaction cost

def sell_db(return_list):
# return_list = (last_price, brokerage_fee, current_balance, trade_volume, agg_balance, username, ticker_symbol, current_number_shares)
    #check if user holds enough stock
    #update user's balance
    #insert transaction
    #if user sold all stocks holdings row should be deleted not set to 0
    database = 'trade_information.db'
    connection = sqlite3.connect(database,check_same_thread = False)
    cursor = connection.cursor()
    last_price = return_list[0]
    brokerage_fee = return_list[1]
    current_balance = return_list[2]
    trade_volume = return_list[3]
    agg_balance = return_list[4]
    username = return_list[5]
    ticker_symbol = return_list[6]
    current_number_shares = return_list[7]

    #user
    cursor.execute("""
        UPDATE user
        SET current_balance = {}
        WHERE username = '{}';
    """.format(agg_balance, username)
    )
    #transactions
    cursor.execute("""
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        owner_username,
        last_price
        ) VALUES(
        '{}',{},'{}',{}
        );""".format(ticker_symbol,trade_volume*-1,username,last_price)
    )
    #holdings
    #at this point, it it assumed that the user has enough shares to sell.
    if current_number_shares >= trade_volume: #if user isn't selling all shares of a specific company
        tot_shares = float(current_number_shares)-float(trade_volume)
        cursor.execute('''
            UPDATE holdings
            SET num_shares = {}, last_price = {}
            WHERE username = "{}" AND ticker_symbol = "{}";
        '''.format(tot_shares, last_price, username, ticker_symbol)
        )
    connection.commit()
    cursor.close()
    connection.close()


def buy(username, ticker_symbol, trade_volume):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'
    #we need to return True or False for the confirmation message
    trade_volume = float(trade_volume)
    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    username = current_user()
#    print(username)
    current_balance = get_user_balance(username) #TODO un-hardcode this value
    print("last price", last_price)
    print("brokerage fee", brokerage_fee)
    print("current balance", current_balance)
    transaction_cost = (trade_volume * last_price) + brokerage_fee
    print("Total cost of Transaction:", transaction_cost)
    left_over = float(current_balance) - float(transaction_cost)
    print("\nExpected user balance after transaction:", left_over)
    return_list = (last_price, brokerage_fee, current_balance, trade_volume,left_over,username,ticker_symbol)
    if transaction_cost <= current_balance:
        return True, return_list #success
    else:
        return False, return_list
    #if yes return new balance = current balance - transaction cost



def buy_db(return_list): # return_list = (last_price, brokerage_fee, current_balance, trade_volume, left_over, username, ticker_symbol)
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'
    username = current_user()
    connection = sqlite3.connect(database,check_same_thread = False)
    cursor = connection.cursor()
    last_price = return_list[0]
    brokerage_fee = return_list[1]
    current_balance = return_list[2]
    trade_volume = return_list[3]
    left_over = return_list[4]
    username = return_list[5]
    ticker_symbol = return_list[6]

    #update users(current_balance), stocks, holdings.
    #users
        #updating the balance of the user
    cursor.execute("""
        UPDATE user
        SET current_balance = {}
        WHERE username = '{}';
    """.format(left_over, username)
    )
    #transactions
    cursor.execute( """
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        owner_username,
        last_price
        ) VALUES(
        '{}',{},'{}',{}
        );""".format(ticker_symbol,trade_volume,username,last_price)
    )

        #inserting information
    #holdings
    query = 'SELECT count(*), num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, ticker_symbol)
    cursor.execute(query)
    fetch_result = cursor.fetchone()
    if fetch_result[0] == 0: #if the user didn't own the specific stock
        cursor.execute('''
            INSERT INTO holdings(last_price, num_shares, ticker_symbol, username)
            VALUES (
            {},{},"{}","{}"
            );'''.format(last_price, trade_volume, ticker_symbol, username)
        )
    else: #if the user already has the same stock
        tot_shares = float(fetch_result[1])+float(trade_volume)
        cursor.execute('''
            UPDATE holdings
            SET num_shares = {}, last_price = {}
            WHERE username = "{}" AND ticker_symbol = "{}";
        '''.format(tot_shares, last_price, username, ticker_symbol)
        )
    connection.commit()
    cursor.close()
    connection.close()

def get_user_balance(username):
    connection = sqlite3.connect('trade_information.db', check_same_thread = False)
    cursor = connection.cursor()
    username = current_user()
    print(username)
    query = 'SELECT current_balance FROM user WHERE username = "{}";'.format(username)
#    print(f'query{query}')
    cursor.execute(query)
    fetched_result = cursor.fetchone()
#    print(f'fetched{fetched_result}')
    cursor.close()
    connection.close()
    return fetched_result[0] #cursor.fetchone() returns tuples

def calculate_balance(ticker_symbol, trade_volume):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'

    current_balance = 1000.0 #TODO un-hardcode this value
    last_price = float(quote_last_price(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    transaction_cost = (trade_volume * last_price) + brokerage_fee
    new_balance = current_balance - transaction_cost
    return new_balance


def lookup_ticker_symbol(company_name):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'

    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input='+company_name
    #FIXME The following return statement assumes that only one
    #ticker symbol will be matched with the user's input.
    #FIXME There also isn't any error handling.
    return json.loads(requests.get(endpoint).text)[0]['Symbol']


def quote_last_price(ticker_symbol):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol='+ticker_symbol
    return json.loads(requests.get(endpoint).text)['LastPrice']

def calculate_p_and_l(username):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'

    #getting all ticker symbols for current user
    all_ticker_symbols = 'SELECT ticker_symbol FROM holdings WHERE username = "{}"'.format(username)
    cursor.execute(all_ticker_symbols)
    ticker_symbols = [t[0] for t in cursor.fetchall()]
    ticker_symbols = list(ticker_symbols)
    p_and_l= 0
    for symbol in ticker_symbols:
        stock_transactions = 'SELECT * FROM transactions WHERE owner_username = "{}" and ticker_symbol = "{}"'.format(username, symbol)
        cursor.execute(stock_transactions)
        transactions = cursor.fetchall()
        print(username,symbol)
        total_shares = 0
        price = 0
        print(f' transactions{transactions}')

# do this instead
# SELECT sum(num_shares*last_price) from transactions where owner_username = 'John' AND ticker_symbol = 'x';
        for transaction in transactions:

            ticker_symbol = transaction[1]
            trade_volume = transaction[2]
            username = transaction[3]
            last_price = transaction[4]

            shares = 'SELECT num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, symbol)
            cursor.execute(shares)
            num_shares = cursor.fetchall()
            num_shares = num_shares[0][0]

            total_shares += num_shares
            print(f'this is the num_shares {num_shares}')
            print(f'total shares {total_shares}')

            purchased_price  = 'SELECT last_price FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, symbol)
            cursor.execute(purchased_price)
            purchased_price = cursor.fetchall()
            purchase_price = purchased_price[0][0]
            print(f' this is the purchjase price{purchase_price}')
            price += num_shares * purchase_price
            price += price/total_shares
        print(f'this is the price {price}')
        print(f'this is the total shares {total_shares}')
        p_and_l += price/total_shares

    connection.commit()
    cursor.close()
    connection.close()
    return p_and_l



def leaderboard():
    return 'this is the leaderboard you are an admin'
#    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
#    cursor = connection.cursor()

#    query_one = "SELECT username FROM holdings;"
#    cursor.execute(query_one)
#    usernames = cursor.fetchall()

#    print(usernames)

#    for user in usernames:
#        query_two = 'SELECT current_balance FROM user WHERE username="{}";'.format(user)
#        cursor.execute(query_two)
#        cash = cursor.fetchone()

#        ticker_symbol = []
#        query_three = cursor.execute('SELECT ticker_symbol FROM holdings WHERE username = "{}";'.format(user))
#        cursor.execute(query_three)
#        ticker_symbol = fetchall()

#        for ticker in ticker_symbol:
#            query_four = cursor.execute('SELECT (last_price*num_shares) FROM holdings WHERE ticker_symbol= "{}";'.format(ticker))
#            cursor.execute(query_four)
#            holding_mv= fetchone()

#    cursor.execute("""
#        UPDATE leaderboard(username)
#        VALUES(
#        '{}',{}
#        );""".format(user, total_mv)
#    )
#    leaderboard = ("SELECT * FROM leaderboard")

#    total_mv = cash + holding_mv
#    leaderboard = f'{username} {total_mv}\n'

#    connection.commit()
#    cursor.close()
#    connection.close()
#    return leaderboard
#    cash = cursor.execute("SELECT current_balance FROM user WHERE username = {};".format(username))
#    username = current_user()
#    symbols=cursor.execute("SELECT ticker_symbol FROM holdings WHERE user='{}'".format(username))
#    for symbol in symbols:
#        last_sale = float(quote_last_price(symbol))
#        select num_shares per symbol
#        shares = cursor.execute("SELECT num_shares FROM holdings WHERE ticker_symbol='{}'".format(symbol))
#        profit = last_sale

def holdings():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'

    username = current_user()
    query = 'SELECT * FROM holdings WHERE username = "{}";'.format(username)
    cursor.execute(query)
    holdings = cursor.fetchall()
    return holdings

    curor.close()
    connection.close()



def log_out():
    log_in('aosdnoindc','aonsdoianf')
    try:
        cursor.close()
        connection.close()
    except:
        print('connection already closed')


if __name__ == '__main__':
    # print(lookup_ticker_symbol("tesla"))
    # print(find_quote("tesla"))
    # print(lookup_ticker_symbol('asdfajHLSKDJHFA')) #FIXME This is the code that isn't passing
#    print(calculate_p_and_l('John'))
    print(leaderboard())
#    print(is_admin())

