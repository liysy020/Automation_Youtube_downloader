from django import forms

class YouTubeURLForm(forms.Form):
    url = forms.URLField(label="YouTube URL", widget=forms.TextInput(attrs={"placeholder": "Enter a YouTube URL"}))
