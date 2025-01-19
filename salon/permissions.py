# permissions.py
from rest_framework import permissions


class IsStaffUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    hasattr(request.user, 'staff'))


class CanViewReceipts(permissions.BasePermission):
    def has_permission(self, request, view):
        user_permissions = request.user.user_permissions.all()
        print('user_permissions', user_permissions)
        user_permission_codes = [p.codename for p in user_permissions]
        print('user_permission_codes', user_permission_codes)

        return bool(request.user and request.user.has_perm('salon.view_receiptmodel'))


class CanCreateReceipts(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('salon.can_create_receipts'))


class CanEditReceipts(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('salon.can_edit_receipts'))


class CanViewReports(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('salon.can_view_reports'))


class CanViewStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        print('request.user', request.user)
        # return False
        return bool(request.user and request.user.has_perm('salon.view_staff'))


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            hasattr(request.user, 'staff') and
            request.user.staff.role.title == 'Staff'
        )


class IsReceptionist(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            hasattr(request.user, 'staff') and
            request.user.staff.role.title == 'Receptionist'
        )


# class IsSalonOwner(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return bool(
#             request.user and
#             hasattr(request.user, 'staff') and
#             request.user.staff.role.title == 'Salon Owner'
#         )


class IsSalonOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):

        user = request.user

        receipt_salon = obj.salon
        receipt_salon_owner = receipt_salon.owner

        return bool(
            user and
            receipt_salon_owner == user
        )


class CanViewSalonSalaryReport(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        # receipt_salon_owner = obj.receipt.salon.owner
        print("obj", obj.owner_id)

        return (
            bool(user and
                 obj.owner_id == user.id)
        )


class CanDeleteStaffReceipt(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        receipt_salon_owner = obj.receipt.salon.owner

        return bool(
            user and
            receipt_salon_owner == user
        )


class IsSalonStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        user = request.user
        salon = obj
        return False
