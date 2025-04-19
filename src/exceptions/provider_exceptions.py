"""
Custom exceptions for connection providers.
"""


class ConnectionError(Exception):
    """Base exception for connection-related errors."""
    pass


class ConnectionTimeoutError(ConnectionError):
    """Raised when a connection attempt times out."""
    pass


class ConnectionAuthenticationError(ConnectionError):
    """Raised when authentication fails."""
    pass


class CommandExecutionError(Exception):
    """Base exception for command execution errors."""
    pass


class CommandTimeoutError(CommandExecutionError):
    """Raised when a command execution times out."""
    pass


class CommandPermissionError(CommandExecutionError):
    """Raised when a command fails due to insufficient permissions."""
    pass


class SearchError(Exception):
    """Base exception for file search errors."""
    pass


class SearchPermissionError(SearchError):
    """Raised when a search fails due to insufficient permissions."""
    pass


class SearchPathError(SearchError):
    """Raised when a search path is invalid or inaccessible."""
    pass
