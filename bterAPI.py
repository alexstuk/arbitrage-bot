import http.client
import urllib.request, urllib.parse, urllib.error
import json
import hashlib
import hmac
import time


class bterapi:
    __api_key = '';
    __api_secret = '';
    __nonce_v = 1;
    __wait_for_nonce = False

    def __init__(self, api_key, api_secret, wait_for_nonce=False):
        # Create an object with authentication information.
        self.__api_key = api_key
        self.__api_secret = api_secret
        self.__wait_for_nonce = wait_for_nonce

    def __nonce(self):
        if self.__wait_for_nonce: time.sleep(0.0001)
        self.__nonce_v = str((time.time() - 1469674815)*1000).split('.')[0]

    def __signature(self, params):
        # Getting signature from api secret and parameters
        return hmac.new(self.__api_secret, params, digestmod=hashlib.sha512).hexdigest()

    def __api_call(self, method, params):
        # Making any API call
        self.__nonce()
        params['nonce'] = str(self.__nonce_v)
        params = urllib.parse.urlencode(params)
        params = params.encode('utf8')
        headers = {b"Content-type": b"application/x-www-form-urlencoded",
                   b"Key": self.__api_key,
                   b"Sign": self.__signature(params)}
        conn = http.client.HTTPSConnection("bter.com")
        conn.request("POST", "https://bter.com/api/1/private/" + method, params, headers)
        response = conn.getresponse()
        raw_data = response.read()
        encoding = response.info().get_content_charset('utf8')  # JSON default
        data = json.loads(raw_data.decode(encoding))
        conn.close()
        return data

    def get_param(self, couple, param):
        # API call to get parameters
        conn = http.client.HTTPSConnection("bter.com")
        conn.request("GET", "/api/1/" + param + "/" + couple)
        response = conn.getresponse()
        data = json.load(response)
        conn.close()
        return data

    def get_funds(self):
        # API call to check funds on the account
        return self.__api_call('get_funds', {})

    def order_list(self, tpair):
        # API call to get order list
        params = {"pair": tpair}
        return self.__api_call('order_list', params)

    def place_order(self, tpair, ttype, trate, tamount):
        # API call to place order
        params = {
            "pair": tpair,
            "type": ttype,
            "rate": trate,
            "amount": tamount}
        return self.__api_call('place_order', params)

    def cancel_order(self, torder_id):
        # API call to cancel order
        params = {"order_id": torder_id}
        return self.__api_call('cancel_order', params)


api_key1 = ''
api_secret1 = ''

bter = bterapi(api_key1.encode('utf-8'), api_secret1.encode('utf-8'), wait_for_nonce=True)
