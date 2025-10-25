from django.db import models, transaction
#from django.contrib.auth import get_user_model
from .managers import  AccountManager
from django.core.exceptions import ValidationError
from django.conf import settings
from decimal import Decimal

# Create your models here.
class Account(models.Model):

    class AccountStatus(models.TextChoices):
        ACTIVE = 'ACT', 'Active'
        FROZEN = 'FRZ', 'Frozen'
        CLOSED = 'CLO', 'Closed'
        PENDING = 'PEND', 'Pending'

    class AccountType(models.TextChoices):
        CHECKING = 'CHK', 'Checking'
        SAVING = 'SAV', 'Savings',
        LOAN = 'LON', 'Loan',

    account_number = models.CharField(max_length=15, unique=True, null=False)
    account_type =  models.CharField(max_length=3, choices=AccountType.choices, default=AccountType.CHECKING)
    status = models.CharField(max_length=4, choices=AccountStatus.choices, default=AccountStatus.PENDING)
    lastactivitydate = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'bank_accounts'
    )

    objects = AccountManager()

    def __str__(self):

        return  f"{self.owner} - {self.account_number}"

    def get_current_balance(self):
        
        return self.current_balance_record.current_balance

    def is_active(self):
        
        return self.status


class Transaction(models.Model):

    class TransactionType(models.TextChoices):
        DEBIT = 'DBT', 'Debit'
        CREDIT = 'CRT', 'Credit'

    account = models.ForeignKey(
        'accounts.Account', 
        on_delete=models.CASCADE, 
        related_name='primary_transactions'
        )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=3, choices=TransactionType.choices, default=TransactionType.DEBIT)
    description = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now=True)
    related_account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.SET_NULL,
        null = True,
        blank = True,
        related_name='counterparty_transactions'
    )

    def get_transaction_history(self):
        pass
        #create account for person 1 and person 2 
        #n/b: person 1 and 2 mocks the two ends of a transaction
        #get the accounts involved person1 -> person2 for both 1 and 2
        #introduce a function that
        # 1)checks the type of transaction
        # 2)lists the transction type, accounts involved , amount 

    def transfer_funds(self):
        pass

    def reverse_transaction(self):
        pass

class Balance(models.Model):
    account = models.OneToOneField(
        'accounts.Account',
        on_delete=models.PROTECT,
        related_name = 'current_balance_record'
    )
    current_balance =models.DecimalField(max_digits=12, decimal_places=2)
    available_balance = models.DecimalField(max_digits=12, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    MIN_BALANCE = Decimal('100.00')

    def __str__(self):
        return f"{self.account.account_number} - {self.current_balance}"

    def calculate_summary(self):
        
        return {

            "current_balance": self.current_balance,
            "available_balance":self.available_balance,
            "last_updated":self.last_updated 

        }

    def can_debit(self, amount:Decimal) -> bool:
        
        if amount <= 0:
             
            raise ValidationError("Debit amount must be greater than zero")

        if  self.available_balance - amount < self.MIN_BALANCE:

            return False
        
        return True
    
    @transaction.atomic()
    def debit(self, amount:Decimal) -> None:
        
        if not self.can_debit(amount):

            raise ValidationError("Insufficient funds for this debit")
        
        self.current_balance -= amount

        self.available_balance -= amount

        self.save()

    @transaction.atomic()
    def credit(self, amount:Decimal) -> None:
        
        if amount <= 0:

            raise ValidationError("credit amount must be greater than zero")

        self.current_balance += amount

        self.available_balance += amount