from  rest_framework import serializers
from .models import Account, Balance

class AccountCreateSerializer(serializers.ModelSerializer):

    initial_deposit = serializers.DecimalField(max_digits=12, decimal_places=2, required = False, default = 0.00)

    class Meta:

        model = Account
        
        fields = ['account_type', 'initial_deposit']

class AccountListSerializer(serializers.ModelSerializer):
    
    current_balance =  serializers.SerializerMethodField()

    class Meta:

        model = Account

        fields = ['account_number', 'account_type', 'status', 'current_balance']

    def get_current_balance(self, obj):

        return obj.get_current_balance()
    
class BalanceSerializer(serializers.ModelSerializer):

    class Meta:

        model = Balance

        fields = ['current_balance', 'available_balance']

class AccountDetailSerializer(serializers.ModelSerializer):

    class Meta:

        balance = BalanceSerializer(read_only = True)

        fields = ['account_number', 'account_type', 'status', 'balance']

