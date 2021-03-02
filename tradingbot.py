import btceAPI, poloniexAPI
import urllib.request
import json
import time
from time import sleep
from datetime import datetime
import socket
import threading
from threading import Thread
from threading import Thread
import struct
import requests
from classExchange import Btce, Poloniex, Kraken, Gdax, exchange_list, tuple_list
import os

# How to long to wait for request in seconds
timeout = 5
socket.setdefaulttimeout(timeout)

# Takes time to make arbitrage
deal_time = 0
# Total deals were made since initiating the bot
total_deals = 0
# Total profit were made since initiating the bot
total_profit = 0
# List with info on available opportunities
opportunity_list = []

# Refreshing balances on all exchanges
threads = [threading.Thread(target=exchange.refresh_balances, args=()) for
           exchange in exchange_list]

for thread in threads:
    thread.setDaemon(True)
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

# Updating the amount of funds on exchanges
for exchange in exchange_list:
    exchange.start_eth = exchange.eth
    exchange.start_btc = exchange.btc
    
# Saving the amount of funds in a log file
with open('BotLog', 'a') as file_:
    file_.write('\n' + str(datetime.now()) + ' Loading Bot... Checking funds...\n')

for exchange in exchange_list:
    with open('BotLog', 'a') as file_:
        file_.write('Balance on ' + str(exchange.name) + '\nBTC:' + str(exchange.btc) + '\nETH:' + str(
            exchange.eth) + '\n')
        
# Saving the trading pairs in a log file
with open('BotLog', 'a') as file_:
    file_.write('\nPairs \n')

for tuple in tuple_list:
    with open('BotLog', 'a') as file_:
        file_.write(str(tuple[0].name) + ' -- ' + str(tuple[1].name) + '\n')


def loading_book(exchange):
    global Poloniex, Btce
    # Refreshing the price on the exchange
    exchange.refresh_price()


def search_profit():
    global opportunity_list, exchange_list, Poloniex, Btce, Kraken, Gdax, tuple_list, total_deals, deal_time
    
    # Looping through exchanges to get info on the books and possible arbitrage opportunities
    
    thrds = [threading.Thread(target=loading_book, args=(exch,)) for exch in exchange_list]
    for thrd in thrds:
        thrd.setDaemon(True)
    for thrd in thrds:
        thrd.start()
    for thrd in thrds:
        thrd.join()
    
    # Saving buying and selling prices on various exchanges in a file 
    with open('Eth_Btc Bot 0.2', 'a') as file_:
        file_.write(str(Btce.buyBtce) + '\n' + str(Btce.sell_price) + '\n' + str(Poloniex.buy_price) + '\n' + str(Poloniex.sell_price) + '\n')

    i = 0
    opportunity_list = []
    
    # Looping through all trading pairs in search of opportunities 
    while i < len(tuple_list):
        profit = (tuple_list[i][0].sell_price - tuple_list[i][1].buy_price)/tuple_list[i][1].buy_price*100

        # Profit needed to be profitable after paying fees and leaving some extra room
        maker_min_profit = (1/((1 - tuple_list[i][0].fee)*(1 - tuple_list[i][1].fee)) - 1) * 100 + 0.1
        print(tuple_list[i][0].name, '-', tuple_list[i][1].name, ' maker profit: ', round(maker_min_profit, 3), ' profit: ', round(profit, 6))

        if profit > maker_min_profit:
            with open('BotLog', 'a') as file_:
                file_.write(str(datetime.now()) + ' Opportunity on ' + str(tuple_list[i][0].name) + ' amount:' + str(tuple_list[i][0].sell_amount) + ' price:' + str(tuple_list[i][0].sell_price) + '\n' + 'and on ' + str(tuple_list[i][1].name) + ' amount:' + str(tuple_list[i][1].buy_amount) + ' price:' + str(tuple_list[i][1].buy_price) + '\n')
                file_.write('Expected profit: ' + str(round(profit, 3)) + '%\n')

            sell_price = tuple_list[i][0].sell_price + tuple_list[i][0].add
            buy_price = tuple_list[i][1].buy_price - tuple_list[i][1].add

            # Calculating trading amount by finding lowest available balance
            if tuple_list[i][0].sell_amount > tuple_list[i][1].buy_amount:
                amount = tuple_list[i][1].buy_amount
            else:
                amount = tuple_list[i][0].sell_amount
            if amount > tuple_list[i][0].eth:
                amount = tuple_list[i][0].eth
            if amount*buy_price > tuple_list[i][1].btc:
                amount = tuple_list[i][1].btc/buy_price

            # Setting trading amount bigger if balance is higher
            if amount < 10:
                amount = 0.05

            if amount > 10:
                amount = 1

            # checking the difference in crypto between arbitraging exchanges
            oversold = tuple_list[i][0].eth - tuple_list[i][1].eth

            # Counting profit if transaction is complete
            abs_profit = amount * tuple_list[i][0].sell_price * (1 - tuple_list[i][0].fee) * (1 - tuple_list[i][1].fee) - amount * tuple_list[i][1].buy_price

            # Checking if there is enough crypto for trade and writing down the trade
            if amount > 0.1001:
                opportunity_list.append({'selling': tuple_list[i][0], 'buying': tuple_list[i][1], 'amount': amount, 'sell_price': sell_price, 'buy_price': buy_price, 'profit': abs_profit, 'oversold': oversold})
                for exch in exchange_list:
                    with open('BotLog', 'a') as file_:
                        file_.write('Balance on ' + str(exch.name) + '\nBTC:' + str(exch.btc) + '\nETH:' + str(
                            exch.eth) + '\n')

        i += 1

    # Registering info on balances, deals, etc on the screen
    current_time = str(datetime.now())
    print(current_time[:-5], 'extra eth:', round((Poloniex.eth + Btce.eth - Poloniex.start_eth - Btce.start_eth), 2), ' extra btc:',
          round((Poloniex.btc + Btce.btc - Poloniex.start_btc - Btce.start_btc), 5), ' Opportunity List:', opportunity_list,' Total profit: ', round(total_profit, 5), ' Deals:', total_deals)

    if opportunity_list:
        curr_time = time.time()
        time_past = curr_time - deal_time
        # Making a time gap between orders to mitigate risk
        if 5 < time_past < 30:
            # Refreshing balances
            thrds = [threading.Thread(target=exch.refresh_balances, args=()) for exch in exchange_list]

            for thrd in thrds:
                thrd.setDaemon(True)
            for thrd in thrds:
                thrd.start()
            for thrd in thrds:
                thrd.join()


            thrds = [threading.Thread(target=exch.open_orders, args=()) for exch in exchange_list]

            for thrd in thrds:
                thrd.setDaemon(True)
            for thrd in thrds:
                thrd.start()
            for thrd in thrds:
                thrd.join()

            # Adding chosen time gap
            deal_time = deal_time + 630

        return False
    else:
        return True


