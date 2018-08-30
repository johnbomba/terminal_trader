#! usr/bin/env python3
import datetime
import json
import requests
import pandas as pd
from pprint import pprint

prefix = 'https://api.iextrading.com/1.0'

def quote():
    stock = input('stock symbol: ')
    quote = prefix+f'/stock/{stock}/quote'
    print(quote)
    
    
    return json.loads(requests.get(quote).text)

def book():
    stock = input("stocksymbol: ")
    book = prefix+f"/stock/{stock}/book"
    pprint(book)
    return json.loads(requests.get(book).text)

def chart():
    stock = input("stocksymbol: ")
    chart = prefix+f"/stock/{stock}/chart/1y"
    return chart

def earnings():
    stock = input("stocksymbol: ")
    earn = prefix+f'/stock/{stock}/earnings'
    return earn

if __name__ == '__main__':
    # Spprint(quote())
    pprint(book())
    # pprint(chart())    
    # pprint(earnings())