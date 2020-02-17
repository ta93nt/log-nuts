from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings

class LoginForm(AuthenticationForm):
    #ログイン画面のフォーム
    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.fields['username'].widget.attrs['class'] = 'form-control'
       self.fields['password'].widget.attrs['class'] = 'form-control'

class SearchForm(forms.Form):
    store = forms.CharField(label='店舗名', max_length=50, required=False)
    food = forms.CharField(label='食品名', max_length=50, required=False)
    size = forms.CharField(label='サイズ', max_length=50, required=False)