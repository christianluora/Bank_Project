from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Account, Balance
from decimal import Decimal

# Create your tests here.

User = get_user_model()

class AccountModelTests(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(username = "JohnMichael", email= "John@example.com", password = "Michael@254" )

    def test_account_creation(self):

        account = Account.objects.create_account(owner = self.user, account_type = Account.AccountType.CHECKING, initial_deposit = 500)

        self.assertEqual(account.owner, self.user)

        self.assertEqual(account.account_type, Account.AccountType.CHECKING)

        self.assertEqual(account.status, Account.AccountStatus.PENDING)

        balance = account.current_balance_record

        self.assertEqual(balance.current_balance, Decimal("500"))

        self.assertEqual(balance.available_balance, Decimal("500"))

class BalanceModelTests(TestCase):
    
    def setUp(self):

        self.user = User.objects.create_user(username = "KenyonJmes", email = "Kenyon@example.com", password = "Kenyon_123")

        self.account = Account.objects.create_account(owner = self.user, account_type = Account.AccountType.CHECKING, initial_deposit = 500)

        self.balance = self.account.current_balance_record

    def test_can_debit(self):

        self.assertTrue(self.balance.can_debit(Decimal("200")))

        self.assertFalse(self.balance.can_debit(Decimal("700")))

        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):

            self.balance.can_debit(Decimal("-10"))

    def test_debit_operation(self):

        initial_balance = self.balance.current_balance

        self.balance.debit(Decimal("50"))

        self.assertEqual(self.balance.current_balance, initial_balance - Decimal("50"))

        self.assertEqual(self.balance.available_balance, initial_balance - Decimal("50"))

    def test_credit_operation(self):

        initial_balance = self.balance.current_balance

        self.balance.credit(Decimal("50"))

        self.assertEqual(self.balance.current_balance, initial_balance + Decimal("50"))

        self.assertEqual(self.balance.available_balance, initial_balance + Decimal("50"))

    def test_calculate_summary(self):

        summary = self.balance.calculate_summary()

        self.assertIn("current_balance", summary)

        self.assertIn("available_balance", summary)
        
        self.assertEqual(summary["current_balance"], self.balance.current_balance)
        