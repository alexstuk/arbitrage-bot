# secret: 78a98c203628379112a1613979556ca2b4ca6cfdd79ad0e86509bcf1a5c28883
# key: HQB2602V-PQSCON7D-XO85V1L8-ECK26J40-4CC57L0M
import http.client
import urllib.request, urllib.parse, urllib.error
import json
import hashlib
import hmac
import time

class api:
	__api_key = '';
	__api_secret = '';
	__nonce_v = 1;
	__wait_for_nonce = False

	def __init__(self, api_key, api_secret, wait_for_nonce=False):
		self.__api_key = api_key
		self.__api_secret = api_secret
		self.__wait_for_nonce = wait_for_nonce

	def __nonce(self):
		if self.__wait_for_nonce: time.sleep(0.001)
		self.__nonce_v = str((time.time() - 1469674815) * 1000).split('.')[0]

	def __signature(self, params):
		sig = hmac.new(self.__api_secret.encode(), params.encode(), hashlib.sha512)
		return sig.hexdigest()

	def __api_call(self, method, params):
		self.__nonce()
		params['method'] = method
		params['nonce'] = str(self.__nonce_v)
		params = urllib.parse.urlencode(params)
		headers = {"Content-type": "application/x-www-form-urlencoded",
				   "Key": self.__api_key,
				   "Sign": self.__signature(params)}
		conn = http.client.HTTPSConnection("btc-e.com")
		conn.request("POST", "/tapi", params, headers)
		response = conn.getresponse().read().decode()
		data = json.loads(response)
		conn.close()
		return data

	def get_param(self, couple, param):
		conn = http.client.HTTPSConnection("btc-e.com")
		conn.request("GET", "/api/2/" + couple + "/" + param)
		response = conn.getresponse().read().decode()
		data = json.loads(response)
		conn.close()
		return data

	def getInfo(self):
		return self.__api_call('getInfo', {})

	def TransHistory(self, tfrom, tcount, tfrom_id, tend_id, torder, tsince, tend):
		params = {
			"from": tfrom,
			"count": tcount,
			"from_id": tfrom_id,
			"end_id": tend_id,
			"order": torder,
			"since": tsince,
			"end": tend}
		return self.__api_call('TransHistory', params)

	def TradeHistory(self, tfrom, tcount, tfrom_id, tend_id, torder, tsince, tend, tpair):
		params = {
			"from": tfrom,
			"count": tcount,
			"from_id": tfrom_id,
			"end_id": tend_id,
			"order": torder,
			"since": tsince,
			"end": tend,
			"pair": tpair}
		return self.__api_call('TradeHistory', params)

	def ActiveOrders(self, tpair):
		params = {"pair": tpair}
		return self.__api_call('ActiveOrders', params)

	def Trade(self, tpair, ttype, trate, tamount):
		params = {
			"pair": tpair,
			"type": ttype,
			"rate": trate,
			"amount": tamount}
		return self.__api_call('Trade', params)

	def CancelOrder(self, torder_id):
		params = {"order_id": torder_id}
		return self.__api_call('CancelOrder', params)

api_key = ''
api_secret = ''
btce = api(api_key, api_secret, wait_for_nonce=True)


#print(btce.getInfo())

#dealDetailsB = btce.Trade('zzz_btc', 'buy', 0.000001, 10)
#print(dealDetailsB)
"""
buyPriceB = float(getPrice('btc-e', 'eth_btc', 'buy')) * 1.0009
fundsBtce = float(btce.getInfo()['return']['funds']['btc'])
fundsBtce = fundsBtce / buyPriceB
print(buyPriceB)
print(fundsBtce)
dealDetailsB = btce.Trade('eth_btc', 'buy', round(buyPriceB,5), round(fundsBtce,5))
print(dealDetailsB)
#print(btceApi.getInfo())
#dealDetailsB = btce.Trade('eth_btc', 'buy', 0.01, 0.1 )
#print(dealDetailsB)
#activeorder =  ActiveOrders(self, tpair):

#print(btceApi.getInfo()['return']['funds']['btc'])
"""