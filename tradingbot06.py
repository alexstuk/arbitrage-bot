import datetime
import pickle
import requests
import json
import matplotlib.pyplot as plt
import time
import numpy as np
import datetime as dt
import poloniexAPI
import socket
import os
from datetime import datetime

check = False

coin1 = 'BTC'
coin2 = 'SDC'

upperBound = 50.5
lowerBound = 49.5
average = 800



coin1amount = 0
coin2amount = 0

tradedAmount = 30
addedDecimal = 0.005

deals = 0
totalProfit = 0
lastBoughtFor = 0
buyPrice = 0
sellPrice = 0
totalBuyPrice = 0
totalSellPrice = 0

stance = 'none'

allHistoryList = []
rateList = []
dateList = []
amountList = []
tradeIdList = []
# for check:

tradeHistoryList = []


timeout = 50
socket.setdefaulttimeout(timeout)


dateconv = np.vectorize(dt.datetime.fromtimestamp)


def refreshBalancePolo():
    global coin1amount, coin2amount
    balance = poloniexAPI.polo.returnBalances()
    if coin1 in balance:
        coin1amount = round(float(balance[coin1]) - 0.00001, 5)
        coin2amount = round(float(balance[coin2]) - 0.00001, 5)


def refreshPricePolo():
    global buyAccum, sellAccum, buyPrice, sellPrice
    urldata = 'https://poloniex.com/public?command=returnOrderBook&currencyPair=' + coin1+ '_' + coin2 + '&depth=100'
    s = requests.Session()
    try:
        r = s.get(urldata, timeout=50)
        text = r.text
        theJSON = json.loads(text)
        buyPrice = float(theJSON['asks'][0][0])
        #buyAmount = float(theJSON['asks'][0][1])
        sellPrice = float(theJSON['bids'][0][0])
        #sellAmount = float(theJSON['bids'][0][1])

        bids = theJSON['bids']
        i = 0
        sellAccum = 0
        while float(bids[i][0]) > sellPrice * (1 - addedDecimal):
            sellAccum += float(bids[i][1])
            i += 1

        sellAccum /= 1.5
        sellPrice *= (1 - addedDecimal)

        asks = theJSON['asks']
        i = 0
        buyAccum = 0
        while float(asks[i][0]) < buyPrice * (1 + addedDecimal):
            buyAccum += float(asks[i][1])
            i += 1

        buyAccum /= 1.5
        buyPrice *= (1 + addedDecimal)

    finally:
        s.close()

def updateHistory():
    global totalTrades, allHistoryList

    months = 0.5
    back = 0

    lastLoadDate = time.time() + 7 * 60 * 60 - back * 30 * 24 * 3600
    allTime = months * 30 * 24 * 3600
    oneLoad = 21600
    loads = 0
    startDate = lastLoadDate - allTime
    endDate = startDate + oneLoad

    totalTrades = 1

    while lastLoadDate > endDate:
        print('Loads left: ', allTime/oneLoad - loads - 1)
        loads += 1
        urldata = 'https://poloniex.com/public?command=returnTradeHistory&currencyPair=' + coin1 + '_' + coin2 + '&start=' + str(startDate) + '&end=' + str(endDate)

        s = requests.Session()
        try:
            r = s.get(urldata, timeout=50)
            text = r.text
            tradeHistoryList = json.loads(text)

        finally:
            s.close()

        tradeHistoryList = list(reversed(tradeHistoryList))

        for trade in tradeHistoryList:
            rate = float(trade['rate'])
            date = trade['date']
            amount = float(trade['amount'])
            tradeID = trade['tradeID']

            zipTrade = {'rate': rate, 'date': date, 'amount': amount, 'tradeID': tradeID}

            allHistoryList.append(zipTrade)

        startDate += oneLoad
        endDate += oneLoad
    # print(allHistoryList[0])
    # print(allHistoryList[1])
    # print(allHistoryList[2])
    # print(allHistoryList[3])
    # print(allHistoryList[len(allHistoryList) - 1])


def loadRecentHistory(lastID):
    global dateList, allHistoryList, tradeHistoryList
    tradesList = []
    newHistoryList = []
    rateList = []

    lastDate = time.time() + 60
    firstDate = lastDate - 0.2 * 60 * 60

    urldata = 'https://poloniex.com/public?command=returnTradeHistory&currencyPair=' + coin1 + '_' + coin2 + '&start=' + str(
        firstDate) + '&end=' + str(lastDate)

    s = requests.Session()
    try:
        r = s.get(urldata, timeout=50)
        text = r.text
        tradeHistoryList = json.loads(text)
    finally:
        s.close()
    tradeHistoryList = list(reversed(tradeHistoryList))


    for trade in tradeHistoryList:
        if trade['tradeID'] == lastID or trade['tradeID'] > lastID:
            rate = float(trade['rate'])
            date = trade['date']
            amount = float(trade['amount'])
            tradeID = trade['tradeID']

            zipTrade = {'rate': rate, 'date': date, 'amount': amount, 'tradeID': tradeID}
            newHistoryList.append(zipTrade)
            if allHistoryList[-1]['tradeID'] < tradeID:
                allHistoryList.append(zipTrade)
    return newHistoryList


