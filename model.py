#!/usr/bin/env python

import json

import sqlite3
import requests
import uuid

def is_admin():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
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
    query = 'SELECT count(*), username FROM current_user;'
    cursor.execute(query)
    username = cursor.fetchone()
    count = int(username[0])
    username = username[1]
    if count == 0:
        cursor.execute("INSERT INTO current_user(username)VALUES('oaisfhaoidj');"  )
        connection.commit()
        cursor.close()
        connection.close()
    else:
        return username
        cursor.close()
        connection.close()

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
    api_key = uuid.uuid4()
    cursor.execute(
        f"""INSERT INTO user(
            username,
            password,
            current_balance,
            is_admin,
            api_key
            ) VALUES(
            "{new_user}",
            "{new_password}",
            {new_fund},
            {admin},
            "{api_key}"
        );"""
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
    username = current_user()
    connection = sqlite3.connect('trade_information.db', check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT count(*), num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, ticker_symbol)
    cursor.execute(query)
    fetch_result = cursor.fetchone()
    if fetch_result[0] == 0:
        number_shares = 0
    else:
        current_number_shares = fetch_result[1]


    last_price = float(quote_last(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    current_balance = get_user_balance(username) #TODO un-hardcode this value
    print("Price", last_price)
    print("brokerage fee", brokerage_fee)
    print("current balance", current_balance)
    transaction_revenue = (trade_volume * last_price) - brokerage_fee
    print("Total revenue of Transaction:", transaction_revenue)
    agg_balance = float(current_balance[0]) + float(transaction_revenue)
    print("\nExpected user balance after transaction:", agg_balance)
    return_list = (last_price, brokerage_fee, current_balance, trade_volume,agg_balance,username,ticker_symbol, current_number_shares)

    if current_number_shares >= trade_volume:
        sell_db(return_list)
        updateHoldings()
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
    cursor.execute(f"""
        UPDATE user
        SET current_balance = {agg_balance}
        WHERE username = '{username}';
    """)
    
    #transactions
    cursor.execute("""
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        username,
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
    trade_volume = float(trade_volume)
    print(f" this is the buy symbol{ticker_symbol}")
    last_price = float(quote_last(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    username = current_user()
    print(f' buy functon username {username}')
    current_balance = get_user_balance(username) #TODO un-hardcode this value
    print("last price", last_price)
    transaction_cost = (trade_volume * last_price) + brokerage_fee
    left_over = float(current_balance[0]) - float(transaction_cost)
    return_list = (last_price, brokerage_fee, current_balance[0], trade_volume,left_over,username,ticker_symbol)
    if transaction_cost <= current_balance[0]:
        buy_db(return_list)
        return True, return_list #success
    else:
        return False, return_list
    #if yes return new balance = current balance - transaction cost



def buy_db(return_list): # return_list = (last_price, brokerage_fee, current_balance, trade_volume, left_over, username, ticker_symbol)
    print(f'this si the return list {return_list}')
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'
    username = current_user()
    connection = sqlite3.connect(database,check_same_thread = False)
    cursor = connection.cursor()
    last_price = return_list[0]
    trade_volume = return_list[3]
    left_over = return_list[4]
    username = return_list[5]
    ticker_symbol = return_list[6]

    #update users(current_balance), stocks, holdings.
    #users
        #updating the balance of the userINSERT INTO
    cursor.execute(f"""
        UPDATE user
        SET current_balance = {left_over}
        WHERE username = '{username}'
    ;"""
    )
    #transactions
    cursor.execute(f"""
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        username,
        last_price
        ) VALUES(
        '{ticker_symbol}',{trade_volume},'{username}',{last_price}
        );"""
    )

        #inserting information
    #holdings
    query = 'SELECT count(*), num_shares, avg_price FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, ticker_symbol)
    cursor.execute(query)
    fetch_result = cursor.fetchone()
    print(f'fetch result {fetch_result}')
    if fetch_result[0] == 0: #if the user didn't own the specific stock
        cursor.execute(f'''
            INSERT INTO holdings(last_price, num_shares, ticker_symbol, username, avg_price)
            VALUES (
            {last_price},{trade_volume},"{ticker_symbol}","{username}","{last_price}"
            );'''
        )
    else: #if the user already has the same stock
        tot_shares = float(fetch_result[1])+float(trade_volume)
        print(f' tot shares  {tot_shares}')
        calc_avg = (float(fetch_result[2]*float(fetch_result[1]) + trade_volume*last_price)/tot_shares)
        print(f'calc avg {calc_avg}')
        cursor.execute(f'''
            UPDATE holdings
            SET num_shares = {tot_shares}, last_price = {last_price}, avg_price ={calc_avg}
            WHERE username = "{username}" AND ticker_symbol = "{ticker_symbol}";
        ''')
        
    
    connection.commit()
    cursor.close()
    connection.close()

def get_user_balance(username):
    connection = sqlite3.connect('trade_information.db', check_same_thread = False)
    cursor = connection.cursor()
    username = current_user()
    print(username)
    query = f'SELECT current_balance FROM user WHERE username = "{username}";'
    cursor.execute(query)
    fetched_result = cursor.fetchone()
    print(f' this is the get balance result {fetched_result}')
    cursor.close()
    connection.close()
    return fetched_result #cursor.fetchone() returns tuples

def calculate_balance(ticker_symbol, trade_volume):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    database = 'trade_information.db'

    current_balance = 1000.0 #TODO un-hardcode this value
    last_price = float(quote_last(ticker_symbol))
    brokerage_fee = 6.95 #TODO un-hardcode this value
    transaction_cost = (trade_volume * last_price) + brokerage_fee
    new_balance = current_balance - transaction_cost
    return new_balance


def lookup_ticker_symbol(company_name):
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input='+company_name
    #FIXME The following return statement assumes that only one
    #ticker symbol will be matched with the user's input.
    #FIXME There also isn't any error handling.
    return json.loads(requests.get(endpoint).text)[0]['Symbol']


def quote_last(ticker_symbol):
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol='+ticker_symbol
    return json.loads(requests.get(endpoint).text)['LastPrice']

def calculate_p_and_l():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    query_hold = f'SELECT * FROM holdings'
    cursor.execute(query_hold)
    holding_info = cursor.fetchall()
    print(f'this is the holding info {holding_info}')
    update_leaderboard(holding_info)
    cursor.close()
    connection.close()

def update_leaderboard(holding_info):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    print(f'\n\n\n\n this is the update leaderboard function {holding_info}\n\n\n\n')
    for item in holding_info:
        name = item[1]
        symbol = item[2]
        shares = item[3]
        last =  item[4]
        avg = item[5]
        p_and_l = shares * (last - avg)
        x = cursor.execute(f'SELECT count(*) FROM leaderboard WHERE username = "{name}";')
        count = cursor.fetchall()
        count = count [0][0]
        if count == 0:
            cursor.execute(f"""
            INSERT INTO leaderboard(
            p_and_l, username)
            VALUES(
            {p_and_l}, "{name}");""")
            # print(shares)
            # print(p_and_l)

        else:
                cursor.execute("""
            UPDATE leaderboard
            SET p_and_l=?
            WHERE username=?
            ;""", (p_and_l, name))

    connection.commit()
    cursor.close()
    connection.close()

def leaderboard():
    # return 'this is the leaderboard you are an admin'
    if is_admin() == True:
        calculate_p_and_l()
        connection = sqlite3.connect('trade_information.db',check_same_thread=False)
        cursor = connection.cursor()
        query = 'SELECT username, p_and_l FROM leaderboard;'
        cursor.execute(query)
        raw_leaderboard = cursor.fetchall()
        print(f'\n\n\n\n leaderboad {raw_leaderboard} \n\n\n\n')
        query_two = 'SELECT username, current_balance FROM user'
        cursor.execute(query_two)
        raw_user = cursor.fetchall()
        print(f'\n\nraw user {raw_user}\n\n')

        
        leaderboard = [] 


        return leaderboard
    else: 
        return 'you must be an admin to view this page'

def holdings():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    username = current_user()
    query = 'SELECT * FROM holdings WHERE username = "{}";'.format(username)
    cursor.execute(query)
    holdings = cursor.fetchall()
    cursor.close()
    connection.close()
    return holdings

def history():
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    username = current_user()
    # print(username)
    query = f'SELECT * FROM transactions WHERE username = "{username}"'
    cursor.execute(query)
    history = cursor.fetchall()
    print(history)
    cursor.close()
    connection.close()
    return history


def log_out():
    log_in('loggedout','aonsdoianf')
    try:
        cursor.close()
        connection.close()
    except:
        print('connection already closed')

def api_authenticate(apikey):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    SQL = "SELECT pk,username FROM user WHERE api_key=?;"
    cursor.execute(SQL, (apikey,))
    row = cursor.fetchone()
    response = row
    print(row)
    cursor.close()
    connection.close()
    return response

def api_key(pk):
    connection = sqlite3.connect('trade_information.db',check_same_thread=False)
    cursor = connection.cursor()
    SQL="SELECT api_key FROM user WHERE pk = ?;"
    cursor.execute(SQL, (pk,))
    row = cursor.fetchone()
    connection.close()
    return row[0]

# TODO refactor all the functions above using the following connection & close functions

# def connect():
#     connection = sqlite3.connect('trade_information.db',check_same_thread=False)
#     cursor = connection.cursor()

# def  close():
#     cursor.close()
#     connection.close()


if __name__ == '__main__':
    # print(lookup_ticker_symbol("tesla"))
    # print(find_quote("tesla"))
    # print(lookup_ticker_symbol('asdfajHLSKDJHFA')) #FIXME This is the code that isn't passing
    # print(calculate_p_and_l('John'))
    # print(leaderboard())
    # print(is_admin())
    # print(api_key(1))
    print(api_authenticate('2d0ce0c7-e264-449e-a6a2-89ed260da95b'))
