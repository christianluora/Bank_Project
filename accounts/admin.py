from django.contrib import admin
from .models import Account, Transaction, Balance

# Register your models here.
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Balance)
