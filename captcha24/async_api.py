import httpx

from .exceptions import ApiException, NetworkException


class AsyncApiClient:
    """Async HTTP client for 24captcha.online."""

    def __init__(self, server="24captcha.online"):
        self.server = server

    def _url(self, path):
        return f"https://{self.server}{path}"

    async def in_(self, **kwargs):
        """Create a captcha task via POST /in.php."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(self._url("/in.php"), json=kwargs)
        except httpx.HTTPError as e:
            raise NetworkException(e) from e

        if resp.status_code != 200:
            raise NetworkException(f"bad response: {resp.status_code}")

        return self._parse(resp)

    async def res(self, **kwargs):
        """Get task result via POST /res.php."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(self._url("/res.php"), json=kwargs)
        except httpx.HTTPError as e:
            raise NetworkException(e) from e

        if resp.status_code != 200:
            raise NetworkException(f"bad response: {resp.status_code}")

        return self._parse(resp)

    def _parse(self, resp):
        content_type = resp.headers.get("Content-Type", "")
        text = resp.text

        if "application/json" in content_type or text.lstrip().startswith("{"):
            try:
                data = resp.json()
            except ValueError as e:
                raise ApiException(f"cannot parse json: {text}") from e

            if data.get("status") == 0:
                request = data.get("request") or data.get("error_text") or text
                if request == "CAPCHA_NOT_READY":
                    return data
                raise ApiException(str(request))

            return data

        if "ERROR" in text:
            raise ApiException(text)

        return text
