"""Sync client full cycle, task type, and timeout."""

import pytest

from captcha24 import Captcha24, TimeoutException


@pytest.mark.live
def test_sync_full_cycle(solver, captcha_target):
    """Синхронный клиент — полный цикл успешно работает."""
    result = solver.captcha(
        sitekey=captcha_target["sitekey"],
        url=captcha_target["url"],
    )
    assert result["captchaId"]
    assert isinstance(result["code"], str)
    assert len(result["code"]) > 10


@pytest.mark.live
def test_supported_task_type_captcha(solver, captcha_target, uuid_re):
    """Поддерживаемый тип задачи (#CAPTCHA / captcha) — create + shape of result."""
    result = solver.captcha(
        sitekey=captcha_target["sitekey"],
        url=captcha_target["url"],
    )
    assert uuid_re.match(result["captchaId"])
    assert result["code"]


@pytest.mark.live
def test_timeout_stops_waiting(api_key, captcha_target):
    """Timeout — SDK корректно прекращает ожидание."""
    solver = Captcha24(
        api_key,
        defaultTimeout=1,
        pollingInterval=1,
    )
    captcha_id = solver.send(
        sitekey=captcha_target["sitekey"],
        pageurl=captcha_target["url"],
    )
    with pytest.raises(TimeoutException) as exc:
        solver.wait_result(captcha_id, timeout=0.2, polling_interval=0.1)
    assert "timeout" in str(exc.value).lower()