def buy_sell(exchange, buy_or_sell, price, amount):
    global Poloniex, Btce, Gdax, Kraken
    # Triggering the buy/sell order, saving the info in file
    if buy_or_sell == 'buy':
        exchange.deal_details = exchange.buy_function(price, amount)
        exchange.btc -= price * amount * (1 + exchange.fee)
    if buy_or_sell == 'sell':
        exchange.deal_details = exchange.sell_function(price, amount)
        exchange.eth -= amount * (1 + exchange.fee)

    with open('BotLog', 'a') as file_:
        file_.write(str(datetime.now()) +' Deal: ' + str(buy_or_sell) + ' on ' + str(exchange.name) + ' amount:' + str(amount) + ' price:' + str(price) + ' Details:\n' + str(exchange.deal_details) + '\n')
        file_.write('Hanging orders:\n')
        file_.write(str(exchange.hanging_orders) + '\n')

    print('Purchase/sale complete. Deal details:', str(exchange.deal_details))

def cancel_order(exchange, id):
    global Poloniex, Btce
    # Triggering the cancel order, saving the info in file
    exchange.cancel_detail = exchange.cancel_order(id)
    with open('BotLog', 'a') as file_:
        file_.write(str(datetime.now()) + ' Order number#' + str(
            id) + ' have been canceled. Details:\n' + str(exchange.cancel_detail) + '\n')



