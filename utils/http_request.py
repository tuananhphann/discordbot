import requests
from fake_useragent import FakeUserAgent
from urllib3.util import parse_url
from typing import Any


class HttpRequest:
    """
    Simple HTTP request wrapper class using Requests library.

    Attributes:
        session (requests.Session): A session object for making HTTP requests.
        ua (str): A randomly generated User-Agent string.
        headers (dict): Default HTTP headers for the requests.

    Methods:
        get(url: str, **kwargs) -> requests.Response: Perform an HTTP GET request.
        post(url: str, data: Any = None) -> requests.Response: Perform an HTTP POST request.
    """

    session = requests.Session()
    ua = FakeUserAgent().random
    headers = {"user-agent": ua, "host": ""}

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Perform an HTTP GET request.

        Args:
            url (str): The URL to send the GET request to.
            **kwargs: Additional keyword arguments to pass to the requests.get() function.

        Returns:
            requests.Response: The response object containing the server's response to the request.
        """
        if "headers" in kwargs.keys():
            for k, v in kwargs["headers"].items():
                self.headers[k] = v
            kwargs.pop("headers")
        self.headers["host"] = parse_url(url).hostname
        return self.session.get(url=url, headers=self.headers, **kwargs)

    def post(self, url: str, data: Any = None, **kwargs) -> requests.Response:
        """
        Perform an HTTP POST request.

        Args:
            url (str): The URL to send the POST request to.
            data (Any, optional): The data to include in the POST request body. Defaults to None.

        Returns:
            requests.Response: The response object containing the server's response to the request.
        """
        if "headers" in kwargs.keys():
            for k, v in kwargs["headers"].items():
                self.headers[k] = v
            kwargs.pop("headers")
        self.headers["host"] = parse_url(url).hostname
        return self.session.post(url=url, headers=self.headers, data=data)
