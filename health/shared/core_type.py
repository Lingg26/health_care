import enum


class DeleteFlag(int, enum.Enum):
    IS_DELETED = 1
    IS_NOT_DELETED = 0

class PaymentsFlag(int, enum.Enum):
    CASH = 1
    VNPAY = 2

class StateOrder(int, enum.Enum):
    pass

class UserType(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"