"""Auth / API key live checks."""

import pytest

from captcha24 import ApiException, AsyncCaptcha24, Captcha24

INVALID_KEY_UNKNOWN = "0" * 32
INVALID_KEY_FORMAT = "not-a-valid-api-key"


@pytest.mark.live
def test_valid_api_key_accepted(solver):
    """Корректный API key — API принимает запрос (getbalance)."""
    balance = solver.balance()
    assert isinstance(balance, float)


@pytest.mark.live
def test_invalid_api_key_format_raises():
    """Неверный формат ключа — SDK возвращает ApiException."""
    bad = Captcha24(INVALID_KEY_FORMAT, defaultTimeout=5, pollingInterval=1)
    with pytest.raises(ApiException) as exc:
        bad.balance()
    assert "ERROR" in str(exc.value)


@pytest.mark.live
def test_unknown_api_key_raises():
    """Несуществующий ключ (32 символа) — SDK возвращает ApiException."""
    bad = Captcha24(INVALID_KEY_UNKNOWN, defaultTimeout=5, pollingInterval=1)
    with pytest.raises(ApiException) as exc:
        bad.balance()
    assert "ERROR" in str(exc.value)


@pytest.mark.live
@pytest.mark.asyncio
async def test_async_invalid_api_key_raises():
    bad = AsyncCaptcha24(INVALID_KEY_FORMAT, defaultTimeout=5, pollingInterval=1)
    with pytest.raises(ApiException) as exc:
        await bad.balance()
    assert "ERROR" in str(exc.value)
