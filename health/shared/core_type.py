import enum


class DeleteFlag(int, enum.Enum):
    IS_DELETED = 1
    IS_NOT_DELETED = 0


class PaymentsFlag(str, enum.Enum):
    CASH = "CASH"
    VNPAY = "VNPAY"

class StatusOrder(str, enum.Enum):
    confirming = "confirming"
    preparing = "preparing"
    delivering = "delivering"
    success = "success"

class UserType(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
