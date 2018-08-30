#!usr/bin/env python3
import model as m
import time
import os
import sqlite3

from flask import Flask, render_template, request, redirect, session, jsonify

app = Flask(__name__)
username = ''

def api_authenticate(apikey):
    row = m.api_authenticate(apikey)
    if row is None:
        return None, None
    else:
        return row

def errormsg(message):
    return jsonify({
            "error": True,
            "message": message
        })

@app.route("/api/getbalance/<apikey>", methods=["GET"])
def getbalance(apikey):
    pk, username = api_authenticate(apikey)
    if not pk:
        return errormsg("could not authenticate")
    else:
        balance = "{:.2f}".format(m.get_user_balance(username))
        return jsonify({
            "error": False,
            "username": username,
            "balance": balance,
            "message": "Request succeeded"
        })

@app.route("/api/buy/<apikey>", methods=["POST"])
def _buy(apikey):
    pk, username = api_authenticate(apikey)
    if not pk:
        return errormsg("could not authenticate")
    if not request.json:
        return errormsg("no buy order")
    if "symbol" not in request.json or "amount" not in request.json:
        return errormsg("bad order")
    try:
        amount = int(request.json["amount"])
    except:
        return errormsg("bad amount")
    symbol = request.json["symbol"]

    response = m.buy(username, symbol, amount)
    if not response:
        return jsonify({
            "error" : True,
            "symbol" : symbol,
            "amount" : amount,
            "message": "Buy order failed"
        })
    else:
        return jsonify({
            "error" : False,
            "symbol" : symbol,
            "amount" : amount,
            "message" : "Buy order succeeded"
        })

@app.route("/api/sell/<apikey>", methods=["POST"])
def _sell(apikey):
    pk, username = api_authenticate(apikey)
    if not pk:
        return errormsg("could not authenticate")
    if not request.json:
        return errormsg("no sell order")
    if "symbol" not in request.json or "amount" not in request.json:
        return errormsg("bad order")
    try:
        amount = int(request.json["amount"])
    except:
        return errormsg("bad amount")
    symbol = request.json["symbol"]

    response = m.sell(username, symbol, amount)
    if not response:
        return jsonify({
            "error" : True,
            "symbol" : symbol,
            "amount" : amount,
            "message": "Buy order failed"
        })
    else:
        return jsonify({
            "error" : False,
            "symbol" : symbol,
            "amount" : amount,=
            "message" : "Sell order succeeded"
        })



@app.route("/api/quote/<apikey>", methods=["GET"])
def _quote(apikey):
pk, username = api_authenticate(apikey)
    if not pk:
        return errormsg("could not authenticate")
    if not request.json:
        return errormsg("Invalid format")
    if "symbol" not in request.json:
        return errormsg("bad order")
    symbol = request.json["symbol"]

    response = m.quote_last( symbol)
    if not response:
        return jsonify({
            "error" : True,
            "symbol" : symbol,
            "LastPrice" : LastPrice,
            "message": "quote failed"
        })
    else:
        return jsonify({
            "error" : False,
            "symbol" : symbol,
            "LastPrice" : LastPrice,=
            "message" : "last sale"
        })

@app.rout("/api/lookup/<apikey>", methods=["GET"])
def _lookup(apikey):
    if not pk:
        return errormsg("could not authenticate")
    if not request.json:
        return errormsg("Invalid format")
    if "company" not in request.json:
        return errormsg("No company name")
    company = request.json["company"]

    response = m.lookup_ticker_symbol(company_name)
if not response:
        return jsonify({
            "error" : True,
            "company_name" : company_name,
            "message": "look up failed"
        })
    else:
        return jsonify({
            "error" : False,
            "company_name" : company_name,=
            "message" : "last sale"
        })





##########################################

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="GET":
        return render_template('login.html')
    else:
        submitted_username= request.form['username']
        submitted_password = request.form['password']
        result = m.log_in(submitted_username,submitted_password)
        if result == True:
            username = submitted_username
            #print(username)
            return redirect('/menu')
        else:
            print('please try again')
            return redirect('/login')

@app.route('/menu',methods=['GET','POST'])
def index():
    if request.method=="GET":
        return render_template('menu.html')
    else:
        pass

@app.route('/create',methods=['GET','POST'])
def create():
    if request.method=="GET":
        return render_template('create.html')
    else:
        submitted_username = request.form['username']
        submitted_password = request.form['password']
        submitted_funds = request.form['funds']
        try:
            submitted_admin = request.form['admin']
        except:
            submitted_admin = 0

#        submitted_admin = request.form['admin']

#        if submitted_admin:
#            submitted_admin = 1
#        else:
#            submitted_admin = 0

        result = m.create_(submitted_username,submitted_password,submitted_funds,submitted_admin)
        return redirect('/login')

@app.route('/lookup',methods=['GET','POST'])
def look_up():
    if request.method=="GET":
        return render_template('lookup.html')
    else:
        submitted_company_name=request.form['company_name']
        result = m.lookup_ticker_symbol(submitted_company_name)
        return render_template('lookup.html',result=result)

@app.route('/quote',methods=['GET','POST'])
def quote():
    if request.method=="GET":
        return render_template('quote.html')
    else:
        submitted_symbol=request.form['ticker_symbol']
        result = m.quote_last(submitted_symbol)
        return render_template('quote.html',result=result)
# TODO app.route trade should do both buys and sells
# @app.route('/trade',methods=['GET','POST'])
# def buy():
#    if request.method=="GET":
#        return render_template('trade.html')
#    else:
#       pass

@app.route('/buy',methods=['GET','POST'])
def buy():
    username = m.current_user()
    if request.method=="GET":
        return render_template('buy.html')
    else:
        submitted_symbol=request.form['ticker_symbol']
        submitted_volume=request.form['number_of_shares']
        submitted_volume = int(submitted_volume)
        confirmation_message, return_list = m.buy(username,submitted_symbol,submitted_volume)
        result = f"You paid {m.quote_last(submitted_symbol)} for {submitted_volume} shares of {submitted_symbol}."
        if confirmation_message == True:
            return render_template('buy.html', result=result)
        else:
            return render_template('buy.html')

@app.route('/sell',methods=['GET','POST'])
def sell():
    username = m.current_user()
    if request.method=="GET":
        return render_template('sell.html')
    else:
        submitted_symbol=request.form['ticker_symbol']
        submitted_volume=request.form['number_of_shares']
        submitted_volume = int(submitted_volume)
        confirmation_message, return_list = m.sell(username,submitted_symbol,submitted_volume)
        result = f"You sold {submitted_volume} shares of {submitted_symbol} at {m.quote_last(submitted_symbol)}"
        if confirmation_message == True:
            return render_template('sell.html', result=result)
        else:
            return render_template('sell.html')

@app.route('/holdings',methods=['GET','POST'])
def holdings():
    username=m.current_user()
    if request.method=="GET":
        result= m.holdings()
        return render_template('holdings.html', result=result)
    else:
        return render_template('holdings.html')

@app.route('/history',methods=['GET','POST'])
def history():
    username=m.current_user()
    if request.method=="GET":
        result = m.history()
        return render_template('history.html', result=result)
    else:
        return render_template('history.html')

@app.route('/leaderboard',methods=['GET','POST'])
def leaderboard():
    if request.method=="GET":
        m.calculate_p_and_l()
        result = m.leaderboard()
        return render_template('leaderboard.html', result=result)
    else:
        pass

if __name__ == '__main__':
    app.run(debug=True)

