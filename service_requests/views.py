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
    
    # Get recent requests for display (last 5)
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
    
    # Get requests by category
    category_stats = {}
    for category_code, category_name in ServiceRequest.CATEGORY_CHOICES:
        category_stats[category_name] = ServiceRequest.objects.filter(category=category_code).count()
    
    # Prepare chart data
    category_labels = json.dumps(list(category_stats.keys()))
    category_counts = json.dumps(list(category_stats.values()))
    
    # Recent requests
    recent_requests = ServiceRequest.objects.all()[:10]
    
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
