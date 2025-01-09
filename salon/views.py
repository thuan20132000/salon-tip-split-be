# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions, views
from rest_framework.decorators import action
from django_filters import rest_framework as django_filters
from django.db.models import Sum
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer
from django.db.models.functions import TruncDate


from .models import (
    Staff,
    ReceiptModel,
    StaffReceipt,
    Salon
)
from .serializers import (
    StaffSerializer,
    StaffReceiptSerializer,
    ReceiptModelSerializer,
    CreateReceiptModelSerializer,
    UpdateReceiptModelSerializer,
    SalonSerializer
)


class StaffFilter(django_filters.FilterSet):
    hire_date_from = django_filters.DateFilter(
        field_name="hire_date", lookup_expr='gte')
    hire_date_to = django_filters.DateFilter(
        field_name="hire_date", lookup_expr='lte')

    class Meta:
        model = Staff
        fields = {
            'gender': ['exact'],
            'is_active': ['exact'],
            'hire_date': ['exact', 'gte', 'lte'],
        }


class StaffViewSet(viewsets.ModelViewSet):
    """
    API endpoint for staff management
    """
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    # permission_classes = [IsAuthenticated]
    filterset_class = StaffFilter
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['first_name', 'last_name', 'hire_date', 'salary']


class ReceiptFilter(django_filters.FilterSet):

    created_at = django_filters.DateFromToRangeFilter()

    created_at = django_filters.DateFilter(
        field_name="created_at", lookup_expr='date')

    class Meta:
        model = ReceiptModel
        fields = {
            'payment_status': ['exact'],
            'created_at': ['exact', 'gte', 'lte'],
        }


class ReceiptModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for receipt management
    """
    queryset = ReceiptModel.objects.all()
    serializer_class = ReceiptModelSerializer
    # permission_classes = [IsAuthenticated]
    filterset_class = ReceiptFilter
    search_fields = ['payment_method', 'payment_method_price']
    ordering_fields = ['created_at', 'payment_method_price']

    # Custom action to create receipt

    @action(detail=False, methods=['post'], url_path='create-receipt', url_name='create-receipt')
    def create_receipt(self, request):
        serializer = CreateReceiptModelSerializer(data=request.data)
        # add staff_receipts
        # staff_bills = request.data.get('staff_bills')

        # print("staff_bills:  ", staff_bills)

        if serializer.is_valid():
            serializer.save()

            data = serializer.add_staff_receipts(
                request.data.get('staff_receipts'))
            serializer = ReceiptModelSerializer(data, many=False)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # update receipt
    @action(detail=True, methods=['put'], url_path='update-receipt', url_name='update-receipt')
    def update_receipt(self, request, pk=None):
        try:
            receipt = self.get_object()
            
            serializer = UpdateReceiptModelSerializer(
                receipt, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                data = serializer.update_staff_receipts(
                    request.data.get('staff_receipts'))
                serializer = ReceiptModelSerializer(data, many=False)
                return Response({
                    'status': 'success',
                    'message': 'Receipt updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'status': 'error',
                'message': serializer.errors,
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)


class StaffReceiptFilter(django_filters.FilterSet):

    created_at_range = django_filters.DateFromToRangeFilter(
        field_name="created_at",
        lookup_expr='range',
        
    )
    created_at = django_filters.DateFilter(
        field_name="created_at", lookup_expr='date')
    salon = django_filters.CharFilter(
        field_name='receipt__salon', lookup_expr='exact'
    )

    class Meta:
        model = StaffReceipt
        fields = {
            'staff': ['exact'],
            'receipt': ['exact'],
            'created_at': ['exact', 'gte', 'lte'],
        }


class StaffReceiptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for staff receipt management
    """
    queryset = StaffReceipt.objects.all()
    serializer_class = StaffReceiptSerializer
    # permission_classes = [IsAuthenticated]
    filterset_class = StaffReceiptFilter
    search_fields = ['staff', 'receipt']
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            # Calculate total amount
            totals = queryset.aggregate(
                total_service_amount=Sum('service_amount'),
                total_tip_amount=Sum('tip_amount')
            )

            # Handle None values
            total_amount = totals.get('total_service_amount', 0)
            total_tip = totals.get('total_tip_amount', 0)

            # get total turn
            total_turn = queryset.count()

            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'status': 'success',
                'message': 'Staff receipts retrieved successfully',
                'data': serializer.data,
                'total_amount': total_amount,
                'total_tip': total_tip,
                'total_turn': total_turn,

            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)


class SalonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for salon management
    """
    permission_classes = [IsAuthenticated]
    
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer
    # permission_classes = [IsAuthenticated]
    search_fields = ['name', 'address', 'phone', 'email']
    ordering_fields = ['name', 'address', 'phone', 'email']
    filterset_fields = ['name', 'address', 'phone', 'email']
    ordering = ['name', 'address', 'phone', 'email']
    date_hierarchy = 'created_at'


    # get salon's staffs

    @action(detail=True, methods=['get'], url_path='staffs', url_name='staffs')
    def get_staffs(self, request, pk=None):
        try:
            salon = self.get_object()
            staffs = salon.staff_set.all()
            serializer = StaffSerializer(staffs, many=True)
            return Response({
                'status': 'success',
                'message': 'Staffs retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    # get salon's receipts
    @action(detail=True, methods=['get'], url_path='receipts', url_name='receipts')
    def get_receipts(self, request, pk=None):
        try:
            salon = self.get_object()
            receipts = salon.receiptmodel_set.all()
            receipts = ReceiptFilter(request.GET, queryset=receipts).qs
            serializer = ReceiptModelSerializer(receipts, many=True)
            return Response({
                'status': 'success',
                'message': 'Receipts retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
            
    # get salon's staff receipts
    @action(detail=True, methods=['get'], url_path='staff-receipts', url_name='staff-receipts')
    def get_staff_receipts(self, request, pk=None):
        try:
            salon = self.get_object()
            staff_receipts = StaffReceipt.objects.filter(receipt__salon=salon).all()
            staff_receipts = StaffReceiptFilter(request.GET, queryset=staff_receipts).qs
            
            # Calculate total amount
            totals = staff_receipts.aggregate(
                total_service_amount=Sum('service_amount'),
                total_tip_amount=Sum('tip_amount')
            )
            
            # Handle None values
            total_amount = totals.get('total_service_amount', 0)
            total_tip = totals.get('total_tip_amount', 0)
            
            # get total turn
            total_turn = staff_receipts.count()
            
            serializer = StaffReceiptSerializer(staff_receipts, many=True)
            return Response({
                'status': 'success',
                'message': 'Staff receipts retrieved successfully',
                'data': serializer.data,
                'total_amount': total_amount,
                'total_tip': total_tip,
                'total_turn': total_turn,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
            
    # get salon's staff receipts statictics by date
    @action(detail=True, methods=['get'], url_path='staff-receipts-statistics', url_name='staff-receipts-statistics')
    def get_staff_receipts_statistics(self, request, pk=None):
        try:
            # salon = self.get_object()
            query_set = StaffReceipt.objects.filter(receipt__salon=self.get_object())
            query_set = StaffReceiptFilter(request.GET, queryset=query_set).qs
            query_set = query_set.annotate(
                date=TruncDate('created_at')
            )
            
            grouped_receipt = query_set.values(
                'date',
            )
            
            grouped_receipt = grouped_receipt.annotate(
                total_service_amount=Sum('service_amount'),
                total_tip_amount=Sum('tip_amount'),
            ).order_by('date')
            
            
            
            
           
            return Response({
                'status': 'success',
                'message': 'Staff receipts statistics retrieved successfully',
                'data': grouped_receipt
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
            
    # create salons' receipt
    @action(detail=True, methods=['post'], url_path='create-receipt', url_name='create-receipt')
    def create_receipt(self, request, pk=None):
        try:
            salon = self.get_object()
            serializer = CreateReceiptModelSerializer(data=request.data)
            if serializer.is_valid():
                
                serializer.save(salon=salon)

                data = serializer.add_staff_receipts(
                    request.data.get('staff_receipts'))
                serializer = ReceiptModelSerializer(data, many=False)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    
    # get owner's salons
    @action(detail=False, methods=['get'], url_path='my-salons', url_name='my-salons')
    def get_my_salons(self, request):
        try:
            user = request.user
            salons = user.salon_set.all()
            serializer = SalonSerializer(salons, many=True)
            return Response({
                'status': 'success',
                'message': 'Salons retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
            
    


class RegisterView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )

            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })

            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
