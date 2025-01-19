from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

router = routers.DefaultRouter()
router.register(r'staff', views.StaffViewSet)
router.register(r'staff-receipt', views.StaffReceiptViewSet)
router.register(r'receipt', views.ReceiptModelViewSet)
router.register(r'salons', views.SalonViewSet)
router.register(r'user-devices', views.UserDeviceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


]
