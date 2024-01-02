from sqlalchemy.orm import Session

from health.models.chat_logs import ChatLogs as ChatLogsModel
from health.shared.core_type import DeleteFlag

from .base import CrudBase


class ChatLogs(CrudBase):
    model = ChatLogsModel

    def get_all(self, db: Session) -> list[ChatLogsModel]:
        query = db.query(ChatLogsModel)
        return query.all()


chatlogs_service = ChatLogs()