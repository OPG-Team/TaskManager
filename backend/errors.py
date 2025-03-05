from typing import Union, Dict
from pydantic import BaseModel


class ErrorModel(BaseModel):
    """
    Error model.

    @var detail: details of error
    """
    detail: Union[str, Dict[str, str]]