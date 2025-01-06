from rest_framework import serializers
from .models import (
    Staff,
    StaffReceipt,
    ReceiptModel,
    Salon
)
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class StaffSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = '__all__'

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class StaffReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffReceipt
        fields = '__all__'
        depth = 1
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['staff'] = StaffSerializer(instance.staff).data
        return data


class ReceiptModelSerializer(serializers.ModelSerializer):

    staff_receipts = StaffReceiptSerializer(
        many=True, required=False)

    class Meta:
        model = ReceiptModel
        fields = '__all__'
        depth = 2


class CreateReceiptModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReceiptModel
        fields = '__all__'

    def add_staff_receipts(self, staff_receipts: list):
        
        receipts = []
        for staff_receipt in staff_receipts:

            receipt = StaffReceipt()
            receipt.receipt = self.instance
            receipt.service_amount = staff_receipt.get('service_amount', 0)
            receipt.service_name = staff_receipt.get('service_name', '')
            receipt.staff_id = staff_receipt.get('staff')
            receipt.tip_amount = staff_receipt.get('tip_amount', 0)
            receipt.discount_price = staff_receipt.get('discount_price', 0)
            receipt.discount_percent = staff_receipt.get('discount_percent', 0)
            receipt.save()
            receipts.append(receipt)

        self.instance.staff_receipts.set(receipts)

        return self.instance

class UpdateReceiptModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReceiptModel
        fields = '__all__'

    def update_staff_receipts(self, staff_receipts: list):
        print("staff_receipts: ", staff_receipts)
        for staff_receipt in staff_receipts:
            receipt = StaffReceipt.objects.get(id=staff_receipt.get('id'))
            print("receipt::: ", receipt)
            receipt.service_amount = staff_receipt.get('service_amount', 0)
            receipt.service_name = staff_receipt.get('service_name', '')
            receipt.tip_amount = staff_receipt.get('tip_amount', 0)
            receipt.discount_price = staff_receipt.get('discount_price', 0)
            receipt.discount_percent = staff_receipt.get('discount_percent', 0)
            receipt.save()
        return self.instance
    
    
    
class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = '__all__'
        depth = 1
        



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

