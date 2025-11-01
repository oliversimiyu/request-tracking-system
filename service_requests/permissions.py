from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff users to create, update, or delete objects.
    Read access is allowed for authenticated users.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed for staff users
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsStaffOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff users to access the view.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff users to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for the owner or staff
        if request.method in permissions.SAFE_METHODS:
            return (request.user and request.user.is_authenticated and 
                   (request.user.is_staff or 
                    (hasattr(obj, 'assigned_to') and obj.assigned_to == request.user)))
        
        # Write permissions are only allowed for staff users
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsAuthenticatedForRead(permissions.BasePermission):
    """
    Custom permission that requires authentication for all operations.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated