from django.db import models


# Create your models here.


from django import forms

class FilePath(forms.Form):
    file_path = forms.CharField(label='Path to files:', max_length=100)
