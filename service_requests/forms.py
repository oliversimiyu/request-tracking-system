from django import forms
from .models import ServiceRequest, Department
import requests


class ServiceRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load departments from API or database
        self.load_departments()
        
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Special styling for specific fields
        self.fields['description'].widget.attrs.update({
            'rows': 4,
            'placeholder': 'Please describe your issue in detail...'
        })
        
        self.fields['requester_name'].widget.attrs.update({
            'placeholder': 'Enter your full name'
        })
    
    def load_departments(self):
        """Load departments from external API and populate choices"""
        try:
            # First try to get from database
            dept_choices = [(dept.name, dept.name) for dept in Department.objects.all()]
            
            if not dept_choices:
                # If no departments in database, load from external API
                dept_choices = self.fetch_departments_from_api()
            
            # Add a default choice
            dept_choices.insert(0, ('', 'Select Department'))
            self.fields['department'].widget = forms.Select(choices=dept_choices)
            
        except Exception as e:
            # Fallback to static choices if API fails
            static_choices = [
                ('', 'Select Department'),
                ('IT', 'Information Technology'),
                ('HR', 'Human Resources'),
                ('Finance', 'Finance'),
                ('Marketing', 'Marketing'),
                ('Operations', 'Operations'),
                ('Sales', 'Sales'),
            ]
            self.fields['department'].widget = forms.Select(choices=static_choices)
    
    def fetch_departments_from_api(self):
        """Fetch departments from external API"""
        try:
            # Using JSONPlaceholder users as departments (for demonstration)
            response = requests.get('https://jsonplaceholder.typicode.com/users', timeout=5)
            if response.status_code == 200:
                users = response.json()
                dept_choices = []
                
                for user in users[:10]:  # Limit to first 10
                    dept_name = user.get('company', {}).get('name', f"Department {user['id']}")
                    # Store in database for future use
                    Department.objects.get_or_create(
                        name=dept_name,
                        defaults={
                            'code': f"DEPT{user['id']:02d}",
                            'manager': user.get('name', 'Unknown')
                        }
                    )
                    dept_choices.append((dept_name, dept_name))
                
                return dept_choices
        except Exception:
            pass
        
        return []
    
    class Meta:
        model = ServiceRequest
        fields = ['requester_name', 'department', 'category', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class RequestFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Statuses')] + ServiceRequest.STATUS_CHOICES
    CATEGORY_CHOICES = [('', 'All Categories')] + ServiceRequest.CATEGORY_CHOICES
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    department = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Filter by department'
    }))
    search = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Search by name or description'
    }))