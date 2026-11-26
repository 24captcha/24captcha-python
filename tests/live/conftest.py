import os
import re
from pathlib import Path

import pytest
from dotenv import load_dotenv

from captcha24 import AsyncCaptcha24, Captcha24

# Load repo-root .env for local live runs (no-op if file missing).
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

API_KEY = os.getenv("CAPTCHA24_API_KEY")
SITEKEY = os.getenv("CAPTCHA24_SITEKEY")
PAGEURL = os.getenv("CAPTCHA24_PAGEURL", "https://example.com/")


@pytest.fixture
def api_key():
    if not API_KEY:
        pytest.skip("set CAPTCHA24_API_KEY (or .env) to run live tests")
    return API_KEY


@pytest.fixture
def solver(api_key):
    return Captcha24(api_key, defaultTimeout=120, pollingInterval=5)


@pytest.fixture
def async_solver(api_key):
    return AsyncCaptcha24(api_key, defaultTimeout=120, pollingInterval=5)


@pytest.fixture
def captcha_target():
    if not SITEKEY:
        pytest.skip("set CAPTCHA24_SITEKEY (and optionally CAPTCHA24_PAGEURL) for task/solve live tests")
    return {"sitekey": SITEKEY, "url": PAGEURL}


@pytest.fixture
def uuid_re():
    return re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
