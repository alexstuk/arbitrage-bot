import http.client
import urllib.request, urllib.parse, urllib.error


class Connection(object):
    """Kraken.com connection handler.
    """

    def __init__(self, uri='api.kraken.com', timeout=5 ):
        """ Create an object for reusable connections.

        :param uri: URI to connect to.
        :type uri: str
        :param timeout: blocking operations' timeout (in seconds).
        :type timeout: int
        :returns: TODO
        :raises: TODO

        """
        self.headers = {
            'User-Agent': 'krakenex/0.0.6 (+https://github.com/veox/python3-krakenex)'
        }
        self.conn = http.client.HTTPSConnection(uri, timeout=timeout)

    def close(self):
        """ Close the connection.
        """
        self.conn.close()

    def _request(self, url, req={}, headers={}):
        """ Send POST request to API server.

        :param url: fully-qualified URL with all necessary urlencoded
            information
        :type url: str
        :param req: additional API request parameters
        :type req: dict
        :param headers: additional HTTPS headers, such as API-Key and API-Sign
        :type headers: dict
        """
        data = urllib.parse.urlencode(req)
        headers.update(self.headers)

        self.conn.request("POST", url, data, headers)
        response = self.conn.getresponse()

        return response.read().decode()
