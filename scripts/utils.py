class Col:
    """ANSI colors for terminal log messages."""

    END = "\033[0m"
    INFO = "\033[94m"
    SUCCESS = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"


def log_info(message: str) -> None:
    """Print an informational log message."""

    print(message)


def log_success(message: str) -> None:
    """Print a success log message."""

    print(f"{Col.SUCCESS}{message}{Col.END}")


def log_warning(message: str) -> None:
    """Print a warning log message."""

    print(f"{Col.WARNING}{message}{Col.END}")


def log_error(message: str) -> None:
    """Print an error log message."""

    print(f"{Col.ERROR}{message}{Col.END}")


def log_section(message: str) -> None:
    """Print a compact section heading."""

    print(f"\n{Col.INFO}{message}{Col.END}")


def log_dataset(message: str) -> None:
    """Print one dataset heading."""

    print(f"\n{message}")