def main():
    global Poloniex, Btce, total_deals, total_profit, opportunity_list, deal_time


    print('Loading Bot... Checking funds...')
    for exch in exchange_list:
        print('On ', exch.name, ' ETH:', exch.eth, ' BTC:', exch.btc)
    
    # Running the bot indefinitely with this loop
    while True:
        profit = False
        # Looping through profit search function until the opportunity found 
        while not profit:
            profit = search_profit()
            
        # Saving info on found opportunities in a file
        with open('BotLog', 'a') as file_:
            file_.write(str(datetime.now()) + ' Opportunity list:\n' + str(opportunity_list) + '\n')

        i = 0
        b = 1
        delete_opp = []
        length_opp = len(opportunity_list)

        # Looping through all the opportunities
        while i < length_opp:
            while b < length_opp:
                if i != b:
                    # Comparing similar opportunities
                    if opportunity_list[i]['selling'] == opportunity_list[b]['selling'] \
                            or opportunity_list[i]['selling'] == opportunity_list[b]['buying'] \
                            or opportunity_list[i]['buying'] == opportunity_list[b]['selling'] \
                            or opportunity_list[i]['buying'] == opportunity_list[b]['buying']:
                        # Looking for most profitable opportunity
                        if 0.67 < opportunity_list[i]['profit'] / opportunity_list[b]['profit'] < 1.5:
                            # Looking for exchange that has more crypto to trade
                            if opportunity_list[i]['oversold'] > opportunity_list[b]['oversold']:
                                if b not in delete_opp:
                                    # Adding worst opportunity to a list
                                    delete_opp.append(b)
                            else:
                                if i not in delete_opp:
                                    delete_opp.append(i)
                        else:
                            if opportunity_list[i]['profit'] / opportunity_list[b]['profit'] > 1.49:
                                if b not in delete_opp:
                                    delete_opp.append(b)
                            else:
                                if i not in delete_opp:
                                    delete_opp.append(i)
                b += 1
            b = 0
            i += 1
        # Sorting the list so the worst opportunities are upfront
        delete_opp.sort(reverse=True)
        i = 0
        # Removing bad opportunities
        while i < len(delete_opp):
            opportunity_list.remove(opportunity_list[int(delete_opp[i])])
            i += 1
        # Saving in a file info only about the best opportunities
        with open('BotLog', 'a') as file_:
            file_.write(str(datetime.now()) + ' Adjusted opportunity list:\n' + str(opportunity_list) + '\n')

        for opp in opportunity_list:
            total_profit += float(opp['profit'])
            
        # Creating a new list with the best opportunities
        i = 0
        b = 0
        adj_opp_list = []
        while i < len(opportunity_list):
            adj_opp_list.append({'exchange': None, 'operation': '', 'price': 0, 'amount': 0})
            adj_opp_list[b]['exchange'] = opportunity_list[i]['selling']
            adj_opp_list[b]['operation'] = 'sell'
            adj_opp_list[b]['price'] = opportunity_list[i]['sell_price']
            adj_opp_list[b]['amount'] = opportunity_list[i]['amount']
            adj_opp_list.append({'exchange': None, 'operation': '', 'price': 0, 'amount': 0})
            adj_opp_list[b+1]['exchange'] = opportunity_list[i]['buying']
            adj_opp_list[b+1]['operation'] = 'buy'
            adj_opp_list[b+1]['price'] = opportunity_list[i]['buy_price']
            adj_opp_list[b+1]['amount'] = opportunity_list[i]['amount']
            b += 2
            i += 1

        with open('BotLog', 'a') as file_:
            file_.write(str(datetime.now()) + ' Adjusted opportunity list*:\n' + str(adj_opp_list) + '\n')

        for exchange in exchange_list:
            exchange.deal_details_old = exchange.deal_details

        # Triggering the selling/buying
        threads = [threading.Thread(target=buy_sell, args=(opp['exchange'], opp['operation'], opp['price'], opp['amount'], )) for opp in adj_opp_list]
        for thread in threads:
            thread.setDaemon(True)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()


        cancel_list = []

        # Removing opportunities that didn't go through
        for opportunity in opportunity_list:
            if not opportunity['selling'].succesful_deal(opportunity['selling'].deal_details) or not opportunity['buying'].succesful_deal(opportunity['buying'].deal_details):
                cancel_list.append(opportunity)
                with open('BotLog', 'a') as file_:
                    file_.write(str(datetime.now()) + ' Reason for canceling: One of the orders had an error in deal_details.\n')
            else:
                if not opportunity['selling'].completed_deal(opportunity['selling'].deal_details) and not opportunity['buying'].completed_deal(opportunity['buying'].deal_details):
                    cancel_list.append(opportunity)
                    with open('BotLog', 'a') as file_:
                        file_.write(str(datetime.now()) + ' Reason for canceling: Both orders did not get filled.\n')
                else:
                    if opportunity['selling'].deal_details == opportunity['selling'].deal_details_old or opportunity['buying'].deal_details == opportunity['buying'].deal_details_old:
                        cancel_list.append(opportunity)
                        with open('BotLog', 'a') as file_:
                            file_.write(str(datetime.now()) + ' Reason for canceling: One of the orders did not get triggered \n')

        # Creating and saving the list of opportunities that were not triggered
        adj_cancel_list = []

        i = 0
        b = 0
        while i < len(cancel_list):
            adj_cancel_list.append({'exchange': None, 'order_id': 0})
            adj_cancel_list[b]['exchange'] = cancel_list[i]['selling']
            adj_cancel_list[b]['order_id'] = cancel_list[i]['selling'].order_id
            adj_cancel_list.append({'exchange': None, 'order_id': 0})
            adj_cancel_list[b + 1]['exchange'] = cancel_list[i]['buying']
            adj_cancel_list[b + 1]['order_id'] = cancel_list[i]['buying'].order_id
            b += 2
            i += 1
        i = 0
        b = 0

        with open('BotLog', 'a') as file_:
            file_.write(str(datetime.now()) + ' Cancel list:\n' + str(cancel_list) + '\n')

        with open('BotLog', 'a') as file_:
            file_.write(str(datetime.now()) + ' Cancel list*:\n' + str(adj_cancel_list) + '\n')

        # Cancelling the hanging orders
        threads = [threading.Thread(target=cancel_order, args=(cancel_opp['exchange'], cancel_opp['order_id'], )) for cancel_opp in adj_cancel_list]
        for thread in threads:
            thread.setDaemon(True)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        deal_time = time.time()
        total_deals += 1


while True:
    try:
        main()

    # Catching all possible exceptions, errors with connection and restarting the bot
    except Exception as e:
        print(e)
        # Logging all the errors
        with open('BotLog', 'a') as file_:
            file_.write(str(datetime.now()) + ' Exception occurred:' + str(e) + '\n')
        print('.........Restarting.........')