def loadHistory():
    global dateList
    rateList = []
    dateList = []
    firstDate = time.time() - 16 * 60 * 60
    lastDate = time.time() + 0.2 * 60 * 60

    urldata = 'https://poloniex.com/public?command=returnTradeHistory&currencyPair=' + coin1 + '_' + coin2 + '&start=' + str(
        firstDate) + '&end=' + str(lastDate)

    s = requests.Session()
    try:
        r = s.get(urldata, timeout=50)
        text = r.text
        tradeHistoryList = json.loads(text)
    finally:
        s.close()
    tradeHistoryList = list(reversed(tradeHistoryList))

    for trade in tradeHistoryList:
        rateList.append(float(trade['rate']))
        dateList.append(trade['date'])
    return rateList

def findUpAndDown(prices, n=average):

    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n
        if i == len(prices):
            lastUp = up
            lastDown = down

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return up, down, rsi[len(rsi) - 1]


def lastRsi(prices, up, down, n=average):
    global upDownRSI

    deltas = np.diff(prices)
    rs = up / down

    rsi = np.zeros_like(prices)
    rsi[0] = 100. - 100. / (1. + rs)

    for i in range(1, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (n - 1) + upval) / n
        down = (down * (n - 1) + downval) / n
        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)
        if i == len(prices) - 1:
            upDownRSI[0] = up
            upDownRSI[1] = down
            upDownRSI[2] = rsi[len(rsi) - 1]


def rsiFunc(prices, n=14):

    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi


def checkStance():
    global priceList, stance
    priceList = loadHistory()
    #if coin1amount > tradedAmount * priceList[len(priceList) - 1] and coin2amount > tradedAmount:
    if coin1amount > coin2amount * priceList[len(priceList) - 1]:
        stance = 'none'
    elif coin1amount < coin2amount * priceList[len(priceList) - 1]:
        stance = 'holding'
    else:
        stance = 'empty'
        with open(os.path.join(r'C:\Users\Loki-2\PycharmProjects\text game\botLog tradingbot06', fileName),
                  'a') as file_:
            file_.write(str(datetime.now()) + ' missed opportunity, no funds left\n')


