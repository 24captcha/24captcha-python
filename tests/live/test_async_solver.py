"""Async client full cycle and timeout."""

import pytest

from captcha24 import AsyncCaptcha24, TimeoutException


@pytest.mark.live
@pytest.mark.asyncio
async def test_async_full_cycle(async_solver, captcha_target):
    """Асинхронный клиент — полный цикл успешно работает."""
    result = await async_solver.captcha(
        sitekey=captcha_target["sitekey"],
        url=captcha_target["url"],
    )
    assert result["captchaId"]
    assert isinstance(result["code"], str)
    assert len(result["code"]) > 10


@pytest.mark.live
@pytest.mark.asyncio
async def test_async_create_and_poll_not_ready(async_solver, captcha_target, uuid_re):
    from captcha24 import NetworkException

    captcha_id = await async_solver.send(
        sitekey=captcha_target["sitekey"],
        pageurl=captcha_target["url"],
    )
    assert uuid_re.match(captcha_id)
    with pytest.raises(NetworkException) as exc:
        await async_solver.get_result(captcha_id)
    assert "CAPCHA_NOT_READY" in str(exc.value)


@pytest.mark.live
@pytest.mark.asyncio
async def test_async_timeout_stops_waiting(api_key, captcha_target):
    """Timeout — async SDK корректно прекращает ожидание."""
    solver = AsyncCaptcha24(api_key, defaultTimeout=1, pollingInterval=1)
    captcha_id = await solver.send(
        sitekey=captcha_target["sitekey"],
        pageurl=captcha_target["url"],
    )
    with pytest.raises(TimeoutException) as exc:
        await solver.wait_result(captcha_id, timeout=0.2, polling_interval=0.1)
    assert "timeout" in str(exc.value).lower()
