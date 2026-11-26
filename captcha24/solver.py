import time

from .api import ApiClient
from .exceptions import (
    ApiException,
    NetworkException,
    TimeoutException,
    ValidationException,
)


class Captcha24:
    """
    Client for the 24Captcha API.

    Docs: https://24captcha.online/api-docs/
    """

    def __init__(
        self,
        apiKey,
        defaultTimeout=120,
        pollingInterval=5,
        server="24captcha.online",
    ):
        if not apiKey:
            raise ValidationException("apiKey is required")

        self.API_KEY = apiKey
        self.default_timeout = defaultTimeout
        self.polling_interval = pollingInterval
        self.api_client = ApiClient(server=server)

    def captcha(
        self,
        sitekey,
        url=None,
        pageurl=None,
        rqdata=None,
        invisible=False,
        proxy=None,
        **kwargs,
    ):
        """
        Solve a captcha and return a token.

        Parameters
        ----------
        sitekey : str
            Value of data-sitekey on the page.
        url / pageurl : str, optional
            Address of the target page. If omitted, the worker may use a fake URL.
        rqdata : str, optional
            Extra data from network requests (often named rqdata).
        invisible : bool, optional
            True for invisible captcha. Default: False.
        proxy : dict, optional
            {'type': 'HTTPS', 'uri': 'login:password@IP:PORT'}
        """
        page = pageurl or url
        params = {
            "sitekey": sitekey,
            "invisible": invisible,
            **kwargs,
        }
        if page:
            params["pageurl"] = page
        if rqdata is not None:
            params["rqdata"] = rqdata
        if proxy is not None:
            params["proxy"] = proxy

        return self.solve(**params)

    def solve(self, timeout=0, polling_interval=0, **kwargs):
        """Send captcha and poll until solved."""
        captcha_id = self.send(**kwargs)
        result = {"captchaId": captcha_id}

        timeout = float(timeout or self.default_timeout)
        sleep = int(polling_interval or self.polling_interval)
        code = self.wait_result(captcha_id, timeout, sleep)
        result["code"] = code
        return result

    def send(self, **kwargs):
        """Submit a captcha task and return its ID."""
        if not kwargs.get("sitekey"):
            raise ValidationException("sitekey is required")

        params = self._prepare_params(kwargs)
        response = self.api_client.in_(**params)

        if isinstance(response, dict):
            if response.get("status") != 1:
                raise ApiException(str(response.get("request") or response))
            return response["request"]

        if isinstance(response, str) and response.startswith("OK|"):
            return response[3:]

        raise ApiException(f"cannot recognize response {response}")

    def get_result(self, captcha_id):
        """Poll once for a captcha answer. Raises NetworkException if not ready."""
        response = self.api_client.res(
            key=self.API_KEY,
            action="get",
            id=captcha_id,
            json=1,
        )

        if isinstance(response, dict):
            if response.get("status") == 1:
                return response["request"]
            request = response.get("request")
            if request == "CAPCHA_NOT_READY":
                raise NetworkException("CAPCHA_NOT_READY")
            raise ApiException(str(request or response))

        if response == "CAPCHA_NOT_READY":
            raise NetworkException("CAPCHA_NOT_READY")

        if isinstance(response, str) and response.startswith("OK|"):
            return response[3:]

        raise ApiException(f"cannot recognize response {response}")

    def wait_result(self, captcha_id, timeout, polling_interval):
        max_wait = time.time() + timeout

        while time.time() < max_wait:
            try:
                return self.get_result(captcha_id)
            except NetworkException:
                time.sleep(polling_interval)

        raise TimeoutException(f"timeout {timeout} exceeded")

    def balance(self):
        """Get account balance."""
        response = self.api_client.res(
            key=self.API_KEY,
            action="getbalance",
            json=1,
        )

        if isinstance(response, dict):
            if response.get("status") != 1:
                raise ApiException(str(response.get("request") or response))
            return float(response["request"])

        return float(response)

    def _prepare_params(self, params):
        params = dict(params)
        params["key"] = self.API_KEY
        params["json"] = 1

        proxy = params.pop("proxy", None)
        if proxy:
            if not isinstance(proxy, dict) or "uri" not in proxy or "type" not in proxy:
                raise ValidationException("proxy must be {'type': 'HTTPS'|'HTTP', 'uri': 'login:password@IP:PORT'}")
            params["proxy"] = proxy["uri"]
            params["proxytype"] = proxy["type"]

        if "invisible" in params:
            params["invisible"] = bool(params["invisible"])

        return params
