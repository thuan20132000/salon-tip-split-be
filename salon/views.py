# Create your views here.
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, User, Permission
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status, permissions, views
from rest_framework.decorators import action
from django_filters import rest_framework as django_filters
from django.db.models import Sum, Count, F, DecimalField
from django.db.models.functions import Cast

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer, StaffSerializer, AddStaffSerializer
from django.db.models.functions import TruncDate
from services.onesignal_service import OneSignalService
from django.contrib.auth import authenticate
from salon.permissions import (
    CanViewReceipts,
    CanViewStaff,
    IsSalonOwner,
    IsSalonStaff,
    CanDeleteStaffReceipt,
    CanViewSalonSalaryReport
)

from .models import (
    Staff,
    ReceiptModel,
    StaffReceipt,
    Salon,
    UserDeviceModel
)
from .serializers import (
    StaffSerializer,
    StaffReceiptSerializer,
    ReceiptModelSerializer,
    CreateReceiptModelSerializer,
    UpdateReceiptModelSerializer,
    SalonSerializer,
    StaffLoginSerializer,
    UserDeviceModelSerializer,
    SalonStaffSerializer
)

from salon.enums import (
    UserRoleEnums,
    PaymentStatusEnums
)

import json


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
    permission_classes = [IsAuthenticated,]
    filterset_class = StaffFilter
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['first_name', 'last_name', 'hire_date', 'salary']


class ReceiptFilter(django_filters.FilterSet):

    created_at_range = django_filters.DateFromToRangeFilter()

    created_at = django_filters.DateFilter(
        field_name="created_at", lookup_expr='date')

    staff = django_filters.CharFilter(
        field_name='staff_receipts__staff', lookup_expr='exact'
    )

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
    filterset_class = ReceiptFilter
    search_fields = ['payment_method', 'payment_method_price']
    ordering_fields = ['created_at', 'payment_method_price']

    # content_type = ContentType.objects.get_for_model(ReceiptModel)
    # post_permission = Permission.objects.filter(content_type=content_type)
    # print([perm.codename for perm in post_permission])

    # permission_classes = [CanViewReceipts]
    # Custom action to create receipt

    def send_create_receipt_notification(self, salon_receipt):

        try:
            # comment:
            staff_receipts = salon_receipt['staff_receipts']

            notification_string = ""
            user_ids = []
            owner_id = salon_receipt['salon']['owner']
            user_ids.append(owner_id)

            for staff_receipt in staff_receipts:
                user_ids.append(staff_receipt['user']['id'])
                notification_string += f"{
                    staff_receipt['user']['first_name']} - "
                notification_string += f"Sale: ${
                    staff_receipt['service_amount']} - "
                notification_string += f"Tip: ${
                    staff_receipt['tip_amount']} \n"

            user_device_ids = UserDeviceModel.objects.filter(
                user__id__in=user_ids,
                device_id__isnull=False
            ).values('device_id')
            device_ids = [item['device_id'] for item in user_device_ids]

            heading = f"New receipt: {salon_receipt["payment_status"]}"
            notification = OneSignalService()

            notification.send_notification_by_ids(
                heading=heading,
                content=notification_string,
                player_ids=device_ids)

        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return None
        # end try
        # )

    @action(detail=False, methods=['post'], url_path='create-receipt', url_name='create-receipt')
    def create_receipt(self, request):

        try:
            # comment:
            serializer = CreateReceiptModelSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()

                data = serializer.add_staff_receipts(
                    request.data.get('staff_receipts'))
                serializer = ReceiptModelSerializer(data, many=False)

                self.send_create_receipt_notification(
                    salon_receipt=serializer.data)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # end try

    # update receipt
    @action(
        detail=True,
        methods=['put'],
        url_path='update-receipt',
        url_name='update-receipt',
        permission_classes=[IsSalonOwner]
    )
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

                self.send_create_receipt_notification(
                    salon_receipt=serializer.data)

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

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsSalonOwner()]
        return super(ReceiptModelViewSet, self).get_permissions()

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [CanDeleteStaffReceipt()]
        return super(StaffReceiptViewSet, self).get_permissions()

    @action(
        detail=True,
        methods=['delete'],
        url_path='delete',
        url_name='delete',
        permission_classes=[CanDeleteStaffReceipt]
    )
    def delete_staff_receipt(self, request, *args, **kwargs):
        print("destroy")
        return super().destroy(self, request, *args, **kwargs)


class SalonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for salon management
    """

    queryset = Salon.objects.all()
    serializer_class = SalonSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'address', 'phone', 'email']
    ordering_fields = ['name', 'address', 'phone', 'email']
    filterset_fields = ['name', 'address', 'phone', 'email']
    ordering = ['name', 'address', 'phone', 'email']
    date_hierarchy = 'created_at'
    # get salon's staffs

    @action(
        detail=True,
        methods=['get'],
        url_path='staffs',
        url_name='staffs',
    )
    def get_staffs(self, request, pk=None):
        try:
            staff = request.user.staff
            staff_salon = staff.salon

            staffs = self.get_object().staff_set.all()
            serializer = SalonStaffSerializer(staffs, many=True)
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
            if salon.owner == request.user:
                receipts = ReceiptModel.objects.filter(
                    salon=salon)
                receipts = ReceiptFilter(request.GET, queryset=receipts).qs
            else:
                receipts = ReceiptModel.objects.filter(
                    salon=salon,
                    staff_receipts__staff=request.user.staff,
                )
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
            if IsAdminUser and salon.owner == request.user:
                staff_receipts = StaffReceipt.objects.filter(
                    receipt__salon=salon,
                    receipt__payment_status=PaymentStatusEnums.PAID.value,
                ).all()
            else:
                staff_receipts = StaffReceipt.objects.filter(
                    receipt__salon=salon,
                    receipt__payment_status=PaymentStatusEnums.PAID.value,
                    staff=request.user.staff,
                )
                print("staff receipts: ", staff_receipts)

            staff_receipts = StaffReceiptFilter(
                request.GET, queryset=staff_receipts).qs

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
    @action(
        detail=True,
        methods=['get'],
        url_path='staff-receipts-statistics',
        url_name='staff-receipts-statistics',
    )
    def get_staff_receipts_statistics(self, request, pk=None):
        try:
            salon = self.get_object()

            if salon.owner == request.user:
                query_set = StaffReceipt.objects.filter(
                    receipt__salon=salon,
                    receipt__payment_status=PaymentStatusEnums.PAID.value,
                ).all()
            else:
                query_set = StaffReceipt.objects.filter(
                    receipt__salon=salon,
                    staff=request.user.staff,
                    receipt__payment_status=PaymentStatusEnums.PAID.value,
                )

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
                total_turn=Count('id'),
            ).order_by('-date')

            summary = query_set.aggregate(
                total_service_amount=Sum('service_amount'),
                total_tip_amount=Sum('tip_amount'),
                total_turn=Count('id')
            )

            return Response({
                'status': 'success',
                'message': 'Staff receipts statistics retrieved successfully',
                'data': grouped_receipt,
                'summary': summary
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    # get staff revenue statistics
    @action(
        detail=True,
        methods=['get'],
        url_path='staff-service-revenue',
        url_name='staff-service-revenue',
        permission_classes=[IsAuthenticated, CanViewSalonSalaryReport]
    )
    def get_staff_service_revenue(self, request, pk=None):
        try:
            salon = self.get_object()

            if salon.owner == request.user:
                query_set = StaffReceipt.objects.filter(
                    receipt__salon=salon,
                    receipt__payment_status=PaymentStatusEnums.PAID.value,
                ).all()
            else:
                query_set = StaffReceipt.objects.filter(
                    receipt__salon=salon,
                    staff=request.user.staff,
                    receipt__payment_status=PaymentStatusEnums.PAID.value,
                )

            query_set = StaffReceiptFilter(request.GET, queryset=query_set).qs
            query_set = query_set.annotate(
                date=TruncDate('created_at')
            )

            grouped_receipt = query_set.values(
                'staff_id',
                'staff__first_name',
                'staff__commission_rate',
                'date',
            )

            grouped_receipt = grouped_receipt.annotate(
                total_service_amount=Sum('service_amount'),
                total_tip_amount=Sum('tip_amount'),
                total_turn=Count('id'),
                service_revenue=Cast(F('total_service_amount') * F('staff__commission_rate'),
                                     DecimalField(max_digits=10, decimal_places=2))
            ).order_by('-date')

            summary = query_set.aggregate(
                total_service_amount=Sum('service_amount'),
                total_tip_amount=Sum('tip_amount'),
                total_turn=Count('id')
            )

            return Response({
                'status': 'success',
                'message': 'Staff revenue statistics retrieved successfully',
                'data': grouped_receipt,
                'summary': summary
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

                # notification = OneSignalService()
                # res = notification.send_to_all(
                #     heading="New Receipt",
                #     content="You have a new receipt"
                # )
                # print("Notification sent:: ",res)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    # get owner's salons

    @action(
        detail=False,
        methods=['get'],
        url_path='my-salons',
        url_name='my-salons',
        permission_classes=[IsAuthenticated]
    )
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

    @action(detail=False, methods=['get'], url_path='notification', url_name='notification')
    def send_notifications(self, request):
        try:
            print("send notification")
            notification = OneSignalService()
            res = notification.send_to_all()
            return Response({
                'status': 'success',
                'message': 'Notification sent successfully',
                'data': res
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    # add salon staff

    @action(
        detail=True,
        methods=['post'],
        url_path='add-staff',
        url_name='add-staff',
        permission_classes=[IsAuthenticated]
    )
    def add_staff(self, request, pk=None):
        try:
            salon = self.get_object()
          
            data = request.data.copy()
          
            data['salon'] = salon.id
            serializer = AddStaffSerializer(data=data)
            if serializer.is_valid():
                staff = serializer.create(data)
                return Response({
                    'status': 'success',
                    'message': 'Staff added successfully',
                    # 'data': AddStaffSerializer(staff).data
                }, status=status.HTTP_201_CREATED)
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

    # soft delete salon staff
    @action(
        detail=True,
        methods=['delete'],
        url_path='delete-staff',
        url_name='delete-staff',
    )
    def delete_staff(self, request, pk=None):
        try:
            staff_id = request.GET.get('staff_id')
            staff = Staff.objects.get(id=staff_id)
            staff.delete()
            return Response({
                'status': 'success',
                'message': 'Staff deleted successfully',
                'data': None
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

                if user:
                    return Response({
                        # 'user': UserSerializer(user).data,
                        'user': UserSerializer(user).data,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
                else:
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

    # staff login
    # @action(detail=False, methods=['post'], url_path='staff-login', url_name='staff-login')
    # def staff_login(self, request):
    #     try:
    #         serializer = StaffLoginSerializer(data=request.GET)
    #         print("staff login:: ",serializer.data)

    #         if serializer.is_valid():
    #             username = request.GET.get('username')
    #             password = request.GET.get('password')
    #             user = authenticate(username=username, password=password)
    #             if user:
    #                 refresh = RefreshToken.for_user(user)
    #                 return Response({
    #                     'user': UserSerializer(user).data,
    #                     'refresh': str(refresh),
    #                     'access': str(refresh.access_token),
    #                 })
    #         return Response(
    #             {'error': 'Invalid credentials'},
    #             status=status.HTTP_401_UNAUTHORIZED
    #         )
    #     except Exception as e:
    #         return Response({
    #             'status': 'error',
    #             'message': str(e),
    #             'data': None
    #         }, status=status.HTTP_400_BAD_REQUEST)


class UserDeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user device management
    """
    queryset = UserDeviceModel.objects.all()
    serializer_class = UserDeviceModelSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['user', 'device_id']
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'message': 'User devices retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['post'],
        url_path='register-device',
    )
    def register_device(self, request):
        try:
            print("register device")

            user = request.user
            print("user: ", user)
            print("request data: ", request.data)
            user_device = user.devices.create(**request.data)

            serializer = UserDeviceModelSerializer(user_device)

            return Response({
                'status': 'success',
                'message': 'Device registered successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['post'],
        url_path='unregister-device',
    )
    def unregister_device(self, request):
        try:
            print("unregister device")
            device_id = request.data.get('device_id')
            user_device = UserDeviceModel.objects.get(device_id=device_id)
            user_device.delete()

            return Response({
                'status': 'success',
                'message': 'Device unregistered successfully',
                'data': None
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['post'],
        url_path='send-notification',
    )
    def send_notification(self, request):
        try:
            notification = OneSignalService()
            device_ids = request.data.get('device_ids')
            print("send notification:: ", type(device_ids))
            # string to list
            device_ids_list = json.loads(device_ids)
            print("device_ids_list: ", device_ids)

            res = notification.send_notification_by_ids(device_ids_list)
            return Response({
                'status': 'success',
                'message': 'Notification sent successfully',
                'data': res
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
