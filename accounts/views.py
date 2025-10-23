from rest_framework import viewsets, status, filters
from .models import Account
from .permissions import IsOwnerOrStaff
from rest_framework.response import Response 
from .serializers import AccountListSerializer, AccountDetailSerializer, AccountCreateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction


# Create your views here.
class AccountViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, IsOwnerOrStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['account_number', 'account_type', 'status']
    odering_fields = ['lastactivitydate', 'account_number']

    #get all accounts 
    queryset = Account.objects.all()

    #get the user object 
    #return the specific user using the defined custom method in the manager
    def get_queryset(self):
        user = self.request.user
        return Account.objects.for_user(user)

    #define list of http actions 
    #list = GET/accounts
    #retrieve = GET/account/<id>
    #create = POST/account
     

    def get_serializer_class(self):
        if self.action == 'list':
            return AccountListSerializer
        elif self.action == 'retrieve':
            return AccountDetailSerializer
        elif self.action == 'create':
            return AccountCreateSerializer
        return AccountDetailSerializer

    def perform_create(self, serializer):
        user = self.request.user
        validated_data = serializer.validated_data
        
        account_type = validated_data.get('account_type', Account.AccountType.CHECKING)
        initial_deposit = validated_data.get('initial_deposit', 0.00)

        with transaction.atomic():
            Account.objects.create_account(
            owner = user,
            account_type = account_type,
            initial_deposit = initial_deposit
            )

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        account = self.get_object()
        return Response({'balance': account.get_current_balance()})


