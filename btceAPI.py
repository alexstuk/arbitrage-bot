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
		# Create an object with authentication information.
		self.__api_key = api_key
		self.__api_secret = api_secret
		self.__wait_for_nonce = wait_for_nonce

	def __nonce(self):
		if self.__wait_for_nonce: time.sleep(0.001)
		# Setting nonce using time
		self.__nonce_v = str((time.time() - 1469674815) * 1000).split('.')[0]

	def __signature(self, params):
		# Making signature from api secret and parameters by hashing
		sig = hmac.new(self.__api_secret.encode(), params.encode(), hashlib.sha512)
		return sig.hexdigest()

	def __api_call(self, method, params):
		# Making any API call
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
		# API call to get parameters
		conn = http.client.HTTPSConnection("btc-e.com")
		conn.request("GET", "/api/2/" + couple + "/" + param)
		response = conn.getresponse().read().decode()
		data = json.loads(response)
		conn.close()
		return data

	def getInfo(self):
		# API call to get info
		return self.__api_call('getInfo', {})

	def trans_history(self, tfrom, tcount, tfrom_id, tend_id, torder, tsince, tend):
		# API call to get transaction history
		params = {
			"from": tfrom,
			"count": tcount,
			"from_id": tfrom_id,
			"end_id": tend_id,
			"order": torder,
			"since": tsince,
			"end": tend}
		return self.__api_call('trans_history', params)

	def trade_history(self, tfrom, tcount, tfrom_id, tend_id, torder, tsince, tend, tpair):
		# API call to get trade history
		params = {
			"from": tfrom,
			"count": tcount,
			"from_id": tfrom_id,
			"end_id": tend_id,
			"order": torder,
			"since": tsince,
			"end": tend,
			"pair": tpair}
		return self.__api_call('trade_history', params)

	def active_orders(self, tpair):
		# API call to get active orders
		params = {"pair": tpair}
		return self.__api_call('active_orders', params)

	def trade(self, tpair, ttype, trate, tamount):
		# API call to trade
		params = {
			"pair": tpair,
			"type": ttype,
			"rate": trate,
			"amount": tamount}
		return self.__api_call('trade', params)

	def cancel_order(self, torder_id):
		# API call to cancel order
		params = {"order_id": torder_id}
		return self.__api_call('cancel_order', params)

api_key = ''
api_secret = ''
btce = api(api_key, api_secret, wait_for_nonce=True)
