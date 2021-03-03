import hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from GdaxPublicClient import PublicClient

class AuthenticatedClient(PublicClient):
    def __init__(self, key, b64secret, passphrase, api_url="https://api.gdax.com", product_id="BTC-USD"):
        # Create an object with authentication information.
        self.url = api_url
        self.product_id = product_id
        self.auth = GdaxAuth(key, b64secret, passphrase)

    def get_account(self, account_id):
        # API call to get account info
        r = requests.get(self.url + '/accounts/' + account_id, auth=self.auth)
        return r.json()

    def get_accounts(self):
        return self.get_account('')

    def get_account_history(self, account_id):
        # API call to get account history
        list = []
        r = requests.get(self.url + '/accounts/%s/ledger' %account_id, auth=self.auth)
        list.append(r.json())
        if "cb-after" in r.headers:
            self.history_pagination(account_id, list, r.headers["cb-after"])
        return list

    def history_pagination(self, account_id, list, after):
        #Pagination allows for fetching results before and after the current page of results and is well suited for realtime data
        r = requests.get(self.url + '/accounts/%s/ledger?after=%s' %(account_id, str(after)), auth=self.auth)
        if r.json():
            list.append(r.json())
        if "cb-after" in r.headers:
            self.history_pagination(account_id, list, r.headers["cb-after"])
        return list

    def get_account_holds(self, account_id):
        # API call to get account holds
        list = []
        r = requests.get(self.url + '/accounts/%s/holds' %account_id, auth=self.auth)
        list.append(r.json())
        if "cb-after" in r.headers:
            self.holds_pagination(account_id, list, r.headers["cb-after"])
        return list

    def holds_pagination(self, account_id, list, after):
        r = requests.get(self.url + '/accounts/%s/holds?after=%s' %(account_id, str(after)), auth=self.auth)
        if r.json():
            list.append(r.json())
        if "cb-after" in r.headers:
            self.holds_pagination(account_id, list, r.headers["cb-after"])
        return list

    def buy(self, buy_params):
        # API call to by crypto
        buy_params["side"] = "buy"
        if not buy_params["product_id"]:
            buy_params["product_id"] = self.product_id
        r = requests.post(self.url + '/orders', json=buy_params, auth=self.auth)
        return r.json()

    def sell(self, sellParams):
        # API call to sell crypto
        sellParams["side"] = "sell"
        r = requests.post(self.url + '/orders', json=sellParams, auth=self.auth)
        return r.json()

    def cancel_order(self, order_id):
        # API call to cancel order
        r = requests.delete(self.url + '/orders/' + order_id, auth=self.auth)
        return r.json()

    def get_order(self, order_id):
        # API call to get order information
        r = requests.get(self.url + '/orders/' + order_id, auth=self.auth)
        return r.json()

    def get_orders(self):
        # API call to get all orders
        list = []
        r = requests.get(self.url + '/orders/', auth=self.auth)
        list.append(r.json())
        if 'cb-after' in r.headers:
            self.paginate_orders(list, r.headers['cb-after'])
        return list

    def paginate_orders(self, list, after):
        r = requests.get(self.url + '/orders?after=%s' %str(after))
        if r.json():
            list.append(r.json())
        if 'cb-after' in r.headers:
            self.paginate_orders(list, r.headers['cb-after'])
        return list

    def get_fills(self, order_id='', product_id='', before='', after='', limit=''):
        # API call to get fills
        list = []
        url = self.url + '/fills?'
        if order_id: url += "order_id=%s&" %str(order_id)
        if product_id: url += "product_id=%s&" %(product_id or self.product_id)
        if before: url += "before=%s&" %str(before)
        if after: url += "after=%s&" %str(after)
        if limit: url += "limit=%s&" %str(limit)
        r = requests.get(url, auth=self.auth)
        list.append(r.json())
        if 'cb-after' in r.headers and limit is not len(r.json()):
            return self.paginate_fills(list, r.headers['cb-after'], order_id=order_id, product_id=product_id)
        return list

    def paginate_fills(self, list, after, order_id='', product_id=''):
        url = self.url + '/fills?after=%s&' % str(after)
        if order_id: url += "order_id=%s&" % str(order_id)
        if product_id: url += "product_id=%s&" % (product_id or self.product_id)
        r = requests.get(url, auth=self.auth)
        if r.json():
            list.append(r.json())
        if 'cb-after' in r.headers:
            return self.paginate_fills(list, r.headers['cb-after'], order_id=order_id, product_id=product_id)
        return list

    def deposit(self, amount="", account_id=""):
        # API call to deposit
        payload = {
            "type": "deposit",
            "amount": amount,
            "account_id": account_id
        }
        r = requests.post(self.url + "/transfers", json=payload, auth=self.auth)
        return r.json()

    def withdraw(self, amount="", account_id=""):
        # API call to withdraw
        payload = {
            "type": "withdraw",
            "amount": amount,
            "account_id": account_id
        }
        r = requests.post(self.url + "/transfers", json=payload, auth=self.auth)
        return r.json()

class GdaxAuth(AuthBase):
    # Provided by Coinbase: https://docs.gdax.com/#signing-a-message
    def __init__(self, api_key, secret_key, passphrase):
        # Create an object with authentication information.
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        # Making request
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        message = message.encode('utf-8')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
        })
        return request

path_url = 'https://api.exchange.coinbase.com/'

passphrase = ''
key = ''
secret = ''

k = AuthenticatedClient(key, secret, passphrase)
t = k.get_accounts()
