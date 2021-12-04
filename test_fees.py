import unittest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime 

from fees import (
    Fees
)
from models import (
    Fee,
    Period
)


class TestBankAccounts(unittest.TestCase):
    def test(self) -> None:
        app = Fees()

        # Check account not found error.
        # with self.assertRaises(AccountNotFoundError):
        #     app.get_balance(uuid4())

        # Create account #1.
        fee_id = app.create_fee(
            name="normal",
            amount=Decimal(100)
        )

        # Check balance of account #1.
        print("collect fees for one year")
        self.assertEqual(app.get_dues(fee_id, datetime(2020,1,1), datetime(2020,12,30)), Decimal(1200))

        print("collect fees for one year but double amount mid-year")
        app.set_amount(fee_id, Decimal(200), datetime(2020,7,1))
        self.assertEqual(app.get_dues(fee_id, datetime(2020,1,1), datetime(2020,12,30)), Decimal(1800))

        acc_id = app.create_account(fee_id, open_since=datetime(2020,1,1))
        app.credit(acc_id, 1000)
        self.assertEqual(app.get_balance(acc_id, datetime(2020,12,30)), Decimal(800))