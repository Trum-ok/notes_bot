class NotionAPIError(Exception):
    pass


class NotionAuthError(NotionAPIError):
    """401/403"""


class NotionRateLimitError(NotionAPIError):
    """429"""


class NotionServerError(NotionAPIError):
    """5xx"""


class NotionRequestError(NotionAPIError):
    """Сеть/таймаут"""
