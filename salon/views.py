# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django_filters import rest_framework as django_filters
from django.db.models import Sum

from .models import (
    Staff,
    ReceiptModel,
    StaffReceipt
)
from .serializers import (
    StaffSerializer,
    StaffReceiptSerializer,
    ReceiptModelSerializer,
    CreateReceiptModelSerializer,
    UpdateReceiptModelSerializer
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
    
    created_at =  django_filters.DateFilter(
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
            
            serializer = UpdateReceiptModelSerializer(receipt, data=request.data, partial=True)
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
    
    created_at = django_filters.DateFromToRangeFilter()
    

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
