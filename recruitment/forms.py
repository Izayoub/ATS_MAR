from django import forms

from accounts.models import Company
from .models import JobOffer



class JobOfferForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = '__all__'
        exclude = ['created_by', 'created_at', 'updated_at']
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'