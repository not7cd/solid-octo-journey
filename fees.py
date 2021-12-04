from datetime import datetime
from eventsourcing.application import Application
from eventsourcing.domain import Aggregate, event
from decimal import Decimal
from uuid import UUID

from models import Account, Fee


class AccountNotFoundError(Exception):
    pass

class Fees(Application):
    def create_fee(self, name, amount):
        a = Fee(name, amount)
        self.save(a)
        return a.id
    
    def create_account(self, fee_id, open_since):
        a = Account(fee_id, open_since)
        self.save(a)
        return a.id

    def set_amount(self, fee_id, amount: Decimal, since: datetime):
        fee = self.repository.get(fee_id)
        fee.set_amount(amount, since)
        self.save(fee)

    def get_dues(self, fee_id, since: datetime, to: datetime) -> Decimal:
        due = 0
        events = self.repository.event_store.get(fee_id)
        copy = None
        for e in events:
            if isinstance(e, Fee.SetAmount):
                due += copy.get_dues(since, e.since)
                since = e.since
            copy = e.mutate(copy)
        due += copy.get_dues(since, to)
        assert copy == self.repository.get(fee_id)
        return due

    def get_balance(self, acc_id, to: datetime):
        acc = self.repository.get(acc_id)
        due = self.get_dues(acc.fee_id, acc.open_since, to)
        return due - acc.balance

    def credit(self, acc_id, amount):
        acc = self.repository.get(acc_id)
        acc.credit(amount)
        self.save(acc)
