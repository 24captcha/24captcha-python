from unittest.mock import MagicMock, patch

import pytest

from captcha24 import (
    ApiException,
    Captcha24,
    NetworkException,
    TimeoutException,
    ValidationException,
)


@pytest.fixture
def solver():
    return Captcha24("a" * 32, defaultTimeout=2, pollingInterval=0)


def test_requires_api_key():
    with pytest.raises(ValidationException):
        Captcha24("")


def test_send_requires_sitekey(solver):
    with pytest.raises(ValidationException):
        solver.send(pageurl="https://example.com/")


def test_prepare_proxy(solver):
    params = solver._prepare_params(
        {
            "sitekey": "sk",
            "proxy": {"type": "HTTPS", "uri": "user:pass@1.2.3.4:8080"},
        }
    )
    assert params["proxy"] == "user:pass@1.2.3.4:8080"
    assert params["proxytype"] == "HTTPS"
    assert params["key"] == "a" * 32
    assert params["json"] == 1


def test_invalid_proxy(solver):
    with pytest.raises(ValidationException):
        solver._prepare_params(
            {
                "sitekey": "sk",
                "proxy": "not-a-dict",
            }
        )


@patch.object(Captcha24, "wait_result", return_value="TOKEN")
@patch.object(Captcha24, "send", return_value="task-id")
def test_captcha(mock_send, mock_wait, solver):
    result = solver.captcha(
        sitekey="site-key",
        url="https://example.com/",
        rqdata="rq",
        invisible=True,
    )
    mock_send.assert_called_once()
    kwargs = mock_send.call_args.kwargs
    assert kwargs["sitekey"] == "site-key"
    assert kwargs["pageurl"] == "https://example.com/"
    assert kwargs["rqdata"] == "rq"
    assert kwargs["invisible"] is True
    assert "enterprise" not in kwargs
    assert result == {"captchaId": "task-id", "code": "TOKEN"}


def test_send_json_ok(solver):
    solver.api_client = MagicMock()
    solver.api_client.in_.return_value = {
        "status": 1,
        "request": "uuid-1",
    }
    captcha_id = solver.send(sitekey="sk", pageurl="https://x.com")
    assert captcha_id == "uuid-1"


def test_send_json_error(solver):
    solver.api_client = MagicMock()
    solver.api_client.in_.side_effect = ApiException("ERROR_ZERO_BALANCE")
    with pytest.raises(ApiException):
        solver.send(sitekey="sk")


def test_get_result_not_ready(solver):
    solver.api_client = MagicMock()
    solver.api_client.res.return_value = {
        "status": 0,
        "request": "CAPCHA_NOT_READY",
    }
    with pytest.raises(NetworkException):
        solver.get_result("uuid-1")


def test_get_result_ok(solver):
    solver.api_client = MagicMock()
    solver.api_client.res.return_value = {
        "status": 1,
        "request": "solved-token",
    }
    assert solver.get_result("uuid-1") == "solved-token"


def test_wait_result_timeout(solver):
    solver.api_client = MagicMock()
    solver.api_client.res.return_value = {
        "status": 0,
        "request": "CAPCHA_NOT_READY",
    }
    with pytest.raises(TimeoutException):
        solver.wait_result("uuid-1", timeout=0.2, polling_interval=0.05)


def test_balance(solver):
    solver.api_client = MagicMock()
    solver.api_client.res.return_value = {
        "status": 1,
        "request": "12.34",
    }
    assert solver.balance() == 12.34
    solver.api_client.res.assert_called_once_with(
        key="a" * 32,
        action="getbalance",
        json=1,
    )
