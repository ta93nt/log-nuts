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
    Subject
)

#フォーム
from .forms import (
    LoginForm, SearchForm
)

#ライブラリ
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP #Decimal変換の際に利用


class TopView(generic.TemplateView):
    """Lognutsトップページ"""
    template_name = 'lognuts/top.html' 

class MypageView(generic.TemplateView):
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

class SearchInput(generic.FormView):
    """検索入力のフォームを扱う"""
    form_class = SearchForm
    template_name = 'lognuts/search_input.html'

    def form_invalid(self, form):
        ''' バリデーションに失敗した時 '''
        return super().form_invalid(form)

    def form_valid(self, form, **kwargs):
        context = super().get_context_data(**kwargs)
        s_store = form['store'].value()
        s_food = form['food'].value()
        s_size = form['size'].value()

        mealsout_df = pd.read_csv(settings.MEALSOUT_NUTS_URL)

        print(mealsout_df)

        #context['search_foods'] = search_foods
        #context['confirm_columns'] = ['レストラン名', '食品名', 'サイズ']
        #セッションにデータを保存
        #self.request.session['search_foods'] = search_foods

        return render(self.request, 'lognuts/search_confirm.html', context)