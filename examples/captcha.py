#!/usr/bin/env python3
"""Example: solve captcha via 24Captcha."""

import os
import sys

from captcha24 import (
    ApiException,
    Captcha24,
    NetworkException,
    TimeoutException,
    ValidationException,
)

API_KEY = os.getenv("CAPTCHA24_API_KEY", "YOUR_API_KEY")


def main():
    solver = Captcha24(
        API_KEY,
        defaultTimeout=120,
        pollingInterval=5,
    )

    try:
        result = solver.captcha(
            sitekey="00000000-0000-0000-0000-000000000000",
            url="https://example.com/",
            # invisible=True,
            # proxy={'type': 'HTTPS', 'uri': 'login:password@IP:PORT'},
        )
    except ValidationException as e:
        print("invalid parameters:", e)
        return 1
    except NetworkException as e:
        print("network error:", e)
        return 1
    except ApiException as e:
        print("api error:", e)
        return 1
    except TimeoutException as e:
        print("timeout:", e)
        return 1

    print("captchaId:", result["captchaId"])
    print("token:", result["code"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
