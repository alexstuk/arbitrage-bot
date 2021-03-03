import btceAPI, poloniexAPI, krakenAPI, gdaxAPI
from krakenAPI import krak
import urllib.request
import json
from threading import Thread
from time import sleep
from datetime import datetime
import os
import socket
from threading import Thread
import requests


class Exchange:
    
    # After selling or buying info about the trade
    deal_details = {}
    
    # Info about the last trade before the current
    deal_details_old = {}
    
    # Info about a canceled order
    cancel_details = {}
    
    # Trade fee
    fee = 0
    
    # API Request string for an exchange
    urldata = ''
    
    # Initial and current amount of ethereum and bitcoin on the exchange
    start_eth, eth = 0, 0
    start_btc, btc = 0, 0
    
    # Amount of ethereum, bitcoin on an exchange after the deal adjusted to take into account the order book values
    adj_eth = 0
    adj_btc = 0
    
    # Price and amount of crypto when bought/sold
    buy_price = 0
    sell_price = 0
    buy_amount = 0
    sell_amount = 0
    
    # Required minimum profit to make the deal profitable
    min_profit = 0

    # Assigning some number to order_ID
    order_id = 777777


    def __init__(self, ex_name):
        self.__name = ex_name
        self.name = ex_name

    def sell(self):
        pass

    def buy(self):
        pass

    # Refreshing buy/sell price for various exchanges by loading order book information

    def refresh_price_polo(self):
        urldata = 'https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_ETH&depth=30'
        s = requests.Session()
        try:
            r = s.get(urldata, timeout=5)
            text = r.text
            the_json = json.loads(text)
            self.buy_price = float(the_json['asks'][0][0])
            self.buy_amount = float(the_json['asks'][0][1])
            self.sell_price = float(the_json['bids'][0][0])
            self.sell_amount = float(the_json['bids'][0][1])
        finally:
            s.close()

    def refresh_price_btce(self):
        urldata = 'https://btc-e.com/api/3/depth/eth_btc'
        s = requests.Session()
        try:
            r = s.get(urldata, timeout=5)
            text = r.text
            the_json = json.loads(text)
            self.sell_price = float(the_json['eth_btc']['bids'][0][0])
            self.sell_amount = float(the_json['eth_btc']['bids'][0][1])
            self.buy_price = float(the_json['eth_btc']['asks'][0][0])
            self.buy_amount = float(the_json['eth_btc']['asks'][0][1])
        finally:
            s.close()

    def refresh_price_kraken(self):
        the_json = krakenAPI.krak.query_public('Depth', {'pair': 'XETHXXBT', 'count': 5})
        self.buy_price = float(the_json['result']['XETHXXBT']['asks'][0][0])
        self.buy_amount = float(the_json['result']['XETHXXBT']['asks'][0][1])
        self.sell_price = float(the_json['result']['XETHXXBT']['bids'][0][0])
        self.sell_amount = float(the_json['result']['XETHXXBT']['bids'][0][1])

    def refresh_price_gdax(self):
        urldata = 'https://api.gdax.com/products/ETH-BTC/book?level=1'
        s = requests.Session()
        try:
            r = s.get(urldata, timeout=5)
            text = r.text
            the_json = json.loads(text)
            self.sell_price = float(the_json['bids'][0][0])
            self.sell_amount = float(the_json['bids'][0][1])
            self.buy_price = float(the_json['asks'][0][0])
            self.buy_amount = float(the_json['asks'][0][1])
        finally:
            s.close()

    # Buy/sell methods for various exchanges

    def sell_polo(self, rate, amount):
        return poloniexAPI.polo.sell('BTC_ETH', rate, amount)

    def buy_polo(self, rate, amount):
        return poloniexAPI.polo.buy('BTC_ETH', rate, amount)

    def sell_btce(self, rate, amount):
        p = str(rate)
        rate = float(p[0:7])
        p = str(amount)
        amount = float(p[0:7])
        return btceAPI.btce.Trade('eth_btc', 'sell', rate, amount)

    def buy_btce(self, rate, amount):
        p = str(rate)
        rate = float(p[0:7])
        p = str(amount)
        amount = float(p[0:7])
        return btceAPI.btce.Trade('eth_btc', 'buy', rate, amount)

    def sell_kraken(self, rate, amount):
        return krakenAPI.krak.PlaceOrder('XETHXXBT', 'sell', rate, amount)

    def buy_kraken(self, rate, amount):
        return krakenAPI.krak.PlaceOrder('XETHXXBT', 'buy', rate, amount)

    def sell_gdax(self, rate, amount):
        p = str(rate)
        rate = float(p[0:7])
        p = str(amount)
        amount = float(p[0:8])
        return gdaxAPI.gdax.sell(rate, amount)

    def buy_gdax(self, rate, amount):
        p = str(rate)
        rate = float(p[0:7])
        p = str(amount)
        amount = float(p[0:8])
        return gdaxAPI.gdax.buy(rate, amount)
    
    # Refreshing balances for various exchanges

    def refresh_balances_btce(self):
        balance = btceAPI.btce.getInfo()
        self.eth = round(float(balance['return']['funds']['eth']) - 0.00001, 5)
        self.btc = round(float(balance['return']['funds']['btc']) - 0.00001, 5)

    def refresh_balances_polo(self):
        balance = poloniexAPI.polo.return_balances()
        self.eth = round(float(balance['ETH']) - 0.00001, 5)
        self.btc = round(float(balance['BTC']) - 0.00001, 5)

    def refresh_balances_kraken(self):
        balance = krakenAPI.krak.query_private('Balance')
        self.eth = float(balance['result']['XETH']) - 0.00001
        self.btc = float(balance['result']['XXBT']) - 0.00001

        dict = krakenAPI.krak.query_private('open_orders')

        adj_btc = 0
        adj_eth = 0
        dict = dict['result']['open']
        for key in dict:
            if dict[key]['descr']['type'] == 'buy':
                adj_btc = adj_btc + float(dict[key]['vol']) * float(dict[key]['descr']['price'])
            if dict[key]['descr']['type'] == 'sell':
                adj_eth = adj_eth + float(dict[key]['vol'])

        self.eth = self.eth - adj_eth
        self.btc = self.btc - adj_btc

    def refresh_balances_gdax(self):
        balance = gdaxAPI.gdax.get_accounts()
        for account in balance:
            if account['currency'] == 'BTC':
                self.btc = round(float(account['available']) - 0.00001, 5)
            if account['currency'] == 'ETH':
                self.eth = round(float(account['available']) - 0.00001, 5)
    
    # Method to check if the deal was successful for various exchanges 

    def succesful_deal_btce(self, deal_details):
        if 'return' in deal_details:
            self.order_id = deal_details['return']['order_id']
            if 'success' in deal_details:
                if deal_details['success'] != 0:
                    return True
        return False

    def succesful_deal_poloniex(self, deal_details):
        if 'orderNumber' in deal_details:
            self.order_id = deal_details['orderNumber']
            if 'error' not in deal_details:
                return True
        return False


    def succesful_deal_gdax(self, deal_details):
        if 'id' in deal_details:
            self.order_id = deal_details['id']
            return True
        return False
    
    # Example:
    # {'result': {'descr': {'order': 'buy 0.10000000 ETHXBT @ limit 0.010000'}, 'txid': ['OHBEGS-YHFZZ-O5W2JS']}, 'error': []}

    def succesful_deal_kraken(self, deal_details):
        if 'result' in deal_details:
            if 'txid' in deal_details['result']:
                self.order_id = deal_details['result']['txid'][0]
            if deal_details['error'] == []:
                return True
        return False

    def completed_deal_poloniex(self, deal_details):
        if 'resultingTrades' in deal_details:
            if deal_details['resultingTrades'] == []:
                return False
            else:
                return True

    def completed_deal_btce(self, deal_details):
        if 'return' in deal_details:
            if 'order_id' in deal_details['return']:
                if deal_details['return']['order_id'] == 0:
                    return True
                else:
                    return False


    def completed_deal_kraken(self, deal_details):
        return True

    def completed_deal_gdax(self, deal_details):
        return True

    def open_orders_poloniex(self):
        self.hanging_orders = poloniexAPI.polo.returnopen_orders('BTC_ETH')

    def open_orders_btce(self):
        self.hanging_orders = btceAPI.btce.active_orders('eth_btc')

    def open_orders_kraken(self):
        self.hanging_orders = krakenAPI.krak.get_open_orders()

    def open_orders_gdax(self):
        self.hanging_orders = gdaxAPI.gdax.get_orders()

    def cancel_order_poloniex(self, order_id):
        self.cancel_details = poloniexAPI.polo.cancel('BTC_ETH', order_id)

    def cancel_order_btce(self, order_id):
        self.cancel_detail = btceAPI.btce.cancel_order(order_id)

    def cancel_order_kraken(self, order_id):
        self.cancel_detail = krakenAPI.krak.cancel_order(order_id)

    def cancel_order_gdax(self, order_id):
        self.cancel_detail = gdaxAPI.gdax.cancel_order(order_id)


