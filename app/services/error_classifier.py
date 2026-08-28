from celery.exceptions import SoftTimeLimitExceeded

from app.models.error_codes import TaskErrorCode


def classify_error(exc: Exception) -> TaskErrorCode:
    """
    Convert internal Python exceptions into
    application-level error codes.
    """

    if isinstance(exc, FileNotFoundError):
        return TaskErrorCode.DOCUMENT_NOT_FOUND

    if isinstance(exc, ValueError):
        return TaskErrorCode.INVALID_DOCUMENT

    if isinstance(exc, SoftTimeLimitExceeded):
        return TaskErrorCode.PROCESSING_TIMEOUT

    if isinstance(exc, (ConnectionError, TimeoutError)):
        return TaskErrorCode.TRANSIENT_ERROR

    return TaskErrorCode.NLP_PROCESSING_ERROR