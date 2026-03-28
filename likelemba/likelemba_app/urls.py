from django.urls import path
from .views import dashboard, dashboard_admin, dashboard_membre

urlpatterns = [
    path('', dashboard, name='dashboard'),

    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    path('dashboard/membre/', dashboard_membre, name='dashboard_membre'),
]
