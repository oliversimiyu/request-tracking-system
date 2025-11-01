from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ServiceRequest, Department
from .forms import ServiceRequestForm, RequestFilterForm
import json


def home(request):
    """Home page with request submission form"""
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save()
            messages.success(request, f'Your request has been submitted successfully! Request ID: {service_request.id}')
            return redirect('home')
    else:
        form = ServiceRequestForm()
    
    # Only show recent requests to authenticated admin users
    recent_requests = None
    if request.user.is_authenticated:
        recent_requests = ServiceRequest.objects.all()[:5]
    
    return render(request, 'service_requests/home.html', {
        'form': form,
        'recent_requests': recent_requests
    })


@login_required
def request_list(request):
    """View all requests with filtering (admin/IT staff view)"""
    filter_form = RequestFilterForm(request.GET)
    requests_query = ServiceRequest.objects.all()
    
    # Apply filters
    if filter_form.is_valid():
        if filter_form.cleaned_data['status']:
            requests_query = requests_query.filter(status=filter_form.cleaned_data['status'])
        
        if filter_form.cleaned_data['category']:
            requests_query = requests_query.filter(category=filter_form.cleaned_data['category'])
        
        if filter_form.cleaned_data['department']:
            requests_query = requests_query.filter(
                department__icontains=filter_form.cleaned_data['department']
            )
        
        if filter_form.cleaned_data['search']:
            search_term = filter_form.cleaned_data['search']
            requests_query = requests_query.filter(
                Q(requester_name__icontains=search_term) |
                Q(description__icontains=search_term)
            )
    
    # Pagination
    paginator = Paginator(requests_query, 10)  # Show 10 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics for dashboard
    stats = {
        'total': ServiceRequest.objects.count(),
        'pending': ServiceRequest.objects.filter(status='pending').count(),
        'in_progress': ServiceRequest.objects.filter(status='in_progress').count(),
        'resolved': ServiceRequest.objects.filter(status='resolved').count(),
    }
    
    return render(request, 'service_requests/request_list.html', {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'stats': stats
    })


@login_required
def request_detail(request, request_id):
    """View individual request details"""
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    return render(request, 'service_requests/request_detail.html', {
        'service_request': service_request
    })


@login_required
@csrf_exempt
def update_request_status(request, request_id):
    """AJAX endpoint to update request status"""
    if request.method == 'POST':
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status in dict(ServiceRequest.STATUS_CHOICES):
            old_status = service_request.status
            service_request.status = new_status
            
            # Automation: Auto-assign to current user when status changes to in_progress
            if new_status == 'in_progress' and not service_request.assigned_to:
                service_request.assigned_to = request.user
            
            service_request.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Status updated from {old_status} to {new_status}',
                'new_status': new_status
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def request_status_check(request, request_id):
    """Public endpoint to check request status"""
    try:
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        return render(request, 'service_requests/status_check.html', {
            'service_request': service_request
        })
    except:
        messages.error(request, 'Request not found.')
        return redirect('home')


@login_required
def dashboard(request):
    """Admin dashboard with statistics and charts"""
    import json
    
    # Get statistics
    total_requests = ServiceRequest.objects.count()
    pending_requests = ServiceRequest.objects.filter(status='pending').count()
    in_progress_requests = ServiceRequest.objects.filter(status='in_progress').count()
    resolved_requests = ServiceRequest.objects.filter(status='resolved').count()
    
    # Get requests by category (reduced by 50%, minimum 1 if any exist)
    category_stats = {}
    for category_code, category_name in ServiceRequest.CATEGORY_CHOICES:
        actual_count = ServiceRequest.objects.filter(category=category_code).count()
        if actual_count > 0:
            # Reduce by 50% but ensure at least 1 if there were any requests
            reduced_count = max(1, actual_count // 2)
        else:
            reduced_count = 0
        category_stats[category_name] = reduced_count
    
    # Prepare chart data
    category_labels = json.dumps(list(category_stats.keys()))
    category_counts = json.dumps(list(category_stats.values()))
    
    # Recent requests (limit to 3 for dashboard)
    recent_requests = ServiceRequest.objects.all()[:3]
    
    context = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'in_progress_requests': in_progress_requests,
        'resolved_requests': resolved_requests,
        'category_stats': category_stats,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'recent_requests': recent_requests,
    }
    
    return render(request, 'service_requests/dashboard.html', context)


@login_required
def department_list(request):
    """View all departments with management options"""
    departments = Department.objects.all().order_by('name')
    
    # Add request count to each department
    department_data = []
    for dept in departments:
        request_count = ServiceRequest.objects.filter(department=dept.name).count()
        department_data.append({
            'department': dept,
            'request_count': request_count
        })
    
    # Pagination - 10 departments per page
    paginator = Paginator(department_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total_departments': departments.count(),
        'departments_with_requests': Department.objects.filter(
            name__in=ServiceRequest.objects.values_list('department', flat=True).distinct()
        ).count()
    }
    
    return render(request, 'service_requests/department_list.html', {
        'page_obj': page_obj,
        'department_data': page_obj.object_list,  # For backward compatibility
        'stats': stats
    })


@login_required
def department_add(request):
    """Add a new department"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        manager = request.POST.get('manager', '').strip()
        
        if name and code:
            try:
                department = Department.objects.create(
                    name=name,
                    code=code.upper(),
                    manager=manager
                )
                messages.success(request, f'Department "{name}" has been created successfully.')
                return redirect('department_list')
            except Exception as e:
                messages.error(request, f'Error creating department: {str(e)}')
        else:
            messages.error(request, 'Department name and code are required.')
    
    return render(request, 'service_requests/department_form.html', {
        'title': 'Add New Department',
        'action': 'Add'
    })


@login_required
def department_edit(request, department_id):
    """Edit an existing department"""
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        manager = request.POST.get('manager', '').strip()
        
        if name and code:
            try:
                department.name = name
                department.code = code.upper()
                department.manager = manager
                department.save()
                messages.success(request, f'Department "{name}" has been updated successfully.')
                return redirect('department_list')
            except Exception as e:
                messages.error(request, f'Error updating department: {str(e)}')
        else:
            messages.error(request, 'Department name and code are required.')
    
    return render(request, 'service_requests/department_form.html', {
        'department': department,
        'title': f'Edit Department: {department.name}',
        'action': 'Update'
    })


@login_required
def department_delete(request, department_id):
    """Delete a department"""
    department = get_object_or_404(Department, id=department_id)
    
    # Check if department has associated requests
    request_count = ServiceRequest.objects.filter(department=department.name).count()
    
    if request.method == 'POST':
        if request_count > 0:
            messages.warning(request, f'Cannot delete department "{department.name}" because it has {request_count} associated requests.')
        else:
            department_name = department.name
            department.delete()
            messages.success(request, f'Department "{department_name}" has been deleted successfully.')
        return redirect('department_list')
    
    return render(request, 'service_requests/department_confirm_delete.html', {
        'department': department,
        'request_count': request_count
    })


@login_required
def sync_departments_api(request):
    """Sync departments from external API"""
    if request.method == 'POST':
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
                
                if created_count > 0 or updated_count > 0:
                    messages.success(request, f'API Sync completed: {created_count} departments created, {updated_count} updated.')
                else:
                    messages.info(request, 'API Sync completed: No new departments found.')
            else:
                messages.error(request, 'Failed to fetch data from external API.')
                
        except Exception as e:
            messages.error(request, f'Error syncing with API: {str(e)}')
    
    return redirect('department_list')
