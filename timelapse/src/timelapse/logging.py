from sys import stderr

def info(message: str) -> None:
    print(f"[INFO] {message}", file=stderr)