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
    jsonBuy, jsonSell, loadingBook = [], [], []
    dealDetails = {}
    dealDetailsOld = {}
    cancelDetails = {}

    fee = 0
    startEth = 0
    startBtc = 0

    urldata = ''

    jsonBuy = 0
    jsonSell = 0

    startEth, eth = 0, 0
    startBtc, btc = 0, 0

    ethOld = 0
    btcOld = 0
    adjEth = 0
    adjBtc = 0

    buyPrice = 0
    sellPrice = 0
    buyAmount = 0
    sellAmount = 0

    minProfit = 0

    orderID = 777777


    def __init__(self, exName):
        self.__name = exName
        self.name = exName

    def sell(self):
        pass

    def buy(self):
        pass

    def refreshPricePolo(self):
        urldata = 'https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_ETH&depth=30'
        s = requests.Session()
        try:
            r = s.get(urldata, timeout=5)
            text = r.text
            theJSON = json.loads(text)
            self.buyPrice = float(theJSON['asks'][0][0])
            self.buyAmount = float(theJSON['asks'][0][1])
            self.sellPrice = float(theJSON['bids'][0][0])
            self.sellAmount = float(theJSON['bids'][0][1])
        finally:
            s.close()

    def refreshPriceBtce(self):
        urldata = 'https://btc-e.com/api/3/depth/eth_btc'
        s = requests.Session()
        try:
            r = s.get(urldata, timeout=5)
            text = r.text
            theJSON = json.loads(text)
            self.sellPrice = float(theJSON['eth_btc']['bids'][0][0])
            self.sellAmount = float(theJSON['eth_btc']['bids'][0][1])
            self.buyPrice = float(theJSON['eth_btc']['asks'][0][0])
            self.buyAmount = float(theJSON['eth_btc']['asks'][0][1])
        finally:
            s.close()


    def refreshPriceKraken(self):
        theJSON = krakenAPI.krak.query_public('Depth', {'pair': 'XETHXXBT', 'count': 5})
        self.buyPrice = float(theJSON['result']['XETHXXBT']['asks'][0][0])
        self.buyAmount = float(theJSON['result']['XETHXXBT']['asks'][0][1])
        self.sellPrice = float(theJSON['result']['XETHXXBT']['bids'][0][0])
        self.sellAmount = float(theJSON['result']['XETHXXBT']['bids'][0][1])




    def refreshPriceGdax(self):
        urldata = 'https://api.gdax.com/products/ETH-BTC/book?level=1'
        s = requests.Session()
        try:
            r = s.get(urldata, timeout=5)
            text = r.text
            theJSON = json.loads(text)
            self.sellPrice = float(theJSON['bids'][0][0])
            self.sellAmount = float(theJSON['bids'][0][1])
            self.buyPrice = float(theJSON['asks'][0][0])
            self.buyAmount = float(theJSON['asks'][0][1])
        finally:
            s.close()


    def sellPolo(self, rate, amount):
        return poloniexAPI.polo.sell('BTC_ETH', rate, amount)

    def buyPolo(self, rate, amount):
        return poloniexAPI.polo.buy('BTC_ETH', rate, amount)

    def sellBtce(self, rate, amount):
        p = str(rate)
        rate = float(p[0:7])
        p = str(amount)
        amount = float(p[0:7])
        return btceAPI.btce.Trade('eth_btc', 'sell', rate, amount)

    def buyBtce(self, rate, amount):
        p = str(rate)
        rate = float(p[0:7])
        p = str(amount)
        amount = float(p[0:7])
        return btceAPI.btce.Trade('eth_btc', 'buy', rate, amount)

    def sellKraken(self, rate, amount):
        return krakenAPI.krak.PlaceOrder('XETHXXBT', 'sell', rate, amount)

    def buyKraken(self, rate, amount):
        return krakenAPI.krak.PlaceOrder('XETHXXBT', 'buy', rate, amount)

    def sellGdax(self, rate, amount):
        p = str(rate)
        rate = float(p[0:7])
        p = str(amount)
        amount = float(p[0:8])
        return gdaxAPI.gdax.sell(rate, amount)

    def buyGdax(self, rate, amount):
        p = str(rate)
        rate = float(p[0:7])
        p = str(amount)
        amount = float(p[0:8])
        return gdaxAPI.gdax.buy(rate, amount)

    def refreshBalancesBtce(self):
        balance = btceAPI.btce.getInfo()
        self.eth = round(float(balance['return']['funds']['eth']) - 0.00001, 5)
        self.btc = round(float(balance['return']['funds']['btc']) - 0.00001, 5)

    def refreshBalancesPolo(self):
        balance = poloniexAPI.polo.returnBalances()
        self.eth = round(float(balance['ETH']) - 0.00001, 5)
        self.btc = round(float(balance['BTC']) - 0.00001, 5)

    """
    def addBalancesKraken(self, action):
        if action == 'balance':
            balance = krak.query_private('Balance')
            print(balance)
            print(krak.key)
            print(krak.secret)
            self.eth = float(balance['result']['XETH']) - 0.00001
            self.btc = float(balance['result']['XXBT']) - 0.00001
        if action == 'openOrders':
            pass
            #self.openOrders = krak.query_private('OpenOrders')

    def refreshBalancesKraken(self):
        thread1 = Thread(target=self.addBalancesKraken, args=('balance',))
        thread2 = Thread(target=self.addBalancesKraken, args=('openOrders',))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        dict = self.openOrders

        adjBtc = 0
        adjEth = 0
        dict = dict['result']['open']
        for key in dict:
            if dict[key]['descr']['type'] == 'buy':
                adjBtc = adjBtc + float(dict[key]['vol']) * float(dict[key]['descr']['price'])
            if dict[key]['descr']['type'] == 'sell':
                adjEth = adjEth + float(dict[key]['vol'])

        self.eth = self.eth - adjEth
        self.btc = self.btc - adjBtc

    """
    def refreshBalancesKraken(self):
        balance = krakenAPI.krak.query_private('Balance')
        self.eth = float(balance['result']['XETH']) - 0.00001
        self.btc = float(balance['result']['XXBT']) - 0.00001

        dict = krakenAPI.krak.query_private('OpenOrders')

        adjBtc = 0
        adjEth = 0
        dict = dict['result']['open']
        for key in dict:
            if dict[key]['descr']['type'] == 'buy':
                adjBtc = adjBtc + float(dict[key]['vol']) * float(dict[key]['descr']['price'])
            if dict[key]['descr']['type'] == 'sell':
                adjEth = adjEth + float(dict[key]['vol'])

        self.eth = self.eth - adjEth
        self.btc = self.btc - adjBtc

    def refreshBalancesGdax(self):
        balance = gdaxAPI.gdax.getAccounts()
        for account in balance:
            if account['currency'] == 'BTC':
                self.btc = round(float(account['available']) - 0.00001, 5)
            if account['currency'] == 'ETH':
                self.eth = round(float(account['available']) - 0.00001, 5)

    def succesfulDealBtce(self, dealDetails):
        if 'return' in dealDetails:
            self.orderID = dealDetails['return']['order_id']
            if 'success' in dealDetails:
                if dealDetails['success'] != 0:
                    return True
        return False

    def succesfulDealPoloniex(self, dealDetails):
        if 'orderNumber' in dealDetails:
            self.orderID = dealDetails['orderNumber']
            if 'error' not in dealDetails:
                return True
        return False


    def succesfulDealGdax(self, dealDetails):
        if 'id' in dealDetails:
            self.orderID = dealDetails['id']
            return True
        return False

