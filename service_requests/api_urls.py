from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ServiceRequestViewSet, DepartmentViewSet,
    submit_request, check_request_status, list_users
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'requests', ServiceRequestViewSet, basename='api-servicerequest')
router.register(r'departments', DepartmentViewSet, basename='api-department')

# API URL patterns
api_urlpatterns = [
    # Router URLs (includes CRUD operations for requests and departments)
    path('', include(router.urls)),
    
    # Public endpoints (no authentication required)
    path('public/submit-request/', submit_request, name='api-submit-request'),
    path('public/request-status/<int:request_id>/', check_request_status, name='api-check-request-status'),
    
    # User management
    path('users/', list_users, name='api-list-users'),
    
    # DRF auth endpoints
    path('auth/', include('rest_framework.urls')),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
]