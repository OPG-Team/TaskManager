import secrets


def create_recovery_code() -> str:
    """Function to generate a secure six-digit recovery code.

    Returns:
        A str, recovery code
    """
    code = ''

    for i in range(6):
        number = secrets.randbelow(10)
        code += str(number)

    return code