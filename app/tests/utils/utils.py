import random
import string


def random_lower_string(str_length: int = 32) -> str:
    """
    Returns random lowercase string.

    Args:
        str_length: string length, 32 default

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
    return f"{random_lower_string(8)}@{random_lower_string(5)}.com"


def get_settings_env_dict() -> dict:
    """
    Return test settings env dict.

    Returns:
        settings dict
    """
    return {
        "BACKEND_CORS_ORIGINS": (
            "http://localhost,http://localhost:4200,http://localhost:3000"
        ),
        "FIRST_SUPERUSER": "admin",
        "FIRST_SUPERUSER_EMAIL": "admin@example.com",
        "FIRST_SUPERUSER_PASSWORD": "secretpwd",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "SQLALCHEMY_DATABASE_DRIVER": "postgresql+asyncpg",
        "SQLALCHEMY_DATABASE_NAME": "test_db",
        "SQLALCHEMY_DATABASE_USER": "user",
        "SQLALCHEMY_DATABASE_PASSWORD": "secret",
        "SQLALCHEMY_DATABASE_HOST": "host",
        "SQLALCHEMY_DATABASE_PORT": "5432",
    }
