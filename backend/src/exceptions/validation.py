from __future__ import annotations


class ValidationError(Exception):
    """
    Base class for all validation-related exceptions.
    """

    pass


class CandidateValidationError(ValidationError):
    """
    Raised when candidate data is invalid.
    """

    pass


class JobDescriptionValidationError(ValidationError):
    """
    Raised when a job description is invalid.
    """

    pass