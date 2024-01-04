from sqlalchemy.orm import Session

from health.models.chat_logs import ChatLogs as ChatLogsModel, ChatHistory as ChatHistoryModel
from health.shared.core_type import DeleteFlag

from .base import CrudBase


class ChatLogs(CrudBase):
    model = ChatLogsModel

    def get_all(self, db: Session) -> list[ChatLogsModel]:
        query = db.query(ChatLogsModel)
        return query.all()

class ChatHistory(CrudBase):
    model = ChatHistoryModel

    def get_all(self, db: Session) -> list[ChatHistoryModel]:
        query = db.query(ChatHistoryModel)
        return query.all()

    def update_status(self, db, account_id=None, admin_id=None):
        list_filter = []
        list_filter.append(self.model.account_id == account_id)
        if account_id and admin_id:
            list_filter.append(self.model.sent_account_id == account_id)
        elif account_id and not admin_id:
            list_filter.append(self.model.sent_account_id != account_id)
        db.query(self.model).filter(*list_filter).update({"status": "seen"})
        db.commit()


chatlogs_service = ChatLogs()
chat_history_service = ChatHistory()