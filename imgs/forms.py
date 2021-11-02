from django import forms
from django.forms import ClearableFileInput
from .models import Imgs


class ImgUploadForm(forms.ModelForm):
    fileDir = forms.ImageField(label="fileDir")

    class Meta:
        model = Imgs
        fields = ("fileDir", )
