"""Create task, polling, and result retrieval against the real API."""

import pytest

from captcha24 import NetworkException


@pytest.mark.live
def test_create_task_returns_id(solver, captcha_target, uuid_re):
    """Создание задачи — API выдаёт корректный ID."""
    captcha_id = solver.send(
        sitekey=captcha_target["sitekey"],
        pageurl=captcha_target["url"],
    )
    assert isinstance(captcha_id, str)
    assert uuid_re.match(captcha_id), captcha_id


@pytest.mark.live
def test_polling_not_ready(solver, captcha_target):
    """Polling — SDK разбирает промежуточный статус CAPCHA_NOT_READY."""
    captcha_id = solver.send(
        sitekey=captcha_target["sitekey"],
        pageurl=captcha_target["url"],
    )
    with pytest.raises(NetworkException) as exc:
        solver.get_result(captcha_id)
    assert "CAPCHA_NOT_READY" in str(exc.value)


@pytest.mark.live
def test_ready_task_returns_token(solver, captcha_target):
    """Готовая задача — SDK получает результат (полный wait)."""
    captcha_id = solver.send(
        sitekey=captcha_target["sitekey"],
        pageurl=captcha_target["url"],
    )
    token = solver.wait_result(captcha_id, timeout=120, polling_interval=5)
    assert isinstance(token, str)
    assert len(token) > 10
