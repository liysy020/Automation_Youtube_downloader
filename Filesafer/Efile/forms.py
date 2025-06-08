from django import forms
from .models import FileDB

class FileDBForm (forms.ModelForm):
    class Meta:
        model = FileDB
        fields = ('file_object',)