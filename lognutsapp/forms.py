from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings

class LoginForm(AuthenticationForm):
    #ログイン画面のフォーム
    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.fields['username'].widget.attrs['class'] = 'form-control'
       self.fields['password'].widget.attrs['class'] = 'form-control'
