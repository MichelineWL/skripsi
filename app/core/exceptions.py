class BusinessRuleError(Exception):
    """Raised when a business rule is violated."""


class ResourceNotFoundError(Exception):
    """Raised when a requested resource does not exist."""


class DuplicateResourceError(Exception):
    """Raised when a duplicate resource is detected."""