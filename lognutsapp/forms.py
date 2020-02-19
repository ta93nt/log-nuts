from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.storage import default_storage
from django.conf import settings
#モデル
from .models import (
    PersonalLog, FoodImage
)

class LoginForm(AuthenticationForm):
    """ログイン画面のフォーム"""
    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.fields['username'].widget.attrs['class'] = 'form-control'
       self.fields['password'].widget.attrs['class'] = 'form-control'

class SearchForm(forms.Form):
    """検索入力フォーム"""
    store = forms.CharField(label='店舗名', max_length=50, required=False)
    food = forms.CharField(label='食品名', max_length=50, required=False)
    size = forms.CharField(label='サイズ', max_length=50, required=False)
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

class ManualForm(forms.ModelForm):
    """手動入力のフォーム"""
    def __init__(self, *args, **kwargs):
        super(ManualForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    class Meta:
        model = PersonalLog
        fields = (
            'food_name',
            'restaurant',
            'date',
            'size',
            'energie',
            'protein',
            'fat',
            'carbohydrate',
            'salt',
        )
        labels = {
            'user':'ユーザ名',
            'food_name':'食品名',
            'restaurant':'店名',
            'date':'食べた日付',
            'size':'サイズ',
            'energie':'カロリー(kcal)',
            'protein':'タンパク質(g)',
            'fat':'脂質(g)',
            'carbohydrate':'炭水化物(g)',
            'salt':'食塩相当量(g)',
        }

class HistoryForm(forms.Form):
    """履歴入力フォーム"""
    personal_log_id = forms.ChoiceField( widget=forms.CheckboxInput, required=True)
    def __init__(self, *args, **kwargs):
        super(HistoryForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = FoodImage
        fields = '__all__'