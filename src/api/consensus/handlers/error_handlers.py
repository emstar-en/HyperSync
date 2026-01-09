"""
Error Handlers for Consensus APIs

Centralized error handling for consensus mechanism APIs.
"""

from typing import Dict, Optional
from enum import Enum

class ErrorType(Enum):
    """Error types for consensus APIs."""
    INVALID_TIER = "invalid_tier"
    INVALID_MECHANISM = "invalid_mechanism"
    PERMISSION_DENIED = "permission_denied"
    VALIDATION_ERROR = "validation_error"
    RESOURCE_ERROR = "resource_error"
    INTERNAL_ERROR = "internal_error"
    MISSING_PARAMETERS = "missing_parameters"

class ConsensusAPIError(Exception):
    """Base exception for consensus API errors."""

    def __init__(self, message: str, error_type: ErrorType, details: Optional[Dict] = None):
        """Initialize error with message, type, and optional details."""
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict:
        """Convert error to dictionary for API response."""
        return {
            "status": "error",
            "error": self.message,
            "error_type": self.error_type.value,
            "details": self.details
        }

class InvalidTierError(ConsensusAPIError):
    """Raised when an invalid tier is specified."""

    def __init__(self, tier_id: str):
        super().__init__(
            f"Invalid tier: {tier_id}",
            ErrorType.INVALID_TIER,
            {"tier_id": tier_id}
        )

class InvalidMechanismError(ConsensusAPIError):
    """Raised when an invalid mechanism is specified."""

    def __init__(self, mechanism_id: str):
        super().__init__(
            f"Invalid mechanism: {mechanism_id}",
            ErrorType.INVALID_MECHANISM,
            {"mechanism_id": mechanism_id}
        )

class PermissionDeniedError(ConsensusAPIError):
    """Raised when tier doesn't have access to mechanism."""

    def __init__(self, mechanism_id: str, tier_id: str, reason: str):
        super().__init__(
            f"Permission denied: {reason}",
            ErrorType.PERMISSION_DENIED,
            {
                "mechanism_id": mechanism_id,
                "tier_id": tier_id,
                "reason": reason
            }
        )

class ValidationError(ConsensusAPIError):
    """Raised when validation fails."""

    def __init__(self, message: str, errors: list):
        super().__init__(
            message,
            ErrorType.VALIDATION_ERROR,
            {"validation_errors": errors}
        )

class ResourceError(ConsensusAPIError):
    """Raised when resource requirements are not met."""

    def __init__(self, message: str, requirements: Dict):
        super().__init__(
            message,
            ErrorType.RESOURCE_ERROR,
            {"requirements": requirements}
        )

def handle_api_error(error: Exception) -> Dict:
    """
    Handle API errors and return standardized error response.

    Args:
        error: Exception to handle

    Returns:
        Error response dictionary
    """
    if isinstance(error, ConsensusAPIError):
        return error.to_dict()

    # Handle standard Python exceptions
    if isinstance(error, ValueError):
        return {
            "status": "error",
            "error": str(error),
            "error_type": ErrorType.VALIDATION_ERROR.value
        }

    if isinstance(error, PermissionError):
        return {
            "status": "error",
            "error": str(error),
            "error_type": ErrorType.PERMISSION_DENIED.value
        }

    # Generic error
    return {
        "status": "error",
        "error": str(error),
        "error_type": ErrorType.INTERNAL_ERROR.value
    }


# Example usage
if __name__ == "__main__":
    try:
        raise InvalidTierError("INVALID_TIER")
    except ConsensusAPIError as e:
        print(e.to_dict())
