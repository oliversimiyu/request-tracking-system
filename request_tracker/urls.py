"""
URL configuration for request_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views, logout
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

def profile_redirect(request):
    """Redirect from accounts/profile/ to dashboard"""
    return redirect('/dashboard/')

def logout_view(request):
    """Custom logout view that accepts GET requests"""
    logout(request)
    return HttpResponseRedirect('/')

# Create public versions of the Spectacular views
class PublicSpectacularAPIView(SpectacularAPIView):
    permission_classes = [AllowAny]

class PublicSpectacularSwaggerView(SpectacularSwaggerView):
    permission_classes = [AllowAny]

class PublicSpectacularRedocView(SpectacularRedocView):
    permission_classes = [AllowAny]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('service_requests.urls')),
    
    # API URLs
    path('', include('service_requests.api_urls')),
    
    # API Documentation (publicly accessible)
    path('api/schema/', PublicSpectacularAPIView.as_view(), name='schema'),
    path('api-docs/', PublicSpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api-docs/redoc/', PublicSpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', logout_view, name='logout'),
    path('accounts/profile/', profile_redirect, name='profile'),
]
