from django import forms

class SearchForm(forms.Form):
    a=forms.CharField()
    b=forms.CharField()
