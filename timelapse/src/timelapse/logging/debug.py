from sys import stderr


def debug(message: str) -> None:
    print(f"[DEBUG] {message}", file=stderr)