# {'result': {'descr': {'order': 'buy 0.10000000 ETHXBT @ limit 0.010000'}, 'txid': ['OHBEGS-YHFZZ-O5W2JS']}, 'error': []}

    def succesfulDealKraken(self, dealDetails):
        if 'result' in dealDetails:
            if 'txid' in dealDetails['result']:
                self.orderID = dealDetails['result']['txid'][0]
            if dealDetails['error'] == []:
                return True
        return False

    def completedDealPoloniex(self, dealDetails):
        if 'resultingTrades' in dealDetails:
            if dealDetails['resultingTrades'] == []:
                return False
            else:
                return True

    def completedDealBtce(self, dealDetails):
        if 'return' in dealDetails:
            if 'order_id' in dealDetails['return']:
                if dealDetails['return']['order_id'] == 0:
                    return True
                else:
                    return False


    def completedDealKraken(self, dealDetails):
        return True

    def completedDealGdax(self, dealDetails):
        return True

    def openOrdersPoloniex(self):
        self.hangingOrders = poloniexAPI.polo.returnOpenOrders('BTC_ETH')

    def openOrdersBtce(self):
        self.hangingOrders = btceAPI.btce.ActiveOrders('eth_btc')

    def openOrdersKraken(self):
        self.hangingOrders = krakenAPI.krak.GetOpenOrders()

    def openOrdersGdax(self):
        self.hangingOrders = gdaxAPI.gdax.getOrders()

    def cancelOrderPoloniex(self, orderID):
        self.cancelDetails = poloniexAPI.polo.cancel('BTC_ETH', orderID)

    def cancelOrderBtce(self, orderID):
        self.cancelDetail = btceAPI.btce.CancelOrder(orderID)

    def cancelOrderKraken(self, orderID):
        self.cancelDetail = krakenAPI.krak.CancelOrder(orderID)

    def cancelOrderGdax(self, orderID):
        self.cancelDetail = gdaxAPI.gdax.cancelOrder(orderID)





