from sys import stderr


def warn(message: str, **kwargs) -> None:
    print(f"[WARN] {message}".format(**kwargs), file=stderr)