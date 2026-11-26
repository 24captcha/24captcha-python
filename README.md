# Python Module for 24Captcha API (captcha solver)

Python package for easy integration with the [24Captcha](https://24captcha.online/) captcha-solving service.
Examples of API requests available on the [API captcha solver page](https://24captcha.online/api-docs/).

- [Python Module for 24Captcha API (captcha solver)](#python-module-for-24captcha-api-captcha-solver)
  - [Installation](#installation)
  - [Development](#development)
  - [Configuration](#configuration)
    - [Captcha24 instance options](#captcha24-instance-options)
  - [Solve captcha](#solve-captcha)
  - [Balance](#balance)
  - [Manual send / get\_result](#manual-send--get_result)
  - [Error handling](#error-handling)
  - [Async](#async)
  - [Examples](#examples)
  - [License](#license)
    - [Graphics and Trademarks](#graphics-and-trademarks)

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

Also, there are a few options that can be configured:

```python
config = {
    "server": "24captcha.online",
    "apiKey": "YOUR_API_KEY",
    "defaultTimeout": 120,
    "pollingInterval": 5,
}
solver = Captcha24(**config)
```

### Captcha24 instance options

| Option | Default value | Description |
| ------ | ------------- | ----------- |
| `server` | `24captcha.online` | API server host |
| `apiKey` | — | Your client API key from the [dashboard](https://24captcha.online/dashboard/) |
| `defaultTimeout` | `120` | Polling timeout in seconds. How long the module waits for an answer from `res.php` |
| `pollingInterval` | `5` | Interval in seconds between requests to `res.php`. Values below 5 are not recommended |

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

Examples of solving are located in the [`examples`](examples/) directory.

## License

The code in this repository is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

### Graphics and Trademarks

The graphics and trademarks included in this repository are not covered by the MIT License. Please contact <a href="mailto:info@24captcha.online">info</a> for permissions regarding the use of these materials.
