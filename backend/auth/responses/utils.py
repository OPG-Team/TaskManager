from typing import List
from fastapi import HTTPException
from errors import ErrorModel


def convert_to_example(http_exceptions: List[HTTPException]) -> dict:
    """Converts from list of HTTPException to dict response for swagger documentation.

    Args:
        http_exceptions: HTTP exceptions

    Returns:
        A dict of HTTP responses for swagger documentation.
    """
    examples = {}
    for http_exception in http_exceptions:
        examples[http_exception.detail.get("code")] = {
            "summary": http_exception.detail.get("code"),
            "value": {
                "detail": http_exception.detail
            }
        }

    return {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": examples
            }
        }
    }

def merge_responses(base: dict, additional: dict) -> dict:
    result = base.copy()
    for status_code, new_response in additional.items():
        if status_code in result:
            # Объединяем examples для существующего кода состояния
            result[status_code]["content"]["application/json"]["examples"].update(
                new_response["content"]["application/json"]["examples"]
            )
        else:
            # Добавляем новый код состояния
            result[status_code] = new_response
    return result