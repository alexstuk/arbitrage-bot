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
        self.__api_key = api_key
        self.__api_secret = api_secret
        self.__wait_for_nonce = wait_for_nonce

    def __nonce(self):
        if self.__wait_for_nonce: time.sleep(0.0001)
        self.__nonce_v = str((time.time() - 1469674815)*1000).split('.')[0]

    def __signature(self, params):
        return hmac.new(self.__api_secret, params, digestmod=hashlib.sha512).hexdigest()

    def __api_call(self, method, params):
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
        conn = http.client.HTTPSConnection("bter.com")
        conn.request("GET", "/api/1/" + param + "/" + couple)
        response = conn.getresponse()
        data = json.load(response)
        conn.close()
        return data

    def GetFunds(self):
        return self.__api_call('getfunds', {})

    def Orderlist(self, tpair):
        params = {"pair": tpair}
        return self.__api_call('orderlist', params)

    def PlaceOrder(self, tpair, ttype, trate, tamount):
        params = {
            "pair": tpair,
            "type": ttype,
            "rate": trate,
            "amount": tamount}
        return self.__api_call('placeorder', params)

    def CancelOrder(self, torder_id):
        params = {"order_id": torder_id}
        return self.__api_call('cancelorder', params)

api_key1 = ''
api_secret1 = ''

bter = bterapi(api_key1.encode('utf-8'), api_secret1.encode('utf-8'), wait_for_nonce=True)
#print(bter.GetFunds())

#trade = bter.PlaceOrder('eth_btc', 'BUY', 0.01, 0.1)
#print(trade)
#{'code': 21, 'message': "Error: you don't have enough fund", 'result': False, 'msg': "Error: you don't have enough fund"}
# not fished trade
#{'message': 'Success', 'code': 0, 'msg': 'Success', 'result': True, 'order_id': 131102}
#finished trade
#{"result":"true", "order_id":"123456",	"msg":"Success"}
#???? what sld be a succesful trade
#{'message': 'Success', 'code': 0, 'order_id': 131113, 'result': True, 'msg': 'Success'}
