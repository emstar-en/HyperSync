"""
HyperSync Redaction Filters

Concrete filter implementations for various redaction scenarios.
"""

import re
from typing import List, Pattern
from hypersync.agents.redaction.pipeline import RedactionFilter


class PIIFilter(RedactionFilter):
    """Filter for personally identifiable information (PII)."""

    # Common PII patterns
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')

    def apply(self, content: str) -> str:
        """Redact PII from content."""
        redacted = content

        # Redact emails
        matches = self.EMAIL_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.EMAIL_PATTERN.sub('[EMAIL_REDACTED]', redacted)

        # Redact phone numbers
        matches = self.PHONE_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.PHONE_PATTERN.sub('[PHONE_REDACTED]', redacted)

        # Redact SSNs
        matches = self.SSN_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.SSN_PATTERN.sub('[SSN_REDACTED]', redacted)

        # Redact credit cards
        matches = self.CREDIT_CARD_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.CREDIT_CARD_PATTERN.sub('[CARD_REDACTED]', redacted)

        return redacted


class ClassificationFilter(RedactionFilter):
    """Filter for classification markings and confidential data."""

    # Classification patterns
    CONFIDENTIAL_PATTERN = re.compile(
        r'\b(CONFIDENTIAL|CLASSIFIED|SECRET|TOP\s+SECRET)\b',
        re.IGNORECASE
    )
    INTERNAL_ONLY_PATTERN = re.compile(
        r'\b(INTERNAL\s+ONLY|PROPRIETARY|RESTRICTED)\b',
        re.IGNORECASE
    )

    def apply(self, content: str) -> str:
        """Redact classification markings."""
        redacted = content

        # Redact confidential markings
        matches = self.CONFIDENTIAL_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.CONFIDENTIAL_PATTERN.sub('[CLASSIFICATION_REDACTED]', redacted)

        # Redact internal markings
        matches = self.INTERNAL_ONLY_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.INTERNAL_ONLY_PATTERN.sub('[INTERNAL_REDACTED]', redacted)

        return redacted


class SecretsFilter(RedactionFilter):
    """Filter for secrets, keys, and credentials."""

    # Secret patterns
    API_KEY_PATTERN = re.compile(r'\b[A-Za-z0-9]{32,}\b')  # Generic long alphanumeric
    AWS_KEY_PATTERN = re.compile(r'AKIA[0-9A-Z]{16}')
    GITHUB_TOKEN_PATTERN = re.compile(r'ghp_[a-zA-Z0-9]{36}')
    PASSWORD_PATTERN = re.compile(r'password[\s:=]+[\S]+', re.IGNORECASE)
    TOKEN_PATTERN = re.compile(r'token[\s:=]+[\S]+', re.IGNORECASE)

    def apply(self, content: str) -> str:
        """Redact secrets and credentials."""
        redacted = content

        # Redact AWS keys
        matches = self.AWS_KEY_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.AWS_KEY_PATTERN.sub('[AWS_KEY_REDACTED]', redacted)

        # Redact GitHub tokens
        matches = self.GITHUB_TOKEN_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.GITHUB_TOKEN_PATTERN.sub('[GITHUB_TOKEN_REDACTED]', redacted)

        # Redact passwords
        matches = self.PASSWORD_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.PASSWORD_PATTERN.sub('password: [REDACTED]', redacted)

        # Redact tokens
        matches = self.TOKEN_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.TOKEN_PATTERN.sub('token: [REDACTED]', redacted)

        return redacted


class InternalRefsFilter(RedactionFilter):
    """Filter for internal references and identifiers."""

    # Internal reference patterns
    INTERNAL_URL_PATTERN = re.compile(
        r'https?://(?:internal|intranet|corp)\.[a-z0-9.-]+(?:/[^\s]*)?',
        re.IGNORECASE
    )
    EMPLOYEE_ID_PATTERN = re.compile(r'\bEMP-\d{6}\b')
    PROJECT_CODE_PATTERN = re.compile(r'\bPROJ-[A-Z0-9]{4,}\b')

    def apply(self, content: str) -> str:
        """Redact internal references."""
        redacted = content

        # Redact internal URLs
        matches = self.INTERNAL_URL_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.INTERNAL_URL_PATTERN.sub('[INTERNAL_URL_REDACTED]', redacted)

        # Redact employee IDs
        matches = self.EMPLOYEE_ID_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.EMPLOYEE_ID_PATTERN.sub('[EMPLOYEE_ID_REDACTED]', redacted)

        # Redact project codes
        matches = self.PROJECT_CODE_PATTERN.findall(redacted)
        self.items_redacted += len(matches)
        redacted = self.PROJECT_CODE_PATTERN.sub('[PROJECT_CODE_REDACTED]', redacted)

        return redacted


class CustomPatternFilter(RedactionFilter):
    """Filter with custom regex patterns."""

    def __init__(self, name: str, patterns: List[str], replacement: str = '[REDACTED]'):
        """
        Initialize custom pattern filter.

        Args:
            name: Filter name
            patterns: List of regex patterns to match
            replacement: Replacement text
        """
        super().__init__(name)
        self.patterns = [re.compile(p) for p in patterns]
        self.replacement = replacement

    def apply(self, content: str) -> str:
        """Apply custom patterns."""
        redacted = content

        for pattern in self.patterns:
            matches = pattern.findall(redacted)
            self.items_redacted += len(matches)
            redacted = pattern.sub(self.replacement, redacted)

        return redacted


# Filter registry for easy lookup
FILTER_REGISTRY = {
    'pii': PIIFilter,
    'classification': ClassificationFilter,
    'secrets': SecretsFilter,
    'internal-refs': InternalRefsFilter,
    'custom': CustomPatternFilter
}


def get_filter(filter_name: str, **kwargs) -> RedactionFilter:
    """
    Get a filter instance by name.

    Args:
        filter_name: Name of the filter
        **kwargs: Additional arguments for filter initialization

    Returns:
        Filter instance
    """
    filter_class = FILTER_REGISTRY.get(filter_name)
    if not filter_class:
        raise ValueError(f"Unknown filter: {filter_name}")

    return filter_class(filter_name, **kwargs)
