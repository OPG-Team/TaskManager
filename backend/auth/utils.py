from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hashes a given password using a secure hashing algorithm.

    Args:
        password: The plaintext password to be hashed.

    Returns:
        A str, the hashed password.
    """
    return pwd_context.hash(password)


def verify_password(default_password: str, hashed_password: str) -> bool:
    """Verifies password.

    Args:
        default_password (str): Password to check.
        hashed_password (str): Hashed password.

    Returns:
        A bool, if password success verified True, else False.
    """
    return pwd_context.verify(default_password, hashed_password)