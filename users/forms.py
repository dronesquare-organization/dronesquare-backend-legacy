from django import forms


class ChangePasswordForm(forms.Form):
    email = forms.CharField(max_length=200)
    current_password = forms.CharField(min_length=8, max_length=200)
    password = forms.CharField(min_length=8, max_length=200)
    password1 = forms.CharField(min_length=8, max_length=200)
