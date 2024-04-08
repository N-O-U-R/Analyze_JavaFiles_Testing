from django import forms

class RepoURLForm(forms.Form):
    repo_url = forms.URLField(label='GitHub Repository URL', required=True, widget=forms.URLInput(attrs={'class': 'form-control'}))
