import random
import string


def random_lower_string(str_length: int = 32) -> str:
    """
    Returns random lowercase string.

    Args:
        str_length: string length

    Returns:
        random lowercase string
    """
    return "".join(random.choices(string.ascii_lowercase, k=str_length))


def random_email() -> str:
    """
    Returns random email.

    Returns:
        random email string
    """
    return f"{random_lower_string()}@{random_lower_string()}.com"