Poloniex = Exchange('POLONIEX')
Btce = Exchange('BTC-E')
Kraken = Exchange('KRAKEN')
Gdax = Exchange('GDAX')

#Gdax.loadingBook.append({'x':2})
#print(Poloniex.loadingBook)

Poloniex.hangingOrders = []
Btce.hangingOrders = []
Kraken.hangingOrders = []
Gdax.hangingOrders = []

Poloniex.refreshBalances = Poloniex.refreshBalancesPolo
Btce.refreshBalances = Btce.refreshBalancesBtce
Kraken.refreshBalances = Kraken.refreshBalancesKraken
Gdax.refreshBalances = Gdax.refreshBalancesGdax

Poloniex.refreshPrice = Poloniex.refreshPricePolo
Btce.refreshPrice = Btce.refreshPriceBtce
Kraken.refreshPrice = Kraken.refreshPriceKraken
Gdax.refreshPrice = Gdax.refreshPriceGdax

Poloniex.buyFunction = Poloniex.buyPolo
Poloniex.sellFunction = Poloniex.sellPolo
Btce.buyFunction = Btce.buyBtce
Btce.sellFunction = Btce.sellBtce
Kraken.buyFunction = Kraken.buyKraken
Kraken.sellFunction = Kraken.sellKraken
Gdax.buyFunction = Gdax.buyGdax
Gdax.sellFunction = Gdax.sellGdax


Poloniex.completedDeal = Poloniex.completedDealPoloniex
Btce.completedDeal = Btce.completedDealBtce
Kraken.completedDeal = Kraken.completedDealKraken
Gdax.completedDeal = Gdax.completedDealGdax


Poloniex.succesfulDeal = Poloniex.succesfulDealPoloniex
Btce.succesfulDeal = Btce.succesfulDealBtce
Kraken.succesfulDeal = Kraken.succesfulDealKraken
Gdax.succesfulDeal = Gdax.succesfulDealGdax

Poloniex.openOrders = Poloniex.openOrdersPoloniex
Btce.openOrders = Btce.openOrdersBtce
Kraken.openOrders = Kraken.openOrdersKraken
Gdax.openOrders = Gdax.openOrdersGdax

Poloniex.cancelOrder = Poloniex.cancelOrderPoloniex
Btce.cancelOrder = Btce.cancelOrderBtce
Kraken.cancelOrder = Kraken.cancelOrderKraken
Gdax.cancelOrder = Gdax.cancelOrderGdax


Poloniex.fee = 0.0025
Btce.fee = 0.002
Kraken.fee = 0.0026
Gdax.fee = 0.003

Poloniex.power = 0.001
Btce.power = 0
Kraken.power = 0.001
Gdax.power = 0.003


Poloniex.add = 0.000002
Btce.add = 0
Kraken.add = 0.000002
Gdax.add = 0

exchangeList = [Poloniex, Btce, Gdax, Kraken]

def GetAllHangingOrders():
    for exchange in exchangeList:
        exchange.openOrders()
        #print(exchange.name)
        #print(exchange.hangingOrders)



#exchangeList = [Poloniex, Gdax]
tupleList = []

def makePairs(exchangeList):
    global tupleList
    i = 0
    b = 0
    while i < len(exchangeList)-1:
        while b < len(exchangeList)-1:
            k = [exchangeList[i], exchangeList[b+1]]
            t = [exchangeList[b+1], exchangeList[i]]
            if k in tupleList or t in tupleList:
                pass
            else:
                if exchangeList[i] == exchangeList[b+1]:
                    pass
                else:
                    tupleList.append(k)
                    tupleList.append(t)
            b += 1
        b = 0
        i += 1
    return tupleList

tupleList = makePairs(exchangeList)

#GetAllHangingOrders()

#for exchange in exchangeList:
#    for order in exchange.hangingOrders:
#        print(exchange.name)
#        print(str(order))


