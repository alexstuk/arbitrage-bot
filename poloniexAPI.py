import urllib, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import json
import time
import hmac, hashlib


def create_time_stamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))


class poloniex:
    def __init__(self, APIKey, Secret):
        # Create an object with authentication information.
        self.APIKey = APIKey
        self.Secret = Secret

    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if ('return' in after):
            if (isinstance(after['return'], list)):
                for x in range(0, len(after['return'])):
                    if (isinstance(after['return'][x], dict)):
                        if ('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(create_time_stamp(after['return'][x]['datetime']))

        return after

    def api_query(self, command, req={}):
        # Processing various API calls

        if (command == "return_ticker" or command == "return24Volume"):
            ret = urllib.request.urlopen(urllib.request.Request('https://poloniex.com/public?command=' + command))
            return json.loads(ret.read())
        elif (command == "return_order_book"):
            ret = urllib.request.urlopen(urllib.request.Request(
                'http://poloniex.com/public?command=' + command + '&currency_pair=' + str(req['currency_pair'])))
            return json.loads(ret.read())
        elif (command == "return_market_trade_history"):
            ret = urllib.request.urlopen(urllib.request.Request(
                'http://poloniex.com/public?command=' + "return_trade_history" + '&currency_pair=' + str(
                    req['currency_pair'])))
            return json.loads(ret.read())
        else:
            req['command'] = command
            req['nonce'] = int(time.time() * 1000)
            post_data = urllib.parse.urlencode(req).encode('utf8')

            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                b'Sign': sign,
                b'Key': self.APIKey
            }

            ret = urllib.request.urlopen(urllib.request.Request('https://poloniex.com/tradingApi', post_data, headers))
            xxx = ret.read()
            text = xxx.decode('utf-8')
            jsonRet = json.loads(text)
            return self.post_process(jsonRet)

    def return_ticker(self):
        # API call to get ticker
        return self.api_query("return_ticker")

    def return24Volume(self):
        # API call to get 24h volume
        return self.api_query("return24Volume")

    def return_order_book(self, currency_pair):
        # API call to get order book
        return self.api_query("return_order_book", {'currency_pair': currency_pair})

    def return_market_trade_history(self, currency_pair):
        # API call to get trade history
        return self.api_query("return_market_trade_history", {'currency_pair': currency_pair})

    # Returns all of your balances.
    # Outputs:
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def return_balances(self):
        # API call to get balances
        return self.api_query('return_balances')

    # Returns your open orders for a given market, specified by the "currency_pair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currency_pair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # order_number   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def return_open_orders(self, currency_pair):
        return self.api_query('return_open_orders', {"currency_pair": currency_pair})

    # Returns your trade history for a given market, specified by the "currency_pair" POST parameter
    # Inputs:
    # currency_pair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def return_trade_history(self, currency_pair):
        return self.api_query('return_trade_history', {"currency_pair": currency_pair})

    # Places a buy order in a given market. Required POST parameters are "currency_pair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currency_pair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs:
    # order_number   The order number
    def buy(self, currency_pair, rate, amount):
        return self.api_query('buy', {"currency_pair": currency_pair, "rate": rate, "amount": amount})

    # Places a sell order in a given market. Required POST parameters are "currency_pair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currency_pair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs:
    # order_number   The order number
    def sell(self, currency_pair, rate, amount):
        return self.api_query('sell', {"currency_pair": currency_pair, "rate": rate, "amount": amount})

    # Cancels an order you have placed in a given market. Required POST parameters are "currency_pair" and "order_number".
    # Inputs:
    # currency_pair  The curreny pair
    # order_number   The order number to cancel
    # Outputs:
    # succes        1 or 0
    def cancel(self, currency_pair, order_number):
        return self.api_query('cancelOrder', {"currency_pair": currency_pair, "order_number": order_number})

    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."}
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs:
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw', {"currency": currency, "amount": amount, "address": address})

APIKey1 = ''
Secret1 = b''

polo = poloniex(APIKey1.encode(), Secret1)
