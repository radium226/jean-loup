from sys import stderr


def info(message: str, **kwargs) -> None:
    print(f"[INFO] {message}".format(**kwargs), file=stderr)