# Initializing each exchange as an object
Poloniex = Exchange('POLONIEX')
Btce = Exchange('BTC-E')
Kraken = Exchange('KRAKEN')
Gdax = Exchange('GDAX')

Poloniex.hanging_orders = []
Btce.hanging_orders = []
Kraken.hanging_orders = []
Gdax.hanging_orders = []

# Redefining names for all methods to unify call methods
Poloniex.refresh_balances = Poloniex.refresh_balances_polo
Btce.refresh_balances = Btce.refresh_balances_btce
Kraken.refresh_balances = Kraken.refresh_balances_kraken
Gdax.refresh_balances = Gdax.refresh_balances_gdax

Poloniex.refresh_price = Poloniex.refresh_price_polo
Btce.refresh_price = Btce.refresh_price_btce
Kraken.refresh_price = Kraken.refresh_price_kraken
Gdax.refresh_price = Gdax.refresh_price_gdax

Poloniex.buy_function = Poloniex.buy_polo
Poloniex.sell_function = Poloniex.sell_polo
Btce.buy_function = Btce.buy_btce
Btce.sell_function = Btce.sell_btce
Kraken.buy_function = Kraken.buy_kraken
Kraken.sell_function = Kraken.sell_kraken
Gdax.buy_function = Gdax.buy_gdax
Gdax.sell_function = Gdax.sell_gdax


