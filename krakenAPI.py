import json
import urllib.request, urllib.parse, urllib.error

# private query nonce
import time

# private query signing
import hashlib
import hmac
import base64
import krakenConnection
from krakenConnection import Connection


class API(object):
    """Kraken.com cryptocurrency Exchange API.

    """

    def __init__(self, key='', secret='', conn=None):
        """Create an object with authentication information.

        :param key: key required to make queries to the API
        :type key: str
        :param secret: private key used to sign API messages
        :type secret: str
        :param conn: connection TODO
        :type conn: krakenex.Connection

        """
        self.key = key
        self.secret = secret
        self.uri = 'https://api.kraken.com'
        self.apiversion = '0'
        self.conn = conn

    def load_key(self, path):
        """Load key and secret from file.

        :param path: path to keyfile
        :type path: str

        """
        f = open(path, "r")
        self.key = f.readline().strip()
        self.secret = f.readline().strip()

    def set_connection(self, conn):
        """Set an existing connection to be used as a default in queries.
        :param conn: connection TODO
        :type conn: krakenex.Connection
        """
        self.conn = conn

    def _query(self, urlpath, req={}, conn=None, headers={}):
        """Low-level query handling.

        :param urlpath: API URL path sans host
        :type urlpath: str
        :param req: additional API request parameters
        :type req: dict
        :param conn: connection TODO
        :type conn: krakenex.Connection
        :param headers: HTTPS headers
        :type headers: dict

        """
        url = self.uri + urlpath

        if conn is None:
            if self.conn is None:
                conn = Connection()
            else:
                conn = self.conn

        ret = conn._request(url, req, headers)
        return json.loads(ret)

    def query_public(self, method, req={}, conn=None):
        """API queries that do not require a valid key/secret pair.

        :param method: API method name
        :type method: str
        :param req: additional API request parameters
        :type req: dict
        :param conn: connection TODO
        :type conn: krakenex.Connection

        """
        urlpath = '/' + self.apiversion + '/public/' + method

        return self._query(urlpath, req, conn)

    def query_private(self, method, req={}, conn=None):
        """API queries that require a valid key/secret pair.

        :param method: API method name
        :type method: str
        :param req: additional API request parameters
        :type req: dict
        :param conn: connection TODO
        :type conn: krakenex.Connection

        """
        urlpath = '/' + self.apiversion + '/private/' + method

        req['nonce'] = int(1000 * time.time())
        postdata = urllib.parse.urlencode(req)

        # Unicode-objects must be encoded before hashing
        encoded = (str(req['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(base64.b64decode(self.secret),
                             message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())

        headers = {
            'API-Key': self.key,
            'API-Sign': sigdigest.decode()
        }

        return self._query(urlpath, req, conn, headers)

    def PlaceOrder(self, tpair, ttype, trate, tamount):
        params = {
            "pair": tpair,
            'ordertype': 'limit',
            "type": ttype,
            "price": trate,
            "volume": tamount}
        return self.query_private('AddOrder', params)

    def GetFunds(self):
        return self.query_private('Balance')

    def CancelOrder(self, txid):
        params = {"txid": txid}
        return self.query_private('CancelOrder', params)

krak = API()


krak.key = ''
krak.secret = ''
#k = krak.query_public('AssetPairs')

#k = krak.PlaceOrder('XETHXXBT', 'buy', 0.02, 10)
#{'error': [], 'result': {'txid': ['OWZO6T-BJDPD-IRQ4JG'], 'descr': {'order': 'buy 0.10000000 ETHXBT @ limit 0.020000'}}}

#t = krak.PlaceOrder('XETHXXBT', 'sell', 0.03, 0.1)
#k = krak.query_private('OpenOrders')
#dealDetails = {'result': {'descr': {'order': 'buy 0.10000000 ETHXBT @ limit 0.010000'}, 'txid': ['OHBEGS-YHFZZ-O5W2JS']}, 'error': []}

#orderID = dealDetails['result']['txid'][0]
#print(orderID)
#k = krak.CancelOrder('OPB43A-Z5ZSQ-PSUOHA')

#k = krak.query_public('Depth', {'pair': 'XETHXXBT', 'count': 5})
#print(t)
#print(k)
#{'error': ['EOrder:Unknown order:OHBEGS-YHFZZ-O5W2JS']}
#{'error': [], 'result': {'count': 1}}
