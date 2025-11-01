from rest_framework import serializers
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema_field
from .models import ServiceRequest, Department


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    request_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'manager', 'created_at', 'request_count']
        read_only_fields = ['created_at', 'request_count']
    
    @extend_schema_field(serializers.IntegerField)
    def get_request_count(self, obj):
        """Get the number of requests for this department"""
        return ServiceRequest.objects.filter(department=obj.name).count()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (for assigned_to field)"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ServiceRequestSerializer(serializers.ModelSerializer):
    """Serializer for ServiceRequest model"""
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'requester_name', 'requester_email', 'department', 
            'category', 'category_display', 'description', 'status', 
            'status_display', 'assigned_to', 'assigned_to_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status_display', 'category_display', 'assigned_to_details']
    
    def validate_category(self, value):
        """Validate category choice"""
        valid_categories = [choice[0] for choice in ServiceRequest.CATEGORY_CHOICES]
        if value not in valid_categories:
            raise serializers.ValidationError(f"Invalid category. Choose from: {valid_categories}")
        return value
    
    def validate_status(self, value):
        """Validate status choice"""
        valid_statuses = [choice[0] for choice in ServiceRequest.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Choose from: {valid_statuses}")
        return value


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new service requests (public endpoint)"""
    
    class Meta:
        model = ServiceRequest
        fields = ['requester_name', 'requester_email', 'department', 'category', 'description']
    
    def validate_category(self, value):
        """Validate category choice"""
        valid_categories = [choice[0] for choice in ServiceRequest.CATEGORY_CHOICES]
        if value not in valid_categories:
            raise serializers.ValidationError(f"Invalid category. Choose from: {valid_categories}")
        return value


class ServiceRequestStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating service request status"""
    status = serializers.ChoiceField(choices=ServiceRequest.STATUS_CHOICES)
    
    def validate_status(self, value):
        """Validate status choice"""
        valid_statuses = [choice[0] for choice in ServiceRequest.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Choose from: {valid_statuses}")
        return value


class DepartmentStatsSerializer(serializers.Serializer):
    """Serializer for department statistics"""
    total_departments = serializers.IntegerField()
    departments_with_requests = serializers.IntegerField()
    request_distribution = serializers.DictField()


class ServiceRequestStatsSerializer(serializers.Serializer):
    """Serializer for service request statistics"""
    total_requests = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    in_progress_requests = serializers.IntegerField()
    resolved_requests = serializers.IntegerField()
    category_distribution = serializers.DictField()