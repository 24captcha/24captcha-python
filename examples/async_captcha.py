#!/usr/bin/env python3
"""Async example: solve captcha via 24Captcha."""

import asyncio
import os
import sys

from captcha24 import AsyncCaptcha24

API_KEY = os.getenv("CAPTCHA24_API_KEY", "YOUR_API_KEY")


async def main():
    solver = AsyncCaptcha24(API_KEY)

    try:
        result = await solver.captcha(
            sitekey="00000000-0000-0000-0000-000000000000",
            url="https://example.com/",
            # invisible=True,
            # proxy={'type': 'HTTPS', 'uri': 'login:password@IP:PORT'},
        )
    except Exception as e:
        print("error:", e)
        return 1

    print("captchaId:", result["captchaId"])
    print("token:", result["code"])
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
