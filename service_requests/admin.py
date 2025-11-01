from django.contrib import admin
from .models import ServiceRequest, Department


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['requester_name', 'department', 'category', 'status', 'created_at']
    list_filter = ['status', 'category', 'department', 'created_at']
    search_fields = ['requester_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    
    def save_model(self, request, obj, form, change):
        # Automation: Automatically update status when marked as resolved
        if obj.status == 'resolved' and change:
            # You can add additional automation logic here
            pass
        super().save_model(request, obj, form, change)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'manager', 'created_at']
    search_fields = ['name', 'code']
