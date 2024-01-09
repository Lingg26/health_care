from pydantic import BaseModel


class ChatHistoryResponseSchema(BaseModel):
    message: str
    account_id: int
