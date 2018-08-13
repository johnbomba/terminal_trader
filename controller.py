#!/usr/bin/env python3

import model
import view
import time
import os
import sqlite3
#the model is the biz logic
#controller is the router
#view is user interface
#run.sh is an alternative to controller.py



#for game servers, you want an infinite loop or else it will crash

connection = sqlite3.connect('trade_information.db',check_same_thread=False)
cursor = connection.cursor()

def game_loop():
    current_username = ''
    condition = True
    while 1:
        user_choice = view.log_or_sign()
        user_choice = user_choice.lower()
        log_in = ['l','login']
        create_ = ['c','create']
        exit_ = ['e','exit']
        accept_input = log_in     \
                      +create_     \
                      +exit_
        if user_choice in accept_input:
            if user_choice in log_in:
                (user_name, password) = view.log_menu()
                current_username = user_name
                has_account = model.log_in(user_name, password)
                if has_account:
                    break
                else:
                    print('WRONG LOGIN INFORMATION. TRY AGAIN')
                    import time
                    time.sleep(3)
            elif user_choice in exit_:
                condition = False
                m.log_out()
                os.system('clear')
                break

            elif user_choice in create_:
                #(new_user,new_password,new_funds) = view.create_menu()
         #       new_user = input("username:")
         #       new_password = input("password:")
         #       new_funds = input('fund:')
         #       newer_funds = float(new_funds)
                (new_user,new_password,new_funds) = view.create_menu()
                newuser = new_user,new_password,new_funds
                cursor.execute(
                    """INSERT INTO user(
                        username,
                        password,
                        current_balance
                    ) VALUES(?,?,?
                    )""", newuser
                )
                connection.commit()
                cursor.close()
                connection.close()

                print("You have signed up!")
                import time
                time.sleep(3)

    while condition:
        buy_inputs = ['b', 'buy']
        sell_inputs = ['s', 'sell']
        lookup_inputs = ['l', 'lookup']
        quote_inputs = ['q', 'quote']
        exit_inputs = ['e', 'exit']
        acceptable_inputs = buy_inputs     \
                            +sell_inputs   \
                            +lookup_inputs \
                            +quote_inputs  \
                            +exit_inputs
        user_input = view.main_menu()
        if user_input in acceptable_inputs:
            if user_input in buy_inputs:
                (ticker_symbol, trade_volume) = view.buy_menu()
                confirmation_message, return_list = model.buy(current_username, ticker_symbol, trade_volume)
                if confirmation_message == True:
                    yes = ['y', 'yes']
                    no = ['n', 'no']
                    choice = input("You have enough money. Would you like to buy this stock?\n[y] Yes\n[n] No\n")
                    if choice in yes:
                        model.buy_db(return_list)
                    else:
                        print("Returning to main menu.")
                else:
                    print("You do not have enough money to buy this stock.")
            elif user_input in sell_inputs:
                (ticker_symbol, trade_volume) = view.sell_menu()
                confirmation_message, return_list = model.sell(current_username, ticker_symbol, trade_volume)#TODO
                if confirmation_message == True:
                    yes = ['y', 'yes']
                    no = ['n', 'no']
                    choice = input("You have enough shares to sell. Would you like to sell this stock?\n[y] Yes\n[n] No\n")
                    if choice.lower() in yes:
                        model.sell_db(return_list)#TODO
                    else:
                        print("Returning to main menu.")
                else:
                    print("You do not have enough shares to sell.")

            elif user_input in lookup_inputs:
                company_name = view.lookup_menu()
                print(model.lookup_ticker_symbol(company_name))
            elif user_input in quote_inputs:
                #TODO
                ticker_symbol = view.quote_menu()
                print(model.quote_last_price(ticker_symbol))
                #import time
                #time.sleep(5)
            elif user_input in exit_inputs:
                os.system('clear')
                break
            else:
                #catches huge error
                #should contain a fallback function
                pass
        else:
            pass
        model.updateHoldings()
        import time
        time.sleep(3)





if __name__ == '__main__':
    game_loop()
