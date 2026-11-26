# Python Module for 24Captcha API

Python 3 package for easy integration with the [24Captcha](https://24captcha.online/) captcha-solving service.

API docs: https://24captcha.online/api-docs/

## Installation

```bash
pip install 24captcha-python
```

Or from source:

```bash
pip install .
```

Requires **Python 3.8+**.

## Development

```bash
pip install -e ".[dev]"
make fix_lint   # ruff check --fix + format
make lint       # check only
make tests
```

Or without Make:

```bash
ruff check . --fix
ruff format .
pytest -vv
```

## Configuration

```python
from captcha24 import Captcha24

solver = Captcha24("YOUR_API_KEY")
```

Async:

```python
from captcha24 import AsyncCaptcha24

solver = AsyncCaptcha24("YOUR_API_KEY")
```

Options:

```python
solver = Captcha24(
    apiKey="YOUR_API_KEY",
    defaultTimeout=120,  # seconds to wait for a solution
    pollingInterval=5,  # seconds between res.php polls (API recommends 5)
    server="24captcha.online",
)
```

## Solve captcha

Find `data-sitekey` on the target page, then:

```python
result = solver.captcha(
    sitekey="00000000-0000-0000-0000-000000000000",
    url="https://example.com/",
)

token = result["code"]
captcha_id = result["captchaId"]
```

Optional parameters:

| Parameter   | Type | Description |
|------------|------|-------------|
| `sitekey`  | str  | Value of `data-sitekey` (required) |
| `url` / `pageurl` | str | Target page URL |
| `rqdata`   | str  | Extra data from network requests |
| `invisible`| bool | Invisible captcha (default `False`) |
| `proxy`    | dict | `{'type': 'HTTPS', 'uri': 'login:password@IP:PORT'}` |

## Balance

```python
balance = solver.balance()
print(balance)
```

## Manual send / get_result

```python
import time
from captcha24 import NetworkException

captcha_id = solver.send(
    sitekey="00000000-0000-0000-0000-000000000000",
    pageurl="https://example.com/",
)

while True:
    try:
        code = solver.get_result(captcha_id)
        break
    except NetworkException:
        time.sleep(5)
```

## Error handling

```python
from captcha24 import (
    Captcha24,
    ValidationException,
    NetworkException,
    ApiException,
    TimeoutException,
)

try:
    result = solver.captcha(sitekey="...", url="https://example.com/")
except ValidationException as e:
    print("invalid parameters:", e)
except NetworkException as e:
    print("network / not ready:", e)
except ApiException as e:
    print("api error:", e)
except TimeoutException as e:
    print("timeout:", e)
```

## Async

```python
import asyncio
from captcha24 import AsyncCaptcha24


async def main():
    solver = AsyncCaptcha24("YOUR_API_KEY")
    result = await solver.captcha(
        sitekey="00000000-0000-0000-0000-000000000000",
        url="https://example.com/",
    )
    print(result["code"])


asyncio.run(main())
```

## Examples

See the [`examples`](examples/) directory.

## License

MIT
