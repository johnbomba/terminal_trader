#!/usr/bin/env python3

import sqlite3

connection = sqlite3.connect('trade_information.db',check_same_thread=False)
cursor = connection.cursor()

cursor.execute(
    """CREATE TABLE user(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password VARCHAR,
        current_balance FLOAT,
        is_admin INTEGER,
        api_key VARCHAR
    );"""
)

cursor.execute(
    """CREATE TABLE transactions(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR,
        ticker_symbol TEXT,
        num_shares FLOAT,
        last_price FLOAT,
        FOREIGN KEY(username) REFERENCES user(username)
    );"""
)

cursor.execute(
    """CREATE TABLE holdings(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(16),
        ticker_symbol VARCHAR(16),
        num_shares FLOAT,
        last_price FLOAT,
        avg_price FLOAT,
        FOREIGN KEY (username) REFERENCES user(username)
    );"""
)

cursor.execute(
    """CREATE TABLE leaderboard(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR,
        p_and_l FLOAT,
        FOREIGN KEY (username) REFERENCES user(username)
    );"""
)

cursor.execute(
    """CREATE TABLE current_user(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR
    );"""
)

cursor.close()
connection.close()

