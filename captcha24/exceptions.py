class SolverExceptions(Exception):
    """Base exception for captcha24 solver errors."""


class ValidationException(SolverExceptions):
    """Invalid parameters passed to the solver."""


class NetworkException(SolverExceptions):
    """Network error or captcha not ready yet."""


class ApiException(SolverExceptions):
    """API returned an error response."""


class TimeoutException(SolverExceptions):
    """Captcha was not solved within the timeout."""
