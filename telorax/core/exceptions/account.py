from telorax.core.exceptions.base import TeloraxError


class AccountError(TeloraxError):
    """Telegram account domain error."""


class AccountRateLimitedError(AccountError):
    def __init__(self, account_id: int, wait_seconds: int) -> None:
        super().__init__(f'Account {account_id} rate limited for {wait_seconds}s')
        self.account_id = account_id
        self.wait_seconds = wait_seconds


class AccountRestrictedError(AccountError):
    def __init__(self, account_id: int) -> None:
        super().__init__(f'Account {account_id} is restricted')
        self.account_id = account_id


class AccountSessionExpiredError(AccountError):
    def __init__(self, account_id: int) -> None:
        super().__init__(f'Account {account_id} session expired')
        self.account_id = account_id


class InvalidSessionError(AccountError):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class AccountImportError(AccountError):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class AccountNotFoundError(AccountError):
    def __init__(self, account_id: int) -> None:
        super().__init__(f'Account {account_id} not found')
        self.account_id = account_id