def backtestingRSI():
    global priceList, stance, totalBuyPrice, totalSellPrice, tradedAmount, lastBoughtFor, totalProfitTimeList, totalProfit, deals
    global upperBound, lowerBound, average, lastID, check

    lastID = allHistoryList[-1]['tradeID']
    recentHistoryList = loadRecentHistory(lastID)

    recentPriceList = []
    for trade in recentHistoryList:
        recentPriceList.append(trade['rate'])

    if len(recentPriceList) > 1:
        lastRsi(recentPriceList, upDownRSI[0], upDownRSI[1], n=average)
    refreshBalancePolo()
    refreshPricePolo()

    #priceList = loadHistory()
    #rsiList = rsiFunc(priceList, n=average)

    lastPrice = allHistoryList[-1]['rate']
    lastDate = allHistoryList[-1]['date']

    checkrateList  = []
    for trade in allHistoryList:
        checkrateList.append(trade['rate'])

    rsicheck = rsiFunc(checkrateList, n=average)

    print('rsi check: ', rsicheck[-1])
    print('price ', lastPrice)
    RSI = upDownRSI[2]
    print('rsi ', RSI)

    timetime = time.mktime(dt.datetime.strptime(lastDate, "%Y-%m-%d %H:%M:%S").timetuple())
    if rsicheck[-1] != RSI and check == False:
        with open(os.path.join(r'C:\Users\Loki-2\PycharmProjects\text game\botLog tradingbot06', fileName),
                  'a') as file_:
            file_.write(str(datetime.now()) + ' diffrent rsis' + '\n')
            file_.write('RSI: ' + str(RSI)+ '\n')
            file_.write('RSI check: ' + str(rsicheck[-1])+ '\n')
            file_.write('last date: ' + str(timetime)+ '\n')
            file_.write('all history list: ' + str(allHistoryList)+ '\n')
            file_.write('recent historyList' + str(recentHistoryList)+ '\n')
            file_.write('last ID: ' + str(lastID) + '\n')
            file_.write('up: ' + str(upDownRSI[0]) + '\n')
            file_.write('down: ' + str(upDownRSI[1]) + '\n')
            file_.write('tradeHistoryList: ' + str(tradeHistoryList))
        check = True
    print('date ', timetime)
    print('Position: ', stance)
    print('Deals: ', deals)
    print('Check: ', check)
    print('Profit: ', round(totalProfit, 5))
    RSI = rsicheck[-1]
    if stance == 'none':
        if RSI < lowerBound and buyAccum > tradedAmount and coin1amount/buyPrice > tradedAmount:
            stance = 'holding'
            deals += 1
            lastBoughtFor = buyPrice
            #if tradedAmount > buyAccum:
            #    tradedAmount = buyAccum
            #if coin1amount/buyPrice < tradedAmount:
            #    tradedAmount = coin1amount/buyPrice - 0.00001

            dealDetails = poloniexAPI.polo.buy(coin1 + '_' + coin2, lastBoughtFor, tradedAmount)

            totalBuyPrice += lastBoughtFor * tradedAmount
            fees = (totalBuyPrice + totalSellPrice) * 0.0025
            totalProfit = totalSellPrice - totalBuyPrice - fees

            with open(os.path.join(r'C:\Users\Loki-2\PycharmProjects\text game\botLog tradingbot06', fileName), 'a') as file_:
                file_.write(str(datetime.now()) + ' Buying ' + str(coin2) + ' @ ' + str(lastBoughtFor) + '\n')
                file_.write(str(dealDetails) + '\n')
                file_.write('Total profit: ' + str(totalProfit) + '\n')
                file_.write('Total deals: ' + str(deals) + '\n')
                file_.write('Date: ' + str(dateList[len(dateList) - 1]) + '\n')
                file_.write('Amount: ' + str(tradedAmount) + '\n')


            print('Buying ', coin2, ' @ ', lastBoughtFor)
            print(dealDetails)
            print('Total profit: ', totalProfit)
            print('Searching for apportunity... Total Deals: ', deals )

    if stance == 'holding' and sellAccum > tradedAmount and coin2amount > tradedAmount:
        if RSI > upperBound:
            stance = 'none'
            deals += 1
            lastSoldFor = sellPrice
            #if tradedAmount > sellAccum:
            #    tradedAmount = sellAccum
            #if coin2amount < tradedAmount:
            #    tradedAmount = coin2amount


            dealDetails = poloniexAPI.polo.sell(coin1 + '_' + coin2, lastSoldFor, tradedAmount)


            totalSellPrice += tradedAmount * lastSoldFor
            fees = (totalSellPrice + totalBuyPrice) * 0.0025
            totalProfit = totalSellPrice - totalBuyPrice - fees

            print('Selling', coin2, '@ ', lastSoldFor)
            print(dealDetails)

            with open(os.path.join(r'C:\Users\Loki-2\PycharmProjects\text game\botLog tradingbot06', fileName), 'a') as file_:
                file_.write(str(datetime.now()) + ' Selling ' + str(coin2) + ' @ ' + str(lastSoldFor) + '\n')
                file_.write(str(dealDetails) + '\n')
                file_.write('Total profit: ' + str(totalProfit) + '\n')
                file_.write('Total deals: ' + str(deals) + '\n')
                file_.write('Date: ' + str(dateList[len(dateList) - 1]))
                file_.write('Amount: ' + str(tradedAmount) + '\n')


            print('Fee for this was ', fees)
            totalProfit += (lastSoldFor - lastBoughtFor - fees)
            print('Total profit: ', totalProfit)
            print('Searching for apportunity... Total Deals: ', deals )



    #print('Total profit of: ', totalProfit)
    #print('Procent profit: ', round(totalProfit / startupCapital, 3) * 100, '%')
    #print('Original capital: ', startupCapital)


updateHistory()
for trade in allHistoryList:
    rateList.append(trade['rate'])
    dateList.append(trade['date'])
    amountList.append(trade['amount'])
    tradeIdList.append(trade['tradeID'])


upDownRSI = list(findUpAndDown(rateList))





print('Searching for apportunity... Total Deals: ', deals)

startDate = str(datetime.now())[:-10]
fileName = 'Log ' + datetime.now().strftime('%b-%d-%I%M%p')

refreshBalancePolo()
print('Balance:')
print(coin1, ': ', str(coin1amount))
print(coin2, ': ', str(coin2amount))

with open(os.path.join(r'C:\Users\Loki-2\PycharmProjects\text game\botLog tradingbot06', fileName),
          'a') as file_:

    file_.write('Bot loaded at: ' + str(startDate) + '\n')
    file_.write('Balance:\n')
    file_.write(coin1 + ': ' + str(coin1amount) + '\n')
    file_.write(coin2 + ': ' + str(coin2amount) + '\n')
if not stance:
    checkStance()

#while True:
#     backtestingRSI()
#backtestingRSI()
import sys
while True:
    try:
        backtestingRSI()
    except:
        e = sys.exc_info()[0]

     #except Exception as e:
     #   print(e)
        with open(os.path.join(r'C:\Users\Loki-2\PycharmProjects\text game\botLog tradingbot06', fileName),
          'a') as file_:
            file_.write(str(datetime.now()) + ' Exception occurred:' + str(e) + '\n')
        print('.........Restarting.........')
