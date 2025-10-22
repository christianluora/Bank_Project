from django.db import models
from django.db import transaction
from django.contrib.auth import get_user_model
import random

User = get_user_model()

class AccountQuerySet(models.QuerySet):


    def for_user(self, user):

        if user and user.is_authenticated:

            return self.filter(owner = user)
        
        return self.none()
    
class AccountManager(models.Manager):

    def get_queryset(self):

        return AccountQuerySet(self.model, using=self._db)
    
    def for_user(self, user):

        return self.get_queryset().filter(owner = user) if user else self.get_queryset().none()
    
    @transaction.atomic

    def create_account(self, owner, account_type='CHK', initial_deposit = 0.00, status = None):
        
        if not owner:

            raise ValueError('Account must have an owner')
        
        existing = self.get_queryset().filter(owner = owner, account_type = account_type).first()
        
        if existing:

            raise ValueError(f"{owner} already has an account of type {account_type}.")
        
        account_number =  self._generate_unique_account_number()

        status = status or self.model.AccountStatus.PENDING

        account = self.create(

            owner = owner,
            account_number = account_number,
            account_type = account_type,
            status = status
        )

        from .models import Balance
        
        Balance.objects.create(

            account = account,
            current_balance = initial_deposit,
            available_balance = initial_deposit

        )

        return account

    def _generate_unique_account_number(self):

        while True:
            acc_no = str(random.randint(1000000000, 9999999999))
            if not self.filter(account_number=acc_no).exists():
                return acc_no
   
#class TransactionManager(models.Manager):

   # def create_transaction(self, account, amount, transaction_type, description, related_account=None):
        # 1. Validate account and amount
        # 2. Get account balance
        # 3. If debit → check sufficient funds
        # 4. Update balance
        # 5. Save balance
        # 6. Create and return Transaction
