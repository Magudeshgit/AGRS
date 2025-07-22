from django import forms
from .models import *
from .models import department as dpt
from django import forms
from django.contrib.auth.forms import UserCreationForm

class CustomSignupForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('parent', 'Parent'),
    )

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'user_type']

CATEGORY_CHOICES = [
    ('Academics', 'Academics'),
    ('Hostel & Facilities', 'Hostel & Facilities'),
    ('Administration', 'Administration'),
    ('Transport', 'Transport'),
    ('Library', 'Library'),
    ('Examination Cell', 'Examination Cell'),
    ('Placement & Training', 'Placement & Training'),
    ('Other', 'Other'),
]

class ComplaintForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=dpt.objects.filter(is_academic=False))
    acad_dept = forms.ModelChoiceField(queryset=dpt.objects.filter(is_academic=True), required=False)
    incident_timestamp = forms.DateTimeField(widget=forms.DateInput(attrs={
        'type': 'datetime-local'
    }))

    class Meta:
        model = Complaint
        fields = ['department', 'title', 'description','incident_timestamp', 'evidence']

class DepartmentResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = '__all__'
        # fields = ['message', 'expected_resolution_date', 'response_evidence']

class ComplaintResponseForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = '__all__'
        # fields = ['department_response', 'response_evidence', 'resolution_deadline']
