from django.views import generic
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from . import models

#ミックスイン
from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin
)

#ログイン・ログアウト関連
from django.contrib.auth.views import (
    LoginView, LogoutView
)

#モデル
from .models import (
    Subject, PersonalLog
)

#フォーム
from .forms import (
    LoginForm, SearchForm
)

#ライブラリ
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP #Decimal変換の際に利用


"""
カスタムミックスイン
"""
class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True
    # 今ログインしてるユーザーのpkと、そのユーザー情報ページのpkが同じか、又はスーパーユーザーなら許可
    def test_func(self):
        user = self.request.user
        return user.pk == int(self.kwargs['pk']) or user.is_superuser

class TopView(generic.TemplateView):
    """Lognutsトップページ"""
    template_name = 'lognuts/top.html' 

class MypageView(OnlyYouMixin, generic.TemplateView):
    """Lognutsマイページ"""
    model = User
    template_name = 'lognuts/mypage.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'lognuts/login.html'

class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'lognuts/top.html'

class SearchInput(OnlyYouMixin, generic.FormView):
    """検索入力のフォームからの入力を扱う"""
    form_class = SearchForm
    template_name = 'lognuts/search_input.html'

    def form_invalid(self, form):
        ''' バリデーションに失敗した時 '''
        return super().form_invalid(form)

    def form_valid(self, form, **kwargs):
        context = super().get_context_data(**kwargs)
        #外食食品DBをNaN->''としてデータフレーム化
        mealsout_df = pd.read_csv(settings.MEALSOUT_NUTS_URL).fillna('')

        if form['store'].value():
            #フォームのstoreがある場合、文字列を含むレコード抽出
            mealsout_df = mealsout_df[ 
                mealsout_df['store_name'].str.contains(form['store'].value()) 
            ]
        if form['food'].value():
            #フォームのfoodがある場合、文字列を含むレコード抽出
            mealsout_df = mealsout_df[ 
                mealsout_df['food_name'].str.contains(form['food'].value()) 
            ]
        if form['size'].value():
            #フォームのsizeがある場合、文字列を含むレコード抽出
            mealsout_df = mealsout_df[ 
                mealsout_df['food_size'].str.contains(form['size'].value()) 
            ]
        context['columns'] = ['レストラン名', '食品名', 'サイズ']
        context['search_foods'] = mealsout_df
        return render(self.request, 'lognuts/search_confirm.html', context)

class SearchComplete(OnlyYouMixin, generic.TemplateView):
    template_name = 'lognuts/search_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #外食食品DBをNaN->''としてデータフレーム化
        mealsout_df = pd.read_csv(settings.MEALSOUT_NUTS_URL).fillna('')
        context['columns'] = [
            'データ挿入日時', 'レストラン名', 'メニュー名', 'サイズ', 'カロリー', '炭水化物', 'タンパク質', '脂質', '食塩相当量'
        ]

        if self.kwargs['id']:
            #合致したレコードをpandas seriesとして取り出す
            input_record =  mealsout_df[ (mealsout_df['id'] == self.kwargs['id']) ].iloc[0]
            p_log = PersonalLog()
            print(input_record.protein)
            p_log.user = self.request.user
            p_log.restaurant = input_record.store_name
            p_log.size = input_record.food_size
            p_log.food_name = input_record.food_name
            p_log.energie = input_record.calorie
            p_log.carbohydrate = dec_conv(input_record.carbohydrate)
            p_log.protein = dec_conv(input_record.protein)
            p_log.fat = dec_conv(input_record.fat)
            p_log.salt = dec_conv(input_record.salt)
            context['p_log'] = p_log
            p_log.save()

        return context

#floatを2桁のDecimal型に変換する
def dec_conv(float_num):
    decimal_num = Decimal(float_num).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    return decimal_num
