from pydantic import BaseModel
from typing import Union

class TerminalParams(BaseModel):
    command: str
    description: str

class PythonParams(BaseModel):
    code: str
    description: str

class ToolCall(BaseModel):
    method: str
    params: Union[TerminalParams, PythonParams] 