Poloniex.completed_deal = Poloniex.completed_deal_poloniex
Btce.completed_deal = Btce.completed_deal_btce
Kraken.completed_deal = Kraken.completed_deal_kraken
Gdax.completed_deal = Gdax.completed_deal_gdax


Poloniex.succesful_deal = Poloniex.succesful_deal_poloniex
Btce.succesful_deal = Btce.succesful_deal_btce
Kraken.succesful_deal = Kraken.succesful_deal_kraken
Gdax.succesful_deal = Gdax.succesful_deal_gdax

Poloniex.open_orders = Poloniex.open_orders_poloniex
Btce.open_orders = Btce.open_orders_btce
Kraken.open_orders = Kraken.open_orders_kraken
Gdax.open_orders = Gdax.open_orders_gdax

Poloniex.cancel_order = Poloniex.cancel_order_poloniex
Btce.cancel_order = Btce.cancel_order_btce
Kraken.cancel_order = Kraken.cancel_order_kraken
Gdax.cancel_order = Gdax.cancel_order_gdax

# Maker fee on the exchanges
Poloniex.fee = 0.0025
Btce.fee = 0.002
Kraken.fee = 0.0026
Gdax.fee = 0.003

# Modifier to account for rounding balances by exchanges
Poloniex.add = 0.000002
Btce.add = 0
Kraken.add = 0.000002
Gdax.add = 0

exchange_list = [Poloniex, Btce, Gdax, Kraken]

def get_all_hanging_orders():
    for exchange in exchange_list:
        exchange.open_orders()

tuple_list = []

def make_pairs(exchange_list):
    global tuple_list
    i = 0
    b = 0
    # Finding all possible combos of exchanges to arbitrage and saving in a list of tuples
    while i < len(exchange_list)-1:
        while b < len(exchange_list)-1:
            k = [exchange_list[i], exchange_list[b+1]]
            t = [exchange_list[b+1], exchange_list[i]]
            if k in tuple_list or t in tuple_list:
                pass
            else:
                if exchange_list[i] == exchange_list[b+1]:
                    pass
                else:
                    tuple_list.append(k)
                    tuple_list.append(t)
            b += 1
        b = 0
        i += 1
    return tuple_list

tuple_list = make_pairs(exchange_list)
