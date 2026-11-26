import asyncio
import time

from .async_api import AsyncApiClient
from .exceptions import (
    ApiException,
    NetworkException,
    TimeoutException,
    ValidationException,
)


class AsyncCaptcha24:
    """
    Async client for the 24Captcha API.

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
        self.api_client = AsyncApiClient(server=server)

    async def captcha(
        self,
        sitekey,
        url=None,
        pageurl=None,
        rqdata=None,
        invisible=False,
        proxy=None,
        **kwargs,
    ):
        """Solve a captcha and return a token. See Captcha24.captcha for params."""
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

        return await self.solve(**params)

    async def solve(self, timeout=0, polling_interval=0, **kwargs):
        captcha_id = await self.send(**kwargs)
        result = {"captchaId": captcha_id}

        timeout = float(timeout or self.default_timeout)
        sleep = int(polling_interval or self.polling_interval)
        code = await self.wait_result(captcha_id, timeout, sleep)
        result["code"] = code
        return result

    async def send(self, **kwargs):
        if not kwargs.get("sitekey"):
            raise ValidationException("sitekey is required")

        params = self._prepare_params(kwargs)
        response = await self.api_client.in_(**params)

        if isinstance(response, dict):
            if response.get("status") != 1:
                raise ApiException(str(response.get("request") or response))
            return response["request"]

        if isinstance(response, str) and response.startswith("OK|"):
            return response[3:]

        raise ApiException(f"cannot recognize response {response}")

    async def get_result(self, captcha_id):
        response = await self.api_client.res(
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

    async def wait_result(self, captcha_id, timeout, polling_interval):
        max_wait = time.monotonic() + timeout

        while time.monotonic() < max_wait:
            try:
                return await self.get_result(captcha_id)
            except NetworkException:
                await asyncio.sleep(polling_interval)

        raise TimeoutException(f"timeout {timeout} exceeded")

    async def balance(self):
        """Get account balance."""
        response = await self.api_client.res(
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
