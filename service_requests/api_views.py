from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import ServiceRequest, Department
from .permissions import IsStaffOrReadOnly, IsStaffOnly, IsAuthenticatedForRead
from .serializers import (
    ServiceRequestSerializer, ServiceRequestCreateSerializer, 
    ServiceRequestStatusUpdateSerializer, DepartmentSerializer,
    ServiceRequestStatsSerializer, DepartmentStatsSerializer,
    UserSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List all service requests",
        description="Retrieve a list of all service requests with optional filtering",
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, description='Filter by status'),
            OpenApiParameter('category', OpenApiTypes.STR, description='Filter by category'),
            OpenApiParameter('department', OpenApiTypes.STR, description='Filter by department'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search in requester name and description'),
        ],
        tags=['Service Requests']
    ),
    retrieve=extend_schema(
        summary="Get service request details",
        description="Retrieve detailed information about a specific service request",
        tags=['Service Requests']
    ),
    create=extend_schema(
        summary="Create new service request",
        description="Create a new service request (staff only)",
        tags=['Service Requests']
    ),
    update=extend_schema(
        summary="Update service request",
        description="Update an existing service request (staff only)",
        tags=['Service Requests']
    ),
    partial_update=extend_schema(
        summary="Partially update service request",
        description="Partially update an existing service request (staff only)",
        tags=['Service Requests']
    ),
    destroy=extend_schema(
        summary="Delete service request",
        description="Delete a service request (staff only)",
        tags=['Service Requests']
    ),
)
class ServiceRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing service requests.
    Provides CRUD operations for service requests.
    READ: Authenticated users can view requests
    WRITE: Only staff users can create, update, delete requests
    """
    queryset = ServiceRequest.objects.all().order_by('-created_at')
    serializer_class = ServiceRequestSerializer
    permission_classes = [IsStaffOrReadOnly]
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = self.queryset
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by category
        category_filter = self.request.query_params.get('category')
        if category_filter:
            queryset = queryset.filter(category=category_filter)
        
        # Filter by department
        department_filter = self.request.query_params.get('department')
        if department_filter:
            queryset = queryset.filter(department__icontains=department_filter)
        
        # Search in requester name and description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(requester_name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset
    
    @extend_schema(
        summary="Update service request status",
        description="Update the status of a service request (staff only)",
        request=ServiceRequestStatusUpdateSerializer,
        responses={200: ServiceRequestSerializer},
        tags=['Service Requests']
    )
    @action(detail=True, methods=['post'], url_path='update-status', permission_classes=[IsStaffOnly])
    def update_status(self, request, pk=None):
        """Update the status of a service request (staff only)"""
        service_request = self.get_object()
        serializer = ServiceRequestStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            old_status = service_request.status
            service_request.status = new_status
            
            # Auto-assign to current user when status changes to in_progress
            if new_status == 'in_progress' and not service_request.assigned_to:
                service_request.assigned_to = request.user
            
            service_request.save()
            
            return Response({
                'success': True,
                'message': f'Status updated from {old_status} to {new_status}',
                'data': ServiceRequestSerializer(service_request).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Get service request statistics",
        description="Get statistics about service requests (staff only)",
        responses={200: ServiceRequestStatsSerializer},
        tags=['Service Requests']
    )
    @action(detail=False, methods=['get'], permission_classes=[IsStaffOnly])
    def stats(self, request):
        """Get statistics about service requests (staff only)"""
        total_requests = ServiceRequest.objects.count()
        pending_requests = ServiceRequest.objects.filter(status='pending').count()
        in_progress_requests = ServiceRequest.objects.filter(status='in_progress').count()
        resolved_requests = ServiceRequest.objects.filter(status='resolved').count()
        
        # Category distribution
        category_distribution = {}
        for category_code, category_name in ServiceRequest.CATEGORY_CHOICES:
            count = ServiceRequest.objects.filter(category=category_code).count()
            category_distribution[category_name] = count
        
        stats_data = {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'in_progress_requests': in_progress_requests,
            'resolved_requests': resolved_requests,
            'category_distribution': category_distribution,
        }
        
        return Response(stats_data)


@extend_schema_view(
    list=extend_schema(
        summary="List all departments",
        description="Retrieve a list of all departments with request counts",
        tags=['Departments']
    ),
    retrieve=extend_schema(
        summary="Get department details",
        description="Retrieve detailed information about a specific department",
        tags=['Departments']
    ),
    create=extend_schema(
        summary="Create new department",
        description="Create a new department (staff only)",
        tags=['Departments']
    ),
    update=extend_schema(
        summary="Update department",
        description="Update an existing department (staff only)",
        tags=['Departments']
    ),
    partial_update=extend_schema(
        summary="Partially update department",
        description="Partially update an existing department (staff only)",
        tags=['Departments']
    ),
    destroy=extend_schema(
        summary="Delete department",
        description="Delete a department (staff only)",
        tags=['Departments']
    ),
)
class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing departments.
    READ: Authenticated users can view departments
    WRITE: Only staff users can create, update, delete departments
    """
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    permission_classes = [IsStaffOrReadOnly]
    
    @extend_schema(
        summary="Sync departments from external API",
        description="Sync departments from JSONPlaceholder API (staff only)",
        responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
        tags=['Departments']
    )
    @action(detail=False, methods=['post'], url_path='sync-api', permission_classes=[IsStaffOnly])
    def sync_api(self, request):
        """Sync departments from external API (staff only)"""
        try:
            import requests as req
            response = req.get('https://jsonplaceholder.typicode.com/users', timeout=10)
            
            if response.status_code == 200:
                users = response.json()
                created_count = 0
                updated_count = 0
                
                for user in users:
                    if 'company' in user and 'name' in user['company']:
                        dept_name = user['company']['name']
                        dept_code = dept_name[:10].upper().replace(' ', '')
                        manager = user.get('name', 'Unknown')
                        
                        department, created = Department.objects.get_or_create(
                            name=dept_name,
                            defaults={
                                'code': dept_code,
                                'manager': manager
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            # Update manager if different
                            if department.manager != manager:
                                department.manager = manager
                                department.save()
                                updated_count += 1
                
                return Response({
                    'success': True,
                    'message': f'API Sync completed: {created_count} departments created, {updated_count} updated.'
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to fetch data from external API.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error syncing with API: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Get department statistics",
        description="Get statistics about departments (staff only)",
        responses={200: DepartmentStatsSerializer},
        tags=['Departments']
    )
    @action(detail=False, methods=['get'], permission_classes=[IsStaffOnly])
    def stats(self, request):
        """Get statistics about departments (staff only)"""
        departments = Department.objects.all()
        total_departments = departments.count()
        departments_with_requests = Department.objects.filter(
            name__in=ServiceRequest.objects.values_list('department', flat=True).distinct()
        ).count()
        
        # Request distribution by department
        request_distribution = {}
        for dept in departments:
            request_count = ServiceRequest.objects.filter(department=dept.name).count()
            request_distribution[dept.name] = request_count
        
        stats_data = {
            'total_departments': total_departments,
            'departments_with_requests': departments_with_requests,
            'request_distribution': request_distribution,
        }
        
        return Response(stats_data)


@extend_schema(
    summary="Submit new service request",
    description="Submit a new service request (public endpoint, no authentication required)",
    request=ServiceRequestCreateSerializer,
    responses={201: ServiceRequestSerializer},
    tags=['Service Requests']
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def submit_request(request):
    """
    Public endpoint for submitting new service requests.
    No authentication required.
    """
    serializer = ServiceRequestCreateSerializer(data=request.data)
    if serializer.is_valid():
        service_request = serializer.save()
        return Response(
            ServiceRequestSerializer(service_request).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Check service request status",
    description="Check the status of a service request by ID (public endpoint)",
    responses={200: ServiceRequestSerializer},
    tags=['Service Requests']
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_request_status(request, request_id):
    """
    Public endpoint for checking service request status.
    No authentication required.
    """
    try:
        service_request = ServiceRequest.objects.get(id=request_id)
        return Response(ServiceRequestSerializer(service_request).data)
    except ServiceRequest.DoesNotExist:
        return Response({
            'error': 'Service request not found'
        }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    summary="List users",
    description="Get a list of all users (for assignment purposes - staff only)",
    responses={200: UserSerializer(many=True)},
    tags=['Authentication']
)
@api_view(['GET'])
@permission_classes([IsStaffOnly])
def list_users(request):
    """
    List all users for assignment purposes.
    Staff authentication required.
    """
    users = User.objects.all().order_by('username')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)