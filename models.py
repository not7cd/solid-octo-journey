from decimal import Decimal
from enum import Enum

from eventsourcing.domain import Aggregate, event
from dateutil.relativedelta import relativedelta
from datetime import date, datetime

class NoValue(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

class Period(NoValue):
    DAILY = relativedelta(days=1)
    WEEKLY = relativedelta(weeks=1)
    MONTHLY = relativedelta(months=1)
    QUATERLY = relativedelta(months=3)
    YEARLY = relativedelta(years=1)

class Fee(Aggregate):
    @event("Opened")
    def __init__(self, name: str, amount: Decimal):
        self.name = name
        self.amount = Decimal(amount)
        self.since = None
    
    @event("SetAmount")
    def set_amount(self, amount: Decimal, since: datetime) -> None:
        if  self.since is not None and since < self.since:
            raise SetAmountInPastError
        self.amount = amount
        self.since = since
    
    def get_dues(self, since: datetime, to: datetime) -> Decimal:
        due = 0
        current = since
        while current < to:
            due += self.amount
            current += Period.MONTHLY.value
            
        return due


class Account(Aggregate):
    @event("Opened")
    def __init__(self, fee_id, open_since):
        self.open_since = open_since
        self.fee_id = fee_id
        self.balance = Decimal("0.00")
        self.is_closed = False
        self.last_paid = datetime.now()

    @event("Credited")
    def credit(self, amount: Decimal, when: datetime) -> None:
        self.balance += amount
        self.last_paid = when
    
    @event("Close")
    def close(self) -> None:
        self.is_closed = True



class TransactionError(Exception):
    pass


class AccountClosedError(TransactionError):
    pass


class InsufficientFundsError(TransactionError):
    pass


class SetAmountInPastError(Exception):
